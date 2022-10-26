from datetime import timedelta
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.api.base import BaseClient
from wyze_sdk.errors import WyzeFeatureNotSupportedError, WyzeRequestError
from wyze_sdk.models.devices import (Bulb, BulbProps, DeviceModels, DeviceProp,
                                     DeviceProps, MeshBulb, PropDef)
from wyze_sdk.models.devices.bulbs import BaseBulb
from wyze_sdk.models.devices.lights import LightControlMode, LightProps, LightVisualEffect
from wyze_sdk.service import WyzeResponse, api_service


class BulbsClient(BaseClient):
    """A Client that services Wyze bulbs/lights.
    """

    LIGHT_STRIP_PRO_SUBSECTION_COUNT = 16

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
            _prop_def = BulbProps.color_temp_mesh()
            _prop_def.validate(color_temp)

            _prop = DeviceProp(definition=PropDef(_prop_def.pid, str), value=str(color_temp))
            if device_model in DeviceModels.LIGHT_STRIP:
                _prop = [_prop]
                _prop.append(DeviceProp(definition=LightProps.control_light(), value=LightControlMode.TEMPERATURE.code))

            return super()._api_client().run_action_list(
                actions={
                    "key": "set_mesh_property",
                    "prop": _prop,
                    "device_mac": device_mac,
                    "provider_key": device_model,
                }
            )

        prop_def = BulbProps.color_temp()
        prop_def.validate(color_temp)

        return super()._api_client().set_device_property_list(
            mac=device_mac, model=device_model, props=DeviceProp(definition=PropDef(prop_def.pid, str), value=str(color_temp)))

    def set_color(self, *, device_mac: str, device_model: str, color: Union[str, Sequence[str]], **kwargs) -> WyzeResponse:
        """Sets the color of a bulb.

        For Light Strip Pro devices, this color can be a list of 16 colors that will
        be used to set the value for each subsection of the light strip. The list is
        ordered like:
        ``
        15 14 13 12
         8  9 10 11
         7  6  5  4
         0  1  2  3
        ``

        Args:
            :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
            :param str device_model: The device model. e.g. ``WLPA19``
            :param color: The new color(s). e.g. ``ff0000`` or ``['ff0000', '00ff00', ...]``
            :type color: Union[str, Sequence[str]]

        :rtype: WyzeResponse

        :raises WyzeFeatureNotSupportedError: If the bulb doesn't support color
            or color is a list and the bulb doesn't support color sections
        """
        if device_model not in DeviceModels.MESH_BULB:
            raise WyzeFeatureNotSupportedError("set_color")

        _color_prop_def = BulbProps.color()
        _color_prop = None

        if isinstance(color, (list, Tuple)):
            if device_model not in DeviceModels.LIGHT_STRIP_PRO:
                raise WyzeFeatureNotSupportedError("The target device type does not support color sections.")
            if len(color) != self.LIGHT_STRIP_PRO_SUBSECTION_COUNT:
                raise WyzeRequestError(f"Color must specify values for all {self.LIGHT_STRIP_PRO_SUBSECTION_COUNT} subsections.")

            color = list(map(lambda _color: _color.upper(), color))
            for _color in color:
                _color_prop_def.validate(_color)
        else:
            color = color.upper()
            _color_prop_def.validate(color)
            _color_prop = DeviceProp(definition=PropDef(_color_prop_def.pid, str), value=str(color))

        _prop = _color_prop

        # if we're dealing with a light strip, we need to set the color control mode
        if device_model in DeviceModels.LIGHT_STRIP:
            _prop = [DeviceProp(definition=LightProps.control_light(), value=LightControlMode.COLOR.code)]
            # Pro light strips also need their subsection property updated
            if device_model in DeviceModels.LIGHT_STRIP_PRO:
                if isinstance(color, str):
                    # turn this into a list of subsections for joining
                    color = [color] * self.LIGHT_STRIP_PRO_SUBSECTION_COUNT
                _prop.append(DeviceProp(definition=LightProps.subsection(), value="00" + "#00".join(color)))

        return super()._api_client().run_action_list(
            actions={
                "key": "set_mesh_property",
                "prop": _prop,
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

    def set_effect(self, *, device_mac: str, device_model: str, effect: LightVisualEffect, **kwargs) -> WyzeResponse:
        """Sets the visual/sound effect for a light.

        Args:
            :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
            :param str device_model: The device model. e.g. ``WLPA19``
            :param str LightVisualEffect: The new visual effect definition.

        :rtype: WyzeResponse

        :raises WyzeFeatureNotSupportedError: If the light doesn't support effects
        """
        if device_model not in DeviceModels.LIGHT_STRIP:
            raise WyzeFeatureNotSupportedError("set_effect")

        _prop = effect.to_plist()
        _prop.append(DeviceProp(definition=LightProps.control_light(), value=LightControlMode.FRAGMENTED.code))

        return super()._api_client().run_action_list(
            actions={
                "key": "set_mesh_property",
                "prop": _prop,
                "device_mac": device_mac,
                "provider_key": device_model,
            }
        )
