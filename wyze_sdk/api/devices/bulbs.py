from datetime import datetime, timedelta
from typing import Optional, Sequence, Union

from wyze_sdk.errors import WyzeFeatureNotSupportedError
from wyze_sdk.models.devices import (Bulb, BulbProps, DeviceModels, DeviceProp, DeviceProps, MeshBulb,
                                     PropDef)
from wyze_sdk.service import WyzeResponse, api_service
from wyze_sdk.api.base import BaseClient


class BulbsClient(BaseClient):
    """A Client that services Wyze bulbs/lights.

    Methods:
        list: Lists all bulbs available to a Wyze account
        info: Retrieves details of a bulb
        turn_on: Turns on a bulb
        turn_off: Turns off a bulb
        set_brightness: Sets the brightness of a bulb
        set_color_temp: Sets the color temperature of a bulb
        set_color: Sets the color of a bulb
        clear_timer: Clears any existing power state timer on the bulb
        set_away_mode: Sets away/vacation mode for a bulb
    """

    def _list_bulbs(self) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device['product_model'] in DeviceModels.BULB]

    def list(self) -> Sequence[Bulb]:
        """Lists all bulbs available to a Wyze account.

        Returns:
            (Sequence[Bulb])
        """
        return [Bulb(**device) for device in self._list_bulbs()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Union[MeshBulb, Bulb]]:
        """Retrieves details of a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'

        Returns:
            (Optional[Bulb])
        """
        bulbs = [_bulb for _bulb in self._list_bulbs() if _bulb['mac']
                 == device_mac]
        if len(bulbs) == 0:
            return None

        bulb = bulbs[0]

        if bulb["product_type"] == MeshBulb.type:
            device_info = super()._api_client().get_v1_device_info(mac=device_mac)
            if "data" in device_info.data and device_info.data['data'] is not None:
                bulb.update(device_info.data["data"])

        bulb.update(
            super()._api_client().get_device_property_list(
                mac=bulb['mac'],
                model=bulb['product_model'],
                target_pids=[])["data"]
        )

        return Bulb.parse(bulb)

    def turn_on(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns on a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            after (timedelta): The delay before performing the action.
        """
        prop_def = DeviceProps.power_state

        if device_model in DeviceModels.MESH_BULB:
            if after is not None:
                raise WyzeFeatureNotSupportedError("delayed power action")
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=PropDef(prop_def.pid, str), value="1"),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        if after is None:
            return super()._api_client().set_device_property(
                mac=device_mac, model=device_model, pid=prop_def.pid, value=1)

        return super()._api_client().set_device_timer(mac=device_mac, plan_execute_ts=datetime.now() + after, action_type=1, action_value=1)

    def turn_off(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns off a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            after (timedelta): The delay before performing the action.
        """
        prop_def = DeviceProps.power_state

        if device_model in DeviceModels.MESH_BULB:
            if after is not None:
                raise WyzeFeatureNotSupportedError("delayed power action")
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=PropDef(prop_def.pid, str), value="0"),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        if after is None:
            return super()._api_client().set_device_property(
                mac=device_mac, model=device_model, pid=prop_def.pid, value=0)

        return super()._api_client().set_device_timer(mac=device_mac, plan_execute_ts=datetime.now() + after, action_type=1, action_value=0)

    def set_brightness(self, *, device_mac: str, device_model: str, brightness: int, **kwargs) -> WyzeResponse:
        """Sets the brightness of a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            brightness (int): The new brightness. e.g. 45
        """
        prop_def = BulbProps.brightness
        prop_def.validate(brightness)

        if device_model in DeviceModels.MESH_BULB:
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=prop_def, value=str(brightness)),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        return super()._api_client().set_device_property(
            mac=device_mac, model=device_model, pid=prop_def.pid, value=brightness)

    def set_color_temp(self, *, device_mac: str, device_model: str, color_temp: int, **kwargs) -> WyzeResponse:
        """Sets the color temperature of a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            color_temp (int): The new color temperature. e.g. 3400
        """
        prop_def = BulbProps.color_temp
        prop_def.validate(color_temp)

        if device_model in DeviceModels.MESH_BULB:
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=PropDef(prop_def.pid, str), value=str(color_temp)),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        return super()._api_client().set_device_property(
            mac=device_mac, model=device_model, pid=prop_def.pid, value=color_temp)

    def set_color(self, *, device_mac: str, device_model: str, color: str, **kwargs) -> WyzeResponse:
        """Sets the color of a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            color (str): The new color temperature. e.g. 'ff0000'

        Raises:
            WyzeFeatureNotSupportedError: If the bulb doesn't support color
        """
        if device_model not in DeviceModels.MESH_BULB:
            raise WyzeFeatureNotSupportedError("set_color")

        prop_def = BulbProps.color
        prop_def.validate(color)

        return super()._api_client().run_action_list(
            actions={
                "key": "set_mesh_property",
                "prop": DeviceProp(definition=prop_def, value=color),
                "device_mac": device_mac,
                "provider_key": device_model,
            }
        )

    def clear_timer(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Clears any existing power state timer on the bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
        """
        if device_model in DeviceModels.MESH_BULB:
            raise WyzeFeatureNotSupportedError("clear_timer")
        return super()._api_client().cancel_device_timer(mac=device_mac, action_type=1)

    def set_away_mode(self, *, device_mac: str, device_model: str, away_mode: bool = True, **kwargs) -> WyzeResponse:
        """Sets away/vacation mode for a bulb.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            away_mode (bool): The new away mode. e.g. True
        """
        return self._set_away_mode_enabled(device_mac=device_mac, device_model=device_model) if away_mode else self._set_away_mode_disbled(device_mac=device_mac, device_model=device_model)

    def _set_away_mode_enabled(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        if device_model in DeviceModels.MESH_BULB:
            return super()._api_client().run_action(
                mac=device_mac,
                action_key="switch_rule",
                action_params={"mac": [device_mac], "rule": api_service.AwayModeGenerator().value},
                provider_key=device_model,
            )
        return super()._api_client().run_action(
            mac=device_mac,
            action_key="switch_rule",
            action_params={"rule": api_service.AwayModeGenerator().value},
            provider_key=device_model,
        )

    def _set_away_mode_disbled(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        prop_def = BulbProps.away_mode

        if device_model in DeviceModels.MESH_BULB:
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=prop_def, value=False),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        super()._api_client().set_device_property(mac=device_mac, model=device_model, pid=prop_def.pid, value="0")
