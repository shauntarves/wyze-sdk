from __future__ import annotations

from typing import Dict, Optional

from mintotp import totp

from wyze_sdk import version
from wyze_sdk.signature import RequestVerifier

from .base import ExServiceClient, WyzeResponse


class AuthServiceClient(ExServiceClient):
    """
    Auth service client is the wrapper on the requests to https://auth-prod.api.wyze.com'
    """
    WYZE_API_KEY = 'RckMFKbsds5p6QY3COEXc2ABwNTYY0q18ziEiSEm'
    WYZE_API_URL = "https://auth-prod.api.wyze.com"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
        api_key: str = WYZE_API_KEY,
    ):
        super().__init__(token=token, base_url=base_url, request_verifier=RequestVerifier(signing_secret=None))
        self.api_key = api_key

    def _get_headers(
        self,
        *,
        request_specific_headers: Optional[dict] = None,
        nonce: Optional[int] = None,
    ) -> Dict[str, str]:
        if request_specific_headers is None:
            request_specific_headers = {}

        request_specific_headers.update({
            'x-api-key': self.api_key,
        })

        return super()._get_headers(request_specific_headers=request_specific_headers)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        params: dict = None,
        json: dict = None,
        request_specific_headers: Optional[dict] = None,
        nonce: Optional[int] = None,
    ) -> WyzeResponse:
        if nonce is None:
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

    def user_login(
        self,
        *,
        email: str,
        password: str,
        key_id: Optional[str] = None,
        api_key: Optional[str] = None,
        totp_key: Optional[str] = None,
        **kwargs,
    ) -> WyzeResponse:
        nonce = self.request_verifier.clock.nonce()
        password = self.request_verifier.md5_string(
            self.request_verifier.md5_string(self.request_verifier.md5_string(password))
        )
        kwargs.update({"nonce": str(nonce), "email": email, "password": password})
        api_headers = {
            "keyid": key_id,
            "apikey": api_key,
            "user-agent": f"wyze-sdk-{version.__version__}",
        }

        response = self.api_call(
            '/api/user/login', json=kwargs, request_specific_headers=api_headers, nonce=nonce
        )

        if response["access_token"]:
            return response

        if 'TotpVerificationCode' in response.get('mfa_options'):
            # TOTP 2FA
            mfa_type = 'TotpVerificationCode'
            if totp_key:
                verification_code = totp(totp_key)
            else:
                verification_code = input('Enter Wyze 2FA Verification Code: ')
            verification_id = response['mfa_details']['totp_apps'][0]['app_id']
        else:
            # SMS 2FA
            mfa_type = 'PrimaryPhone'
            params = {
                'mfaPhoneType': 'Primary',
                'sessionId': response['sms_session_id'],
                'userId': response['user_id']
            }
            payload = {}
            response = self.api_call('/user/login/sendSmsCode', params=params, json=payload)
            verification_id = response['session_id']
            verification_code = input('Enter Wyze SMS 2FA Verification Code: ')
        payload = {
            'email': email,
            'password': password,
            'mfa_type': mfa_type,
            'verification_id': verification_id,
            'verification_code': verification_code
        }
        return self.api_call('/user/login', json=payload, nonce=self.request_verifier.clock.nonce())
