from datetime import timedelta
from typing import Optional, Sequence

from wyze_sdk.api.base import BaseClient
from wyze_sdk.errors import WyzeFeatureNotSupportedError
from wyze_sdk.models.devices import (Bulb, BulbProps, DeviceModels, DeviceProp,
                                     DeviceProps, MeshBulb, PropDef)
from wyze_sdk.models.devices.bulbs import BaseBulb
from wyze_sdk.models.devices.lights import LightProps
from wyze_sdk.service import WyzeResponse, api_service


class BulbsClient(BaseClient):
    """A Client that services Wyze bulbs/lights.
    """

    def _list_bulbs(self) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device['product_model'] in DeviceModels.BULB]

    def list(self) -> Sequence[Bulb]:
        """Lists all bulbs available to a Wyze account.

        :rtype: Sequence[Bulb]
        """
        return [Bulb(**device) for device in self._list_bulbs()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[BaseBulb]:
        """Retrieves details of a bulb.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Optional[BaseBulb]
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

        return BaseBulb.parse(bulb)

    def turn_on(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns on a bulb.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``WLPA19``
        :param Optional[timedelta] after: The delay before performing the action.

        :rtype: WyzeResponse
        """
        prop_def = DeviceProps.power_state()

        if device_model in DeviceModels.MESH_BULB:
            if after is not None:
                return super()._api_client().set_device_timer(mac=device_mac, delay_time=after.seconds, action_type=1, action_value=1)
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=PropDef(prop_def.pid, str), value="1"),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        if after is None:
            return super()._api_client().set_device_property_list(
                mac=device_mac, model=device_model, props=DeviceProp(definition=PropDef(prop_def.pid, str), value="1"))

        return super()._api_client().set_device_timer(mac=device_mac, delay_time=after.seconds, action_type=1, action_value=1)

    def turn_off(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns off a bulb.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``WLPA19``
        :param timedelta after: The delay before performing the action.

        :rtype: WyzeResponse
        """
        prop_def = DeviceProps.power_state()

        if device_model in DeviceModels.MESH_BULB:
            if after is not None:
                return super()._api_client().set_device_timer(mac=device_mac, delay_time=after.seconds, action_type=1, action_value=0)
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=PropDef(prop_def.pid, str), value="0"),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        if after is None:
            return super()._api_client().set_device_property_list(
                mac=device_mac, model=device_model, props=DeviceProp(definition=PropDef(prop_def.pid, str), value="0"))

        return super()._api_client().set_device_timer(mac=device_mac, delay_time=after.seconds, action_type=1, action_value=0)

    def set_brightness(self, *, device_mac: str, device_model: str, brightness: int, **kwargs) -> WyzeResponse:
        """Sets the brightness of a bulb.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``WLPA19``
        :param int brightness: The new brightness. e.g. ``45``

        :rtype: WyzeResponse

        :raises WyzeRequestError: if the new brightness is not valid
        """
        prop_def = BulbProps.brightness()
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
        return super()._api_client().set_device_property_list(
            mac=device_mac, model=device_model, props=DeviceProp(definition=PropDef(prop_def.pid, str), value=str(brightness)))

    def set_color_temp(self, *, device_mac: str, device_model: str, color_temp: int, **kwargs) -> WyzeResponse:
        """Sets the color temperature of a bulb.

        Args:
            :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
            :param str device_model: The device model. e.g. ``WLPA19``
            :param int color_temp: The new color temperature. e.g. ``3400``

        :rtype: WyzeResponse

        :raises WyzeRequestError: if the new color temperature is not valid
        """

        if device_model in DeviceModels.MESH_BULB:
            prop_def = BulbProps.color_temp_mesh()
            prop_def.validate(color_temp)

            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=PropDef(prop_def.pid, str), value=str(color_temp)),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )

        prop_def = BulbProps.color_temp()
        prop_def.validate(color_temp)

        return super()._api_client().set_device_property_list(
            mac=device_mac, model=device_model, props=DeviceProp(definition=PropDef(prop_def.pid, str), value=str(color_temp)))

    def set_color(self, *, device_mac: str, device_model: str, color: str, **kwargs) -> WyzeResponse:
        """Sets the color of a bulb.

        Args:
            :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
            :param str device_model: The device model. e.g. ``WLPA19``
            :param str color: The new color temperature. e.g. ``ff0000``

        :rtype: WyzeResponse

        :raises WyzeFeatureNotSupportedError: If the bulb doesn't support color
        """
        if device_model not in DeviceModels.MESH_BULB:
            raise WyzeFeatureNotSupportedError("set_color")

        prop_def = BulbProps.color()
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

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``WLPA19``

        :rtype: WyzeResponse
        """
        return super()._api_client().cancel_device_timer(mac=device_mac, action_type=1)

    def set_sun_match(self, *, device_mac: str, device_model: str, sun_match: bool = True, **kwargs) -> WyzeResponse:
        """Sets sunlight matching to mimic natural sunlight for a bulb.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``WLPA19``
        :param bool sun_match: The new sun match. e.g. ``True``

        :rtype: WyzeResponse
        """
        prop_def = LightProps.sun_match()

        return super()._api_client().set_device_property_list(
            mac=device_mac, model=device_model, props=DeviceProp(definition=PropDef(prop_def.pid, str), value="1" if sun_match else "0"))

    def set_away_mode(self, *, device_mac: str, device_model: str, away_mode: bool = True, **kwargs) -> WyzeResponse:
        """Sets away/vacation mode for a bulb.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``WLPA19``
        :param bool away_mode: The new away mode. e.g. ``True``

        :rtype: WyzeResponse
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
        prop_def = LightProps.away_mode()

        if device_model in DeviceModels.MESH_BULB:
            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": DeviceProp(definition=prop_def, value=False),
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )
        return super()._api_client().set_device_property(
            mac=device_mac, model=device_model, pid=prop_def.pid, value="0")
