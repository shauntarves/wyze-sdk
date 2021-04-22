from datetime import datetime, timedelta
from typing import Optional, Sequence

from wyze_sdk.models.devices import DeviceModels, DeviceProps, Plug, PlugProps
from wyze_sdk.service import WyzeResponse, api_service
from wyze_sdk.api.base import BaseClient


class PlugsClient(BaseClient):
    """A Client that services Wyze plugs/outlets.

    Methods:
        list: Lists all plugs available to a Wyze account
        info: Retrieves details of a plug
        turn_on: Turns on a plug
        turn_off: Turns off a plug
        clear_timer: Clears any existing power state timer on the plug
        set_away_mode: Sets away/vacation mode for a plug
    """

    def _list_plugs(self) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device['product_model'] in DeviceModels.PLUG]

    def list(self) -> Sequence[Plug]:
        """Lists all plugs available to a Wyze account.

        Returns:
            (Sequence[Plug])
        """
        return [Plug(**device) for device in self._list_plugs()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Plug]:
        """Retrieves details of a plug.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'

        Returns:
            (Optional[Plug])
        """
        plugs = [_plug for _plug in self._list_plugs() if _plug['mac']
                 == device_mac]
        if len(plugs) == 0:
            return None

        plug = plugs[0]
        plug.update(
            super()._api_client().get_device_property_list(
                mac=plug['mac'],
                model=plug['product_model'],
                target_pids=[])["data"]
        )

        switch_state_timer = super()._api_client().get_device_timer(mac=device_mac, action_type=1)
        if "data" in switch_state_timer.data and switch_state_timer.data['data'] is not None:
            plug.update({"switch_state_timer": switch_state_timer.data["data"]})

        return Plug.parse(plug)

    def turn_on(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns on a plug.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPP1'
            after (timedelta): The delay before performing the action.
        """
        prop_def = DeviceProps.power_state

        if after is None:
            return super()._api_client().set_device_property(
                mac=device_mac, model=device_model, pid=prop_def.pid, value=1)

        return super()._api_client().set_device_timer(mac=device_mac, delay_time=after.seconds, action_type=1, action_value=1)

    def turn_off(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns off a plug.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPP1'
            after (timedelta): The delay before performing the action.
        """
        prop_def = DeviceProps.power_state

        if after is None:
            return super()._api_client().set_device_property(
                mac=device_mac, model=device_model, pid=prop_def.pid, value=0)

        return super()._api_client().set_device_timer(mac=device_mac, plan_execute_ts=datetime.now() + after, action_type=1, action_value=0)

    def clear_timer(self, *, device_mac: str, **kwargs) -> WyzeResponse:
        """Clears any existing power state timer on the plug.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
        """
        return super()._api_client().cancel_device_timer(mac=device_mac, action_type=1)

    def set_away_mode(self, *, device_mac: str, device_model: str, away_mode: bool = True, **kwargs) -> WyzeResponse:
        """Sets away/vacation mode for a plug.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPP1'
            away_mode (bool): The new away mode. e.g. True
        """
        prop_def = PlugProps.away_mode
        if away_mode:
            return super()._api_client().run_action(
                mac=device_mac,
                action_key="switch_rule",
                action_params={"rule": api_service.AwayModeGenerator().value},
                provider_key=device_model,
            )
        return super()._api_client().set_device_property(mac=device_mac, model=device_model, pid=prop_def.pid, value="0")
