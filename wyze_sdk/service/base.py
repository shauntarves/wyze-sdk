import logging
import platform
import sys
import time
import uuid
from abc import ABCMeta
from contextlib import suppress
from json import dumps
from typing import Dict, Optional, Union
from urllib.parse import urljoin

import requests

from wyze_sdk import version
from wyze_sdk.errors import WyzeRequestError
from wyze_sdk.signature import RequestVerifier

from .wyze_response import WyzeResponse


class BaseServiceClient(metaclass=ABCMeta):

    WYZE_APP_ID = "9319141212m2ik"
    WYZE_APP_NAME = "wyze"
    WYZE_APP_VERSION = "2.19.14"
    WYZE_PHONE_TYPE = 2

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        headers: Optional[dict] = None,
        app_id: Optional[str] = WYZE_APP_ID,
        app_name: Optional[str] = WYZE_APP_NAME,
        app_version: Optional[str] = WYZE_APP_VERSION,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        phone_id: Optional[str] = None,
        phone_type: Optional[int] = WYZE_PHONE_TYPE,
        request_verifier: Optional[RequestVerifier] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.token = None if token is None else token.strip()
        self.base_url = base_url
        self.timeout = timeout
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = app_version
        self.headers = headers or {}
        # self.headers["User-Agent"] = self._get_user_agent(
        #     user_agent_prefix, user_agent_suffix
        # )
        self.phone_id = phone_id if phone_id else str(uuid.uuid4())
        self.phone_type = phone_type
        self.default_params = {}
        self.request_verifier = request_verifier
        self._logger = logger if logger is not None else logging.getLogger(__name__)

    def _get_user_agent(self, prefix: Optional[str] = None, suffix: Optional[str] = None):
        """Construct the user-agent header with the package info,
        Python version and OS version.
        Returns:
            The user agent string.
            e.g. 'Python/3.6.7 wyzeclient/2.0.0 Darwin/17.7.0'
        """
        # __name__ returns all classes, we only want the client
        client = "{0}/{1}".format("wyzeclient", version.__version__)
        python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info)
        system_info = "{0}/{1}".format(platform.system(), platform.release())
        user_agent_string = " ".join([python_version, client, system_info])
        prefix = f"{prefix} " if prefix else ""
        suffix = f" {suffix}" if suffix else ""
        return prefix + user_agent_string + suffix

    def _do_request(
            self,
            session: requests.Session,
            request: requests.Request) -> WyzeResponse:
        with suppress(requests.exceptions.HTTPError, requests.exceptions.RequestException, ValueError):
            self._logger.info(f"requesting {request.method} to {request.url}")
            self._logger.debug(f"headers: {request.headers}")
            self._logger.debug(f"body: {request.body}")

            settings = session.merge_environment_settings(request.url, {}, None, None, None)

            self._logger.debug(f"settings: {settings}")

            response = session.send(request, **settings)

            return WyzeResponse(
                client=self,
                http_verb=request.method,
                api_url=request.url,
                req_args=request.body,
                data=response.json(),
                headers=response.headers,
                status_code=response.status_code,
            ).validate()

    def do_post(self, url: str, headers: dict, payload: dict) -> WyzeResponse:
        with requests.Session() as client:
            if headers is not None:
                # add the request-specific headers
                self._logger.debug('merging request-specific headers into session headers')
                client.headers.update(headers)

            # we have to use a prepared request because the requests module
            # doesn't allow us to specify the separators in our json dumping
            # and the server expects no extra whitespace
            req = client.prepare_request(requests.Request('POST', url, json=payload))

            self._logger.debug('unmodified prepared request')
            self._logger.debug(req)

            if isinstance(payload, dict):
                payload = dumps(payload, separators=(',', ':'))
            if isinstance(payload, str):
                req.body = payload.encode('utf-8')
                req.prepare_content_length(req.body)

            return self._do_request(client, req)

    def do_get(self, url: str, headers: dict, payload: dict) -> WyzeResponse:
        # params = req_args["params"] if "params" in req_args else None
        # data = req_args["data"] if "data" in req_args else None
        # headers = req_args["headers"] if "headers" in req_args else None
        # token = params.get("token") if params and "token" in params else None
        # auth = (
        #     req_args["auth"] if "auth" in req_args else None
        # )  # Basic Auth for oauth.v2.access / oauth.access

        with requests.Session() as client:
            if headers is not None:
                # add the request-specific headers
                self._logger.debug('merging request-specific headers into session headers')
                client.headers.update(headers)

            req = client.prepare_request(requests.Request('GET', url, params=payload))

            return self._do_request(client, req)

    def _nonce(self):
        return str(round(time.time() * 1000))

    def api_call(
        self,
        api_endpoint: str,
        *,
        http_verb: str = "POST",
        data: Union[dict] = None,
        params: dict = None,
        json: dict = None,
        headers: dict = None,
        auth: dict = None,
    ) -> WyzeResponse:
        """Create a request and execute the API call to Wyze.
        Args:
            api_endpoint (str): The target Wyze API endpoint.
                e.g. '/app/v2/home_page/get_object_list'
            http_verb (str): HTTP Verb. e.g. 'POST'
            data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            params (dict): The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            json (dict): JSON for the body to attach to the request
                (if data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}
            headers (dict): Additional request headers
            auth (dict): A dictionary that consists of access_token and refresh_token

        Returns:
            (WyzeResponse)
                The server's response to an HTTP request. Data
                from the response can be accessed like a dict.

        Raises:
            WyzeApiError: The following Wyze API call failed:
                '/app/v2/home_page/get_object_list'.
            WyzeRequestError: JSON data can only be submitted as
                POST requests.
        """
        has_json = json is not None
        if has_json and http_verb != "POST":
            msg = "JSON data can only be submitted as POST requests. GET requests should use the 'params' argument."
            raise WyzeRequestError(msg)

        api_url = self._get_url(self.base_url, api_endpoint)
        headers = headers or {}
        headers.update(self.headers)

        if http_verb == "POST":
            return self.do_post(url=api_url, headers=headers, payload=json)
        elif http_verb == "GET":
            return self.do_get(url=api_url, headers=headers, payload=params)

        msg = "Unknown request type."
        raise WyzeRequestError(msg)

    def _get_url(self, base_url: str, api_endpoint: str) -> str:
        """Joins the base URL and an API endpoint path to form an absolute URL.
        Args:
            base_url (str): The base URL. e.g. 'https://api.wyzecam.com'
            api_endpoint (str): The API path. e.g. '/app/v2/home_page/get_object_list'
        Returns:
            The absolute endpoint URL.
                e.g. 'https://api.wyzecam.com/app/v2/home_page/get_object_list'
        """
        return urljoin(base_url, api_endpoint)

    def _get_headers(
        self,
        *,
        headers: dict,
        signature: Optional[str] = None,
        signature2: Optional[str] = None,
        has_json: bool,
        request_specific_headers: Optional[dict],
    ) -> Dict[str, str]:
        """Constructs the headers needed for a request.
        Args:
            has_json (bool): Whether or not the request has json.
            has_files (bool): Whether or not the request has files.
            request_specific_headers (dict): Additional headers specified by the user for a specific request.
        Returns:
            The headers dictionary.
                e.g. {
                    'Content-Type': 'application/json;charset=utf-8',
                    'Signature': 'erewf3254rgt453f34f..==',
                    'User-Agent': 'Python/3.6.8 wyzeclient/2.1.0 Darwin/17.7.0'
                }
        """

        final_headers = {
            # "Content-Type": "application/json;charset=utf-8",
            'Accept-Encoding': 'gzip',
        }
        if headers is None or "User-Agent" not in headers:
            final_headers["User-Agent"] = "okhttp/4.7.2"  # self._get_user_agent()

        if signature:
            final_headers.update({"Signature": "{}".format(signature)})
        if signature2:
            final_headers.update({"Signature2": "{}".format(signature2)})
        if headers is None:
            headers = {}

        # Merge headers specified at client initialization.
        final_headers.update(headers)

        # Merge headers specified for a specific request. e.g. oauth.access
        if request_specific_headers:
            final_headers.update(request_specific_headers)

        if has_json:
            final_headers.update({"Content-Type": "application/json;charset=utf-8"})

        return final_headers

    def get_sorted_params(self, params: dict = {}) -> str:
        return '&'.join(map(lambda x: x[0] + '=' + str(x[1]), params))


