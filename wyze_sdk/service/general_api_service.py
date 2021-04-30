from __future__ import annotations

from typing import Dict, Optional

from wyze_sdk.signature import RequestVerifier

from .base import BaseServiceClient, WyzeResponse


class GeneralApiServiceClient(BaseServiceClient):
    """
    Wyze api client is the wrapper on the requests to https://wyze-general-api.wyzecam.com
    """
    WYZE_API_KEY = ""
    WYZE_API_URL = "https://wyze-general-api.wyzecam.com"
    WYZE_SDK_TYPE = "100"
    WYZE_SDK_VERSION = "1.2.3"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
        sdk_version: Optional[str] = WYZE_SDK_VERSION,
        sdk_type: Optional[str] = WYZE_SDK_TYPE,
        user_id: Optional[str] = None,
    ):
        super().__init__(token=token, base_url=base_url, request_verifier=RequestVerifier(signing_secret=None))
        self.api_key = GeneralApiServiceClient.WYZE_API_KEY
        self.sdk_version = sdk_version
        self.sdk_type = sdk_type
        self.user_id = user_id

    def _get_headers(
        self,
        *,
        request_specific_headers: Optional[dict] = None,
        nonce: Optional[int] = None,
    ) -> Dict[str, str]:
        if request_specific_headers is None:
            request_specific_headers = {}

        request_specific_headers.update({
            'wyzesdktype': self.sdk_type,
            'wyzesdkversion': self.sdk_version,
        })

        return super()._get_headers(headers=None, has_json=True, request_specific_headers=request_specific_headers)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        json: dict = {},
        request_specific_headers: Optional[dict] = None,
    ) -> WyzeResponse:
        json['apiKey'] = self.api_key
        json['appId'] = self.app_id
        json['appVersion'] = self.app_version
        json['deviceId'] = self.phone_id

        return super().api_call(
            api_method,
            http_verb=http_verb,
            params=None,
            json=json,
            headers=self._get_headers(request_specific_headers=request_specific_headers),
        )

    def post_user_event(self, *, pid: str, event_id: str, event_type: int, **kwargs):
        nonce = self.request_verifier.clock.nonce()
        kwargs.update({
            'eventId': event_id,
            'eventType': event_type,
            'logSdk': 100,
            'logTime': nonce,
            'nonce': str(nonce),
            'osInfo': 'Android',
            'osVersion': '9',
            'pid': pid,
            'uid': self.user_id,
        })

        return self.api_call('/v1/user/event', json=kwargs)
