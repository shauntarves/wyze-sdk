"""A Python module for interacting and consuming responses from Wyze."""

import logging
from typing import Union

import wyze_sdk.errors as e


class WyzeResponse:
    """A container of response data.
    Attributes:
        data (dict): The json-encoded content of the response. Along
            with the headers and status code information.
    Methods:
        validate: Check if the response from Wyze was successful.
        get: Retrieves any key from the response data.
    Note:
        Any attributes or methods prefixed with _underscores are
        intended to be "private" internal use only. They may be changed or
        removed at any time.
    """

    def __init__(
        self,
        *,
        client,
        http_verb: str,
        api_url: str,
        req_args: dict,
        data: Union[dict, bytes],  # data can be binary data
        headers: dict,
        status_code: int,
    ):
        self.http_verb = http_verb
        self.api_url = api_url
        self.req_args = req_args
        self.data = data
        self.headers = headers
        self.status_code = status_code
        self._initial_data = data
        self._iteration = None  # for __iter__ & __next__
        self._client = client
        self._logger = logging.getLogger(__name__)

    def __str__(self):
        """Return the Response data if object is converted to a string."""
        if isinstance(self.data, bytes):
            raise ValueError(
                "As the response.data is binary data, this operation is unsupported"
            )
        return f"{self.data}"

    def __getitem__(self, key):
        """Retrieves any key from the data store.
        Note:
            This is implemented so users can reference the
            WyzeResponse object like a dictionary.
            e.g. response["ok"]
        Returns:
            The value from data or None.
        """
        if isinstance(self.data, bytes):
            raise ValueError(
                "As the response.data is binary data, this operation is unsupported"
            )
        return self.data.get(key, None)

    def get(self, key, default=None):
        """Retrieves any key from the response data.
        Note:
            This is implemented so users can reference the
            WyzeResponse object like a dictionary.
            e.g. response.get("ok", False)
        Returns:
            The value from data or the specified default.
        """
        if isinstance(self.data, bytes):
            raise ValueError(
                "As the response.data is binary data, this operation is unsupported"
            )
        return self.data.get(key, default)

    def validate(self):
        """Check if the response from Wyze was successful.
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

            # if 'code' in response_json:
            #     response_code = response_json['code']

            #     if isinstance(response_code, int):
            #         response_code = str(response_code)

            #     if response_code != '1' and 'msg' in response_json and response_json[
            #             'msg'] == 'AccessTokenError':
            #         self._logger.warning(
            #             "The access token has expired. Please refresh the token and try again.")
            #         raise ProviderConnectionException(
            #             "Failed to login with response: {0}".format(response_json))
            #     if response_code != '1' and 'msg' in response_json and response_json[
            #             'msg'] == "UserIsLocked":
            #         self._logger.warning(
            #             "The user account is locked. Please resolve this issue and try again.")
            #         raise ProviderConnectionException(
            #             "Failed to login with response: {0}".format(response_json))
            #     if response_code != '1' and 'msg' in response_json and response_json[
            #             'msg'] == "UserNameOrPasswordError":
            #         self._logger.warning(
            #             "The username or password is incorrect. Please check your credentials and try again.")
            #         raise ProviderConnectionException(
            #             "Failed to login with response: {0}".format(response_json))
            #     if response_code == '1001':
            #         self._logger.error(
            #             "Request to: {} does not respond to parameters in payload {} and gave a result of {}".format(
            #                 request.url, request.body, response_json))
            #         raise ProviderInternalException(
            #             "Parameters passed to Wyze Service do not fit the endpoint")
            #     if response_code == '1003':
            #         # FIXME what do I mean?
            #         self._logger.error(
            #             "Request to: {} does not respond to parameters in payload {} and gave a result of {}".format(
            #                 request.url, request.body, response_json))
            #         raise ProviderInternalException(
            #             "Parameters passed to Wyze Service do not fit the endpoint")
            #     if response_code == '1004':
            #         self._logger.error(
            #             "Request to: {} does not have the correct signature2 of {} and gave a result of {}".format(
            #                 request.url, request.headers.signature2, response_json))
            #         raise ProviderInternalException(
            #             "Parameters passed to Wyze Service do not fit the endpoint")
            #     if response_code == '2001':
            #            self._logger.warning(
            #            "The access token has expired. Please refresh the token and try again.")
            #         raise ProviderConnectionException(
            #             "Failed to login with response: {0}".format(response_json))
            #     if response_code != '1':
            #         print(type(response_code))
            #         self._logger.error(
            #             "Request to: {} failed with payload: {} with result of {}".format(
            #                 request.url, request.body, response_json))
            #         raise ProviderInternalException(
            #             "Failed to connect to the Wyze Service")
        msg = "The request to the Wyze API failed."
        raise e.WyzeApiError(message=msg, response=self)