class WpkNetServiceClient(BaseServiceClient, metaclass=ABCMeta):
    """
    wpk net service client is the wrapper to newer Wyze services like WpkWyzeSignatureService and WpkWyzeExService.
    """

    WYZE_APP_NAME = "com.hualai"
    WYZE_SALTS = {
        "9319141212m2ik": "wyze_app_secret_key_132",
        "venp_4c30f812828de875": "CVCSNoa0ALsNEpgKls6ybVTVOmGzFoiq",
    }

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = "https://api.wyzecam.com/",
        app_name: str = WYZE_APP_NAME,
        app_id: str = BaseServiceClient.WYZE_APP_ID,
        request_verifier: RequestVerifier = None
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            app_name=app_name,
            app_id=app_id,
            request_verifier=request_verifier if request_verifier is not None else RequestVerifier(signing_secret=WpkNetServiceClient.WYZE_SALTS[app_id], access_token=token)
        )

    def _get_headers(
        self,
        *,
        request_specific_headers: Optional[dict] = None,
        nonce: int = None,
    ) -> Dict[str, str]:
        if request_specific_headers is None:
            request_specific_headers = {}

        request_specific_headers.update({
            'access_token': self.token,
            'requestid': self.request_verifier.request_id(nonce),
        })

        return super()._get_headers(headers=None, has_json=False, request_specific_headers=request_specific_headers)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        params: dict = None,
        json: dict = None,
        headers: Optional[dict] = None,
        nonce: int = None,
    ) -> WyzeResponse:
        if headers is None:
            headers = {}

        if http_verb == "POST":
            # this must be done here so that it will be included in the signing
            if json is None:
                json = {}
            json['nonce'] = str(nonce)
            request_data = dumps(json, separators=(',', ':'))
            headers.update({
                'signature2': self.request_verifier.generate_dynamic_signature(timestamp=nonce, body=request_data)
            })
        elif http_verb == "GET":
            if params is None:
                params = {}
            # this must be done here so that it will be included in the signing
            params['nonce'] = nonce
            headers.update({
                'signature2': self.request_verifier.generate_dynamic_signature(timestamp=nonce, body=self.get_sorted_params(sorted(params.items())))
            })

        return super().api_call(
            api_method,
            http_verb=http_verb,
            data=None,
            params=params,
            json=json,
            headers=self._get_headers(request_specific_headers=headers, nonce=nonce),
            auth=None,
        )


class ExServiceClient(WpkNetServiceClient, metaclass=ABCMeta):
    """
    ex service client is the wrapper for WpkWyzeExService.
    """

    def _get_headers(
        self,
        *,
        request_specific_headers: Optional[dict] = None,
        nonce: Optional[int] = None,
    ) -> Dict[str, str]:
        if request_specific_headers is None:
            request_specific_headers = {}

        request_specific_headers.update({
            'appid': self.app_id,
            'appinfo': f"wyze_android_{self.app_version}",
            'phoneid': self.phone_id,
        })

        return super()._get_headers(request_specific_headers=request_specific_headers)


class SignatureServiceClient(WpkNetServiceClient, metaclass=ABCMeta):
    """
    signature service client is the wrapper for WpkWyzeSignatureService
    """
