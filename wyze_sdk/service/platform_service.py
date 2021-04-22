from typing import Optional, Sequence, Tuple, Union

from .base import ExServiceClient, WyzeResponse


class PlatformServiceClient(ExServiceClient):
    """
    Wyze api client is the wrapper on the requests to https://wyze-platform-service.wyzecam.com
    """

    WYZE_API_URL = "https://wyze-platform-service.wyzecam.com"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
    ):
        super().__init__(token=token, base_url=base_url)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        params: dict = None,
        json: dict = None,
        request_specific_headers: Optional[dict] = None,
    ) -> WyzeResponse:
        # create the time-based nonce
        nonce = self.request_verifier.clock.nonce()

        return super().api_call(
            api_method,
            http_verb=http_verb,
            params=params,
            json=json,
            headers=self._get_headers(request_specific_headers=request_specific_headers, nonce=nonce),
            nonce=nonce,
        )

    def get_variable(self, *, keys: Union[str, Sequence[str]], **kwargs):
        if isinstance(keys, (list, Tuple)):
            kwargs.update({"keys": ",".join(keys)})
        else:
            kwargs.update({"keys": keys})
        kwargs.update({'category': 'app'})
        return self.api_call('/app/v2/platform/get_variable', http_verb="GET", params=kwargs)

    def get_user_profile(self, *, appid: Optional[str] = None, **kwargs):
        request_specific_headers = {}
        if appid is not None:
            request_specific_headers.update({'appid': appid})
        return self.api_call('/app/v2/platform/get_user_profile', http_verb="GET", request_specific_headers=request_specific_headers)
