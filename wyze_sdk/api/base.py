import logging
from abc import ABCMeta
from typing import Optional, Sequence

from wyze_sdk.errors import WyzeClientConfigurationError
from wyze_sdk.models.devices.base import DeviceModels
from wyze_sdk.service import (ApiServiceClient, EarthServiceClient,
                              GeneralApiServiceClient, PlatformServiceClient,
                              ScaleServiceClient, SiriusServiceClient,
                              PlutoServiceClient, VenusServiceClient,
                              WyzeResponse)


class BaseClient(object, metaclass=ABCMeta):

    def __init__(
        self,
        token: str = None,
        user_id: str = None,
        base_url: Optional[str] = None,
        logger: logging.Logger = logging.getLogger(__name__),
        **kwargs,
    ):
        if token is None:
            raise WyzeClientConfigurationError("client is not logged in")
        self._token = token.strip()
        self._user_id = user_id
        self._base_url = base_url
        self._logger = logger

    def _platform_client(self) -> PlatformServiceClient:
        return BaseClient._service_client(PlatformServiceClient, token=self._token, base_url=self._base_url)

    def _api_client(self) -> ApiServiceClient:
        return BaseClient._service_client(ApiServiceClient, token=self._token, base_url=self._base_url)

    @staticmethod
    def _service_client(cls, *, token: str, base_url: Optional[str] = None, **kwargs) -> "BaseClient":
        """Create a service client to execute the API call to Wyze.
        Args:
            cls (class): The target service client.
                e.g. 'PlatformServiceClient'
            token (str): The access token.
            base_url (Optional[str]): The base url of the service.
        Returns:
            (BaseClient)
                A new pre-configured client for interacting
                with the target service.
        """
        return cls(
            token=token,
            **{{'base_url': base_url}, kwargs} if base_url is not None else kwargs,
        )

    def _earth_client(self) -> EarthServiceClient:
        return BaseClient._service_client(EarthServiceClient, token=self._token, base_url=self._base_url)

    def _general_api_client(self) -> GeneralApiServiceClient:
        return GeneralApiServiceClient(
            token=self._token,
            **{'base_url': self._base_url} if self._base_url else {},
            user_id=self._user_id,
        )

    def _scale_client(self, device_model: str = DeviceModels.SCALE_[0]) -> ScaleServiceClient:
        return BaseClient._service_client(
            ScaleServiceClient if device_model in DeviceModels.SCALE_ else PlutoServiceClient, token=self._token, base_url=self._base_url)

    def _sirius_client(self) -> EarthServiceClient:
        return BaseClient._service_client(SiriusServiceClient, token=self._token, base_url=self._base_url)

    def _pluto_client(self) -> PlutoServiceClient:
        return BaseClient._service_client(PlutoServiceClient, token=self._token, base_url=self._base_url)

    def _venus_client(self) -> VenusServiceClient:
        return BaseClient._service_client(VenusServiceClient, token=self._token, base_url=self._base_url)

    def _create_user_event(self, pid: str, event_id: str, event_type: int) -> WyzeResponse:
        self._general_api_client().post_user_event(pid=pid, event_id=event_id, event_type=event_type)

    def _list_devices(self, **kwargs) -> Sequence[dict]:
        return self._api_client().get_object_list()["data"]["device_list"]
