from fastapi import File, Response

from hibiapi.api.apple_mask import generate
from hibiapi.utils.routing import SlashRouter

router = SlashRouter(tags=["AppleMask"])


@router.post("/", summary="苹果专属图片生成器")
async def generate_image(apple: bytes = File(...), general: bytes = File(...)):
    """
    ## Name: `generate_image`

    > 生成苹果专属的图片, 其他系统看不到

    仅为实验性功能! 可能在任何时候删除或者失效!

    ---

    ### Optional:
    - ***bytes*** `apple` = `File(...)`
        - Description: 苹果看到的
    - ***bytes*** `general` = `File(...)`
        - Description: 其他系统看到的
    """
    result = await generate(apple, general)
    return Response(result, media_type="image/png")
