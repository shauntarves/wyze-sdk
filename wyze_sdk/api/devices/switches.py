from datetime import datetime, timedelta
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.api.base import BaseClient
from wyze_sdk.models import JsonObject
from wyze_sdk.models.devices import DeviceModels, DeviceProp
from wyze_sdk.models.devices.switches import (Switch, SwitchProps, SwitchTimerAction, SwitchTimerActionType)
from wyze_sdk.service import WyzeResponse


class SwitchesClient(BaseClient):
    """A Client that services Wyze switches.
    """

    def list(self, **kwargs) -> Sequence[Switch]:
        """Lists all switches available to a Wyze account.

        :rtype: Sequence[Switch]
        """
        return [Switch(**device) for device in self._list_switches()]

    def _list_switches(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices() if device["product_model"] in DeviceModels.SWITCH]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Switch]:
        """Retrieves details of a switch.

        :param str device_mac: The device mac. e.g. ``LD_SS1_ABCDEF1234567890``

        :rtype: Optional[Switch]
        """
        switches = [_switch for _switch in self._list_switches() if _switch['mac'] == device_mac]
        if len(switches) == 0:
            return None

        switch = switches[0]

        iot_prop = super()._sirius_client().get_iot_prop(did=device_mac, keys=[prop_def.pid for prop_def in Switch.props().values()])
        if "data" in iot_prop.data and "props" in iot_prop.data["data"]:
            switch.update(iot_prop.data["data"]["props"])

        return Switch(**switch)

    def turn_on(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns on a switch.

        :param str device_mac: The device mac. e.g. ``LD_SS1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``LD_SS1``
        :param Optional[timedelta] after: The delay before performing the action.

        :rtype: WyzeResponse
        """
        if after is None:
            return self._set_switch_properties(device_mac, device_model, DeviceProp(definition=SwitchProps.switch_power(), value=True))

        return self._set_switch_properties(device_mac, device_model, DeviceProp(definition=SwitchProps.timer_action(), value=[SwitchTimerAction(action=SwitchTimerActionType.TURN_ON, time=datetime.now() + after)]))

    def turn_off(self, *, device_mac: str, device_model: str, after: Optional[timedelta] = None, **kwargs) -> WyzeResponse:
        """Turns off a switch.

        :param str device_mac: The device mac. e.g. ``LD_SS1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``LD_SS1``
        :param Optional[timedelta] after: The delay before performing the action.

        :rtype: WyzeResponse
        """
        if after is None:
            return self._set_switch_properties(device_mac, device_model, DeviceProp(definition=SwitchProps.switch_power(), value=False))

        return self._set_switch_properties(device_mac, device_model, DeviceProp(definition=SwitchProps.timer_action(), value=[SwitchTimerAction(action=SwitchTimerActionType.TURN_OFF, time=datetime.now() + after)]))

    def clear_timer(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Clears any existing power state timer on the switch.

        :param str device_mac: The device mac. e.g. ``LD_SS1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``LD_SS1``
        """
        return self._set_switch_properties(device_mac, device_model, DeviceProp(definition=SwitchProps.timer_action(), value=[]))

    def set_away_mode(self, *, device_mac: str, device_model: str, away_mode: bool = True, **kwargs) -> WyzeResponse:
        """Sets away/vacation mode for a switch.

        :param str device_mac: The device mac. e.g. ``LD_SS1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``LD_SS1``
        :param bool away_mode: The new away mode. e.g. ``True``
        """
        return self._set_switch_property(device_mac, device_model, DeviceProp(definition=SwitchProps.away_mode(), value=away_mode))

    def _set_switch_property(self, device_mac: str, device_model: str, prop: DeviceProp) -> WyzeResponse:
        return super()._sirius_client().set_iot_prop(did=device_mac, model=device_model, key=prop.definition.pid, value=str(prop.api_value))

    def _set_switch_properties(self, device_mac: str, device_model: str, props: Union[DeviceProp, Sequence[DeviceProp]]) -> WyzeResponse:
        if not isinstance(props, (list, Tuple)):
            props = [props]
        the_props = {}
        for prop in props:
            if prop.definition.type == JsonObject:
                the_props[prop.definition.pid] = prop.api_value.to_json()
            elif prop.definition.type == Sequence:
                the_props[prop.definition.pid] = [_prop.to_json() for _prop in prop.api_value if isinstance(_prop, JsonObject)]
            else:
                the_props[prop.definition.pid] = str(prop.api_value)
        return super()._sirius_client().set_iot_prop_by_topic(
            did=device_mac, model=device_model, props=the_props)
