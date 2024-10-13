from email.message import Message
from http import client
from typing import Final, Callable, Self
from urllib.error import HTTPError

from pydantic import BaseModel

from . import HttpRequest


####################################################################################################
# httpレスポンスに関するもの
class HttpResponse:
    """httpレスポンスを表すクラス
    """
    http_request: Final[HttpRequest]
    headers: Final[Message]
    read: Final[Callable[[], bytes]]
    __enter__: Final[Callable[[], any]]
    __exit__: Final[Callable[[any, any, any], any]]
    status_code: int

    def __init__(
            self, http_request: HttpRequest, headers: Message, read: Callable[[], bytes],
            __enter__: Callable[[], any],
            __exit__: Callable[[any, any, any], any],
            status_code: int,
    ):
        self.http_request = http_request
        self.headers = headers
        self.read = read
        self.status_code = status_code
        self.__enter__ = __enter__
        self.__exit__ = __exit__

    @staticmethod
    def from_response(request: HttpRequest, response: client.HTTPResponse):
        return HttpResponse(
            request, response.headers, lambda: response.read(), lambda: response.__enter__(),
            lambda exc_type, exc_val, exc_tb: response.__exit__(exc_type, exc_val, exc_tb),
            response.status
        )

    @staticmethod
    def from_http_error(request: HttpRequest, error: HTTPError):
        return HttpResponse(
            request, error.headers, lambda: error.read(), lambda: error.__enter__(),
            lambda exc_type, exc_val, exc_tb: error.__exit__(exc_type, exc_val, exc_tb),
            error.code
        )

    def read(self) -> bytes:
        return self.read()

    def json_model[T: BaseModel](self, model: type[T]) -> T:
        """responseのbodyをjsonオブジェクトに変換する
        :return: jsonを表すディクショナリ
        """
        return model.model_validate_json(self.body())

    def body(self):
        encoding = self.headers.get_content_charset('utf-8')
        return self.read().decode(encoding)

    def __enter__(self):
        self.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)

    def on_status_code(self, expect: int, fn: Callable[[Self], any]) -> Self:
        if self.status_code == expect:
            fn(self)
        return self
