from datetime import datetime, timedelta
from typing import Optional, Sequence

from wyze_sdk.api.base import BaseClient
from wyze_sdk.models.devices import Camera, DeviceModels
from wyze_sdk.service import WyzeResponse


class CamerasClient(BaseClient):
    """A Client that services Wyze cameras.

    Methods:
        list: Lists all cameras available to a Wyze account
        info: Retrieves details of a camera
        turn_on: Turns on a camera
        turn_off: Turns off a camera
    """

    def _list_cameras(self) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device['product_model'] in DeviceModels.CAMERA]

    def list(self) -> Sequence[Camera]:
        """Lists all cameras available to a Wyze account.

        Returns:
            (Sequence[Camera])
        """
        return [Camera(**device) for device in self._list_cameras()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Camera]:
        """Retrieves details of a camera.

        Args:
            :param str device_mac: The device mac. e.g. 'ABCDEF1234567890'

        Returns:
            (Optional[Camera])
        """
        cameras = [_camera for _camera in self._list_cameras() if _camera['mac'] == device_mac]
        if len(cameras) == 0:
            return None

        camera = cameras[0]
        camera.update(
            super()._api_client().get_device_info(
                mac=camera['mac'],
                model=camera['product_model'])["data"]
        )

        latest_events = super()._api_client().get_event_list(
            device_ids=[camera["mac"]], begin=datetime.now() - timedelta(days=1), end=datetime.now())
        if "data" in latest_events.data and latest_events.data['data'] is not None:
            camera.update(latest_events.data["data"])

        return Camera(**camera)

    def turn_on(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Turns on a camera.

        Args:
            :param str device_mac: The device mac. e.g. 'ABCDEF1234567890'
            :param str device_model: The device model. e.g. 'WYZEC1-JZ'
        """
        return super()._api_client().run_action(
            mac=device_mac, provider_key=device_model, action_key="power_on")

    def turn_off(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Turns off a camera.

        Args:
            :param str device_mac: The device mac. e.g. 'ABCDEF1234567890'
            :param str device_model: The device model. e.g. 'WYZEC1-JZ'
        """
        return super()._api_client().run_action(
            mac=device_mac, provider_key=device_model, action_key="power_off")

    def restart(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Restarts a camera.

        Args:
            :param str device_mac: The device mac. e.g. 'ABCDEF1234567890'
            :param str device_model: The device model. e.g. 'WYZEC1-JZ'
        """
        return super()._api_client().run_action(
            mac=device_mac, provider_key=device_model, action_key="restart")
