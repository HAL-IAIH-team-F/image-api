from urllib import request
from urllib.error import HTTPError

from . import HttpRequest
from . import HttpResponse


####################################################################################################
# httpアクセスに関するもの
class HttpClient:
    """httpを使用したアクセスを行います
    """

    @staticmethod
    def fetch(http_request: HttpRequest) -> HttpResponse:
        """requestを使用してhttpアクセスを行います
        :param http_request: アクセスに使用する情報
        :return: リクエストの結果 with構文を使用する必要があります
        """
        try:
            response = request.urlopen(http_request.get_request())
            return HttpResponse.from_response(http_request, response)
        except HTTPError as e:
            return HttpResponse.from_http_error(http_request, e)
