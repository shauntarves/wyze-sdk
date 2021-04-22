from datetime import datetime
import logging
import urllib
from typing import Dict, Optional, Union

from wyze_sdk.signature import RequestVerifier
import wyze_sdk.errors as e
from wyze_sdk.models import datetime_to_epoch

from .base import BaseServiceClient, WyzeResponse


class FordResponse(WyzeResponse):

    def validate(self) -> WyzeResponse:
        """Check if the response from the Ford service was successful.
        Returns:
            (WyzeResponse)
                This method returns it's own object. e.g. 'self'
        Raises:
            WyzeApiError: The request to the Wyze API failed.
        """
        if self._logger.level <= logging.DEBUG:
            body = self.data if isinstance(self.data, dict) else "(binary)"
            self._logger.debug(
                "Received the following response - "
                f"status: {self.status_code}\n"
                f"headers: {dict(self.headers)}\n"
                f"body: {body}"
            )
        if (
            self.status_code == 200
            and self.data
            and (isinstance(self.data, bytes) or int(self.data.get("code", 1)) == 1)
        ):
            return self
        msg = "The request to the Wyze Ford API failed."
        raise e.WyzeApiError(message=msg, response=self)


class FordServiceClient(BaseServiceClient):
    """
    Ford service client is the wrapper on the requests to https://yd-saas-toc.wyzecam.com
    """

    WYZE_API_URL = "https://yd-saas-toc.wyzecam.com"
    WYZE_FORD_APP_KEY = "275965684684dbdaf29a0ed9"
    WYZE_FORD_APP_SECRET = "4deekof1ba311c5c33a9cb8e12787e8c"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
    ):
        super().__init__(token=token, base_url=base_url, request_verifier=RequestVerifier(signing_secret=None))

    def _get_headers(
        self,
        *,
        request_specific_headers: Optional[dict] = None,
    ) -> Dict[str, str]:
        if request_specific_headers is None:
            request_specific_headers = {}

        request_specific_headers.update({
            'appVer': f"And-{self.app_version}",
            "language": "en_US",
            "Keep-Alive": "timeout=120",
        })

        return super()._get_headers(headers=None, has_json=False, request_specific_headers=request_specific_headers)

    def generate_dynamic_signature(self, *, path: str, method: str, body: Union[str, bytes]):
        """Generates a dynamic signature"""
        if body is None:
            body = ""
        if isinstance(body, bytes):
            body = body.decode("utf-8")

        # we must URL-escape this random string
        format_req = urllib.parse.quote_plus(f"{method}{path}{body}{self.WYZE_FORD_APP_SECRET}")
        return self.request_verifier.md5_string(format_req)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "GET",
        params: dict = None,
        json: dict = None,
        request_specific_headers: Optional[dict] = None,
    ) -> WyzeResponse:
        nonce = self.request_verifier.clock.nonce()

        if http_verb == "POST":
            if json is None:
                json = {}
            # this must be done here so that it will be included in the signing
            json.update({
                "access_token": self.token,
                "key": self.WYZE_FORD_APP_KEY,
                "timestamp": str(nonce),
            })
            json.update({
                "sign": self.generate_dynamic_signature(path=api_method, method="post", body=super().get_sorted_params(sorted(json.items()))),
            })
        elif http_verb == "GET":
            if params is None:
                params = {}
            # this must be done here so that it will be included in the signing
            params.update({
                "access_token": self.token,
                "key": self.WYZE_FORD_APP_KEY,
                "timestamp": str(nonce),
            })
            params.update({
                "sign": self.generate_dynamic_signature(path=api_method, method="get", body=super().get_sorted_params(sorted(params.items()))),
            })

        return super().api_call(
            self.base_url + api_method,
            http_verb=http_verb,
            params=params,
            json=json,
            headers=self._get_headers(request_specific_headers=request_specific_headers),
        )

    def get_user_device(self, limit: int = 25, offset: int = 0, **kwargs) -> FordResponse:
        """
        See: com.yunding.ford.manager.NetDeviceManager.getUserDevice
        """
        kwargs.update({'limit': str(limit), "offset": str(offset), "detail": "1"})
        return self.api_call('/openapi/v1/device', params=kwargs)

    def get_lock_info(self, *, uuid: str, **kwargs) -> FordResponse:
        """
        See: com.yunding.ford.manager.NetLockManager.getLockInfo
        """
        kwargs.update({'uuid': uuid})
        return self.api_call('/openapi/lock/v1/info', params=kwargs)

    def get_gateway_info(self, *, uuid: str, **kwargs) -> FordResponse:
        kwargs.update({'uuid': uuid})
        return self.api_call('/openapi/gateway/v1/info', params=kwargs)

    def get_crypt_secret(self, **kwargs) -> FordResponse:
        """
        See: com.yunding.ford.manager.NetLockManager.getCryptSecret
        """
        return self.api_call('/openapi/v1/crypt_secret', params=kwargs)

    def get_family_record_count(self, *, uuid: str, begin: datetime, end: Optional[datetime] = None, **kwargs) -> FordResponse:
        """
        See: com.yunding.ford.manager.NetLockManager.getFamilyRecordCount
        """
        kwargs.update({'uuid': uuid, 'begin': str(datetime_to_epoch(begin))})
        if end is not None:
            kwargs.update({'end': datetime_to_epoch(end)})
        return self.api_call('/openapi/v1/safety/count', params=kwargs)

    def get_family_record(self, *, uuid: str, begin: datetime, end: Optional[datetime] = None, offset: int = 0, limit: int = 20, **kwargs) -> FordResponse:
        """
        Gets a reverse chronological list of lock event records. `begin` is the earliest time.

        See: com.yunding.ford.manager.NetLockManager.getFamilyRecord
        """
        kwargs.update({'uuid': uuid, 'begin': str(datetime_to_epoch(begin)), 'offset': str(offset), 'limit': str(limit)})
        if end is not None:
            kwargs.update({'end': str(datetime_to_epoch(end))})
        return self.api_call('/openapi/v1/safety/family_record', params=kwargs)

    def remote_control_lock(self, *, uuid: str, action: str, **kwargs) -> FordResponse:
        """
        See: com.yunding.ford.manager.NetLockManager.remoteControlLock
        """
        kwargs.update({'uuid': uuid, 'action': action})
        return self.api_call('/openapi/lock/v1/control', http_verb="POST", json=kwargs)
