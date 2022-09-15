import urllib.parse

from core.classes.crypt import RosCrypt
from core.classes.exceptions import InvalidMethodError, InvalidRequestError
from requests import Session


class RosHTTP(RosCrypt):
    def __init__(self) -> None:
        super().__init__()

    def _request(self, method: str, url: str, data: bytes = ...) -> str | None:
        sess = Session()
        sess.verify = False
        sess.headers = self.http_headers(method, urllib.parse.urlparse(url).path)

        if method == 'GET':
            response = sess.get(url)
        elif method == 'POST':
            response = sess.post(url, self.encrypt(b'ticket=%b&%b' % (urllib.parse.quote_plus(self.acct_ticket).encode(), data)))
        else:
            raise InvalidMethodError

        if response.status_code == 200:
            try:
                return self.decrypt(response.content).decode()
            except UnicodeDecodeError:
                return response.content
        raise InvalidRequestError

    def get(self, url: str) -> str | None:
        return self._request('GET', url)

    def post(self, url: str, data: bytes) -> str | None:
        return self._request('POST', url, data)
