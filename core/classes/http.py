import urllib.parse

from core.classes.crypt import RosCrypt
from core.classes.exceptions import InvalidMethod, InvalidRequest
from requests import Session


class RosHTTP(RosCrypt):
    acct_ticket: str
    sess_ticket: str
    sess_key: str

    def __init__(self) -> None:
        super().__init__()

    def _request(self, method: str, url: str, data: bytes = ...) -> str | None:
        sess = Session()
        sess.verify = False
        sess.headers = self.http_headers(method, urllib.parse.urlparse(url).path)

        match method:
            case "GET":
                response = sess.get(url)

            case "POST":
                response = sess.post(url, self.encrypt(b"ticket=%b&%b" % (urllib.parse.quote_plus(self.acct_ticket).encode(), data)))

            case _:
                raise InvalidMethod

        if response.status_code == 200:
            try:
                return self.decrypt(response.content).decode()
            except UnicodeDecodeError:
                return response.content
        raise InvalidRequest

    def get(self, url: str) -> str | None:
        return self._request("GET", url)

    def post(self, url: str, data: bytes) -> str | None:
        return self._request("POST", url, data)
