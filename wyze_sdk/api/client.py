import logging
from typing import Optional, Sequence

from wyze_sdk.api.base import BaseClient
from wyze_sdk.api.devices import (BulbsClient, CamerasClient,
                                  ContactSensorsClient, LocksClient,
                                  MotionSensorsClient, PlugsClient,
                                  ScalesClient, ThermostatsClient,
                                  VacuumsClient)
from wyze_sdk.api.events import EventsClient
from wyze_sdk.errors import WyzeClientConfigurationError
from wyze_sdk.models.devices import Device, DeviceParser
from wyze_sdk.service import (ApiServiceClient, AuthServiceClient,
                              PlatformServiceClient, WyzeResponse)


class Client(object):
    """A Wyze Client is the wrapper on top of Wyze endpoints and allows apps
    to communicate with the various Wyze API platforms.

    The Wyze API is an interface for querying information from
    and enacting change on Wyze devices.

    This client handles constructing and sending HTTP requests to Wyze
    as well as parsing any responses received into a WyzeResponse.

    >>> import os
    >>> from wyze_sdk import Client
    >>> client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
    >>> response = client.bulbs.turn_on(
    >>>     device_mac='ABCDEF1234567890',
    >>>     device_model='WLPA19C')

    .. note:: Any attributes or methods prefixed with _underscores are intended to be "private" internal use only. They may be changed or removed at anytime.
    """
    _logger = logging.getLogger(__name__)
    _token: str = None
    _user_id: str = None

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        totp_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        #: A string specifying the account email address.
        self._email = email
        #: An unencrypted string specifying the account password.
        self._password = password
        #: An unencrypted string specifying the TOTP Key for automatic TOTP 2FA verification code generation.
        self._totp_key = totp_key
        #: An optional string representing the API base URL. **This should not be used except for when running tests.**
        self._base_url = base_url
        #: The maximum number of seconds the client will wait to connect and receive a response from Wyze. Defaults to 30
        self.timeout = timeout

        self.login()

    @property
    def vacuums(self) -> VacuumsClient:
        return VacuumsClient(token=self._token, base_url=self._base_url)

    @property
    def thermostats(self) -> ThermostatsClient:
        return ThermostatsClient(token=self._token, base_url=self._base_url)

    @property
    def cameras(self) -> CamerasClient:
        return CamerasClient(token=self._token, base_url=self._base_url)

    @property
    def bulbs(self) -> BulbsClient:
        return BulbsClient(token=self._token, base_url=self._base_url)

    @property
    def plugs(self) -> PlugsClient:
        return PlugsClient(token=self._token, base_url=self._base_url)

    @property
    def entry_sensors(self) -> ContactSensorsClient:
        return ContactSensorsClient(token=self._token, base_url=self._base_url)

    @property
    def motion_sensors(self) -> MotionSensorsClient:
        return MotionSensorsClient(token=self._token, base_url=self._base_url)

    @property
    def locks(self) -> LocksClient:
        return LocksClient(token=self._token, base_url=self._base_url, user_id=self._user_id)

    @property
    def scales(self) -> ScalesClient:
        return ScalesClient(token=self._token, user_id=self._user_id, base_url=self._base_url)

    @property
    def events(self) -> EventsClient:
        return EventsClient(token=self._token, base_url=self._base_url)

    def _auth_client(self) -> AuthServiceClient:
        return self._new_client(AuthServiceClient)

    def _platform_client(self) -> PlatformServiceClient:
        return self._new_client(PlatformServiceClient)

    def _api_client(self) -> ApiServiceClient:
        return self._new_client(ApiServiceClient)

    def _new_client(self, cls) -> BaseClient:
        return cls(
            token=self._token,
            **{'base_url': self._base_url} if self._base_url else {}
        )

    def _update_session(self, *, access_token: str, refresh_token: str, user_id: Optional[str] = None, **kwargs):
        self._logger.debug("refreshing session data")
        self._token = access_token
        self._refresh_token = refresh_token
        if user_id:
            self._user_id = user_id
            self._logger.debug("wyze user : %s", self._user_id)

    def login(self) -> WyzeResponse:
        """
        Exchanges email and password for an ``access_token`` and a ``refresh_token``, which
        are stored in this client. The tokens will be used for all subsequent requests
        made by this ``Client`` unless ``refresh_token()`` is called.

        :rtype: WyzeResponse

        :raises WyzeClientConfigurationError: If ``access_point`` is already set or both ``email`` and ``password`` are not set.
        """
        if self._token is not None:
            raise WyzeClientConfigurationError("already logged in")
        if self._email is None or self._password is None:
            raise WyzeClientConfigurationError("must provide email and password")
        self._logger.debug(f"access token not provided, attempting to login as {self._email}")
        response = self._auth_client().user_login(email=self._email, password=self._password, totp_key=self._totp_key)
        self._update_session(access_token=response["access_token"], refresh_token=response["refresh_token"], user_id=response["user_id"])
        return response

    def refresh_token(self) -> WyzeResponse:
        """
        Updates ``access_token`` using the previously set ``refresh_token``.

        :rtype: WyzeResponse

        :raises WyzeClientConfigurationError: If ``refresh_token`` is not already set.
        """
        if self._refresh_token is None:
            raise WyzeClientConfigurationError("client is not logged in")
        response = self._api_client().refresh_token(refresh_token=self._refresh_token)
        self._update_session(access_token=response["data"]["access_token"], refresh_token=response["data"]["refresh_token"])
        return response

    def user_get_info(self) -> WyzeResponse:
        """
        Retrieves the current user's info.

        :rtype: WyzeResponse
        """
        return self._api_client().get_user_info()

    def devices_list(self, **kwargs) -> Sequence[Device]:
        """List the devices available to the current user

        :rtype: Sequence[Device]
        """
        return [DeviceParser.parse(device) for device in self._api_client().get_object_list()["data"]["device_list"]]

    def user_get_profile(self) -> WyzeResponse:
        """Retrieves the current user's profile

        :rtype: WyzeResponse
        """
        return self._platform_client().get_user_profile()

    def api_test(
        self,
        api_method: str = "api.test",
        *,
        http_verb: str = "POST",
        **kwargs
    ) -> WyzeResponse:
        """Checks API calling code

        :rtype: WyzeResponse
        """
        return self._api_client().api_call(api_method, http_verb=http_verb, json=kwargs)
