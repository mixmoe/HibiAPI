import zlib
from io import BytesIO

from PIL import Image

from hibiapi.utils.decorators import ToAsync
from hibiapi.utils.exceptions import ClientSideException, ServerSideException

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def decompress_headerless(data: bytes):
    d = zlib.decompressobj(wbits=-15)
    result = d.decompress(data)
    result += d.flush()

    # do all the checks we can?
    assert len(d.unconsumed_tail) == 0
    assert len(d.unused_data) == 0

    return result


def compress(data: bytes):
    c = zlib.compressobj(level=9, wbits=-15)
    result = c.compress(data)
    result += c.flush(zlib.Z_FULL_FLUSH)
    return result


def verbatim(data: bytes, last: bool = False):
    result = b"\x01" if last else b"\x00"
    result += len(data).to_bytes(2, "little")
    result += (len(data) ^ 0xFFFF).to_bytes(2, "little")
    return result + data


def compress_to_size(data: bytes, size: int):
    for i in range(1, len(data)):
        attempt = verbatim(b"") + compress(data[:-i]) + verbatim(data[-i:])
        remainder = size - len(attempt)
        if remainder % 5 == 0:
            break
    else:
        return b""
    if remainder < 0:
        return b""
    attempt += verbatim(b"") * (remainder // 5)
    assert (len(attempt)) == size
    assert decompress_headerless(attempt) == data
    return attempt


def apply_filter(im: Image.Image):
    width, _ = im.size
    imgbytes = im.tobytes()
    filtered = b""
    stride = width * 3
    for i in range(0, len(imgbytes), stride):
        filtered += b"\x00" + imgbytes[i : i + stride]
    return filtered


def check_filter_bytes(data: bytes, width: int):
    stride = width * 3 + 1
    for i in range(0, len(data), stride):
        if data[i] != 0:
            print(data[i - 10 : i + 10].hex())
            raise ServerSideException(f"BAD FILTER AT OFFSET {i}")
    return


def adler32(msg: bytes, init: int = 1):
    a = init & 0xFFFF
    b = init >> 16
    for c in msg:
        a = (a + c) % 65521
        b = (b + a) % 65521
    return a | (b << 16)


def write_png_chunk(stream: BytesIO, name: bytes, body: bytes):
    stream.write(len(body).to_bytes(4, "big"))
    stream.write(name)
    stream.write(body)
    crc = zlib.crc32(body, zlib.crc32(name))
    stream.write(crc.to_bytes(4, "big"))


@ToAsync
def generate(apple: bytes, general: bytes) -> bytes:
    apple_image = Image.open(BytesIO(apple)).convert("RGB")
    width, height = apple_image.size
    general_image = Image.open(BytesIO(general)).convert("RGB")
    width2, height2 = general_image.size

    if width != width2 or height != height2:
        raise ClientSideException("Input images must be the same size!")

    target_size = (width * 3) + 1

    message_1 = apply_filter(apple_image)
    message_2 = apply_filter(general_image)

    a = b""
    a += verbatim(bytes(target_size))  # row of empty pixels
    a += verbatim(bytes(target_size))[:5]  # start the zlib desync

    b: bytes = b""

    ypos = 0

    while ypos < height:
        for pieceheight in range(2, height - ypos):  # TODO: binary search
            start = target_size * ypos
            end = target_size * (ypos + pieceheight)
            acomp = compress_to_size(message_1[start:end], target_size - 5)
            if not acomp:
                break
            bcomp = compress_to_size(message_2[start:end], target_size - 5)
            if not bcomp:
                break
        else:
            pieceheight += 1  # type:ignore
        pieceheight -= 1

        start = target_size * ypos
        end = target_size * (ypos + pieceheight)
        acomp = compress_to_size(message_1[start:end], target_size - 5)
        bcomp = compress_to_size(message_2[start:end], target_size - 5)

        b += acomp
        b += verbatim(bytes(target_size))[:5]
        b += bcomp
        b += verbatim(bytes(target_size))[:5]

        ypos += pieceheight + 1

    # re-sync the zlib streams
    b = b[:-5]
    b += verbatim(b"")
    b += verbatim(b"", last=True)

    interp_1 = decompress_headerless(a) + decompress_headerless(b)
    interp_2 = decompress_headerless(a + b)

    check_filter_bytes(interp_1, width)
    check_filter_bytes(interp_2, width)

    a = b"\x78\xda" + a
    b = b + adler32(interp_2).to_bytes(4, "big")

    height = ypos + 1
    output_data = BytesIO()

    output_data.write(PNG_MAGIC)

    ihdr = b""
    ihdr += width.to_bytes(4, "big")
    ihdr += height.to_bytes(4, "big")
    ihdr += (8).to_bytes(1, "big")  # bitdepth
    ihdr += (2).to_bytes(1, "big")  # true colour
    ihdr += (0).to_bytes(1, "big")  # compression method
    ihdr += (0).to_bytes(1, "big")  # filter method
    ihdr += (0).to_bytes(1, "big")  # interlace method

    write_png_chunk(output_data, b"IHDR", ihdr)

    idat_chunks = BytesIO()
    write_png_chunk(idat_chunks, b"IDAT", a)
    first_offset = idat_chunks.tell()
    write_png_chunk(idat_chunks, b"IDAT", b)

    n = 2
    idot_size = 24 + 8 * n

    idot = b""
    idot += n.to_bytes(4, "big")  # height divisor
    idot += (0).to_bytes(4, "big")  # unknown
    idot += (1).to_bytes(4, "big")  # divided height
    idot += (idot_size).to_bytes(4, "big")  # unknown
    idot += (1).to_bytes(4, "big")  # first height
    idot += (height - 1).to_bytes(4, "big")  # second height
    idot += (idot_size + first_offset).to_bytes(4, "big")  # idat restart offset

    write_png_chunk(output_data, b"iDOT", idot)

    idat_chunks.seek(0)
    output_data.write(idat_chunks.read())

    write_png_chunk(output_data, b"IEND", b"")

    return output_data.getvalue()
