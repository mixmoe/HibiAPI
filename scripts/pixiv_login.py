import hashlib
import sys
from base64 import urlsafe_b64encode
from secrets import token_urlsafe
from typing import Any, Callable, Dict, Optional, TypeVar
from urllib.parse import parse_qs, urlencode

import requests
from loguru import logger as _logger
from PyQt6.QtCore import QUrl
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWebEngineCore import (
    QWebEngineUrlRequestInfo,
    QWebEngineUrlRequestInterceptor,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


app = QApplication(sys.argv)
logger = _logger.opt(colors=True)


class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    code_listener: Optional[Callable[[str], None]] = None

    def __init__(self):
        super().__init__()

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:
        method = info.requestMethod().data().decode()
        url = info.requestUrl().url()

        if (
            self.code_listener
            and "app-api.pixiv.net" in info.requestUrl().host()
            and info.requestUrl().path().endswith("callback")
        ):
            query = parse_qs(info.requestUrl().query())
            code, *_ = query["code"]
            self.code_listener(code)

        logger.debug(f"<y>{method}</y> <u>{url}</u>")


class WebView(QWebEngineView):
    def __init__(self):
        super().__init__()

        self.cookies: Dict[str, str] = {}

        page = self.page()
        profile = page.profile()
        profile.setHttpUserAgent(USER_AGENT)
        page.contentsSize().setHeight(768)
        page.contentsSize().setWidth(432)

        self.interceptor = RequestInterceptor()
        profile.setUrlRequestInterceptor(self.interceptor)
        profile.cookieStore().cookieAdded.connect(self._on_cookie_added)

        self.setFixedHeight(896)
        self.setFixedWidth(414)

        self.start("about:blank")

    def start(self, goto: str):
        self.page().profile().cookieStore().deleteAllCookies()
        self.cookies.clear()
        self.load(QUrl(goto))

    def _on_cookie_added(self, cookie: QNetworkCookie):
        domain = cookie.domain()
        name = cookie.name().data().decode()
        value = cookie.value().data().decode()
        self.cookies[name] = value
        logger.debug(f"<m>Set-Cookie</m> <r>{domain}</r> <g>{name}</g> -> {value!r}")


class ResponseDataWidget(QWidget):
    def __init__(self, webview: WebView):
        super().__init__()
        self.webview = webview

        layout = QVBoxLayout()

        self.cookie_paste = QPlainTextEdit()
        self.cookie_paste.setDisabled(True)
        self.cookie_paste.setPlaceholderText("得到的登录数据将会展示在这里")

        layout.addWidget(self.cookie_paste)

        copy_button = QPushButton()
        copy_button.clicked.connect(self._on_clipboard_copy)
        copy_button.setText("复制上述登录数据到剪贴板")

        layout.addWidget(copy_button)

        self.setLayout(layout)

    def _on_clipboard_copy(self, checked: bool):
        if paste_string := self.cookie_paste.toPlainText().strip():
            app.clipboard().setText(paste_string)


_T = TypeVar("_T", bound="LoginPhrase")


class LoginPhrase:
    @staticmethod
    def s256(data: bytes):
        return urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()

    @classmethod
    def oauth_pkce(cls) -> tuple[str, str]:
        code_verifier = token_urlsafe(32)
        code_challenge = cls.s256(code_verifier.encode())
        return code_verifier, code_challenge

    def __init__(self: _T, url_open_callback: Callable[[str, _T], None]):
        self.code_verifier, self.code_challenge = self.oauth_pkce()

        login_params = {
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
            "client": "pixiv-android",
        }
        login_url = f"{LOGIN_URL}?{urlencode(login_params)}"
        url_open_callback(login_url, self)

    def code_received(self, code: str):
        response = requests.post(
            AUTH_TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "include_policy": "true",
                "redirect_uri": REDIRECT_URI,
            },
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        data: Dict[str, Any] = response.json()

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        expires_in = data.get("expires_in", 0)

        return_text = ""
        return_text += f"access_token: {access_token}\n"
        return_text += f"refresh_token: {refresh_token}\n"
        return_text += f"expires_in: {expires_in}\n"

        return return_text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixiv login helper")

        layout = QHBoxLayout()

        self.webview = WebView()
        layout.addWidget(self.webview)

        self.form = ResponseDataWidget(self.webview)
        layout.addWidget(self.form)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == "__main__":
    window = MainWindow()
    window.show()

    def url_open_callback(url: str, login_phrase: LoginPhrase):
        def code_listener(code: str):
            response = login_phrase.code_received(code)
            window.form.cookie_paste.setPlainText(response)

        window.webview.interceptor.code_listener = code_listener
        window.webview.start(url)

    LoginPhrase(url_open_callback)

    exit(app.exec())
