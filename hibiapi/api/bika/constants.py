from hibiapi.utils.config import APIConfig


class BikaConstants:
    DIGEST_KEY = b"~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
    API_KEY = b"C69BAF41DA5ABD1FFEDC6D2FEA56B"
    DEFAULT_HEADERS = {
        "API-Key": API_KEY,
        "App-Channel": "2",
        "App-Version": "2.2.1.2.3.3",
        "App-Build-Version": "44",
        "App-UUID": "defaultUuid",
        "Accept": "application/vnd.picacomic.com.v1+json",
        "App-Platform": "android",
        "User-Agent": "okhttp/3.8.1",
        "Content-Type": "application/json; charset=UTF-8",
    }
    API_HOST = "https://picaapi.picacomic.com/"
    CONFIG = APIConfig("bika")
