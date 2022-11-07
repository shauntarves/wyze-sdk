from __future__ import annotations
from datetime import datetime

from enum import Enum
from typing import Optional, Sequence, Set, Union

from wyze_sdk.models import JsonObject, PropDef, epoch_to_datetime, show_unknown_key_warning

from .base import (AbstractWirelessNetworkedDevice, SwitchableMixin)


class SwitchProps(object):
    """
    :meta private:
    """

    @classmethod
    def switch_power(cls) -> PropDef:
        return PropDef("switch-power", bool)

    @classmethod
    def switch_iot(cls) -> PropDef:
        return PropDef("switch-iot", bool)

    @classmethod
    def away_mode(cls) -> PropDef:
        return PropDef("vacation_mode", bool, int, [0, 1])

    @classmethod
    def timer_action(cls) -> PropDef:
        return PropDef("timer_action", Sequence)

    @classmethod
    def status_light(cls) -> PropDef:
        return PropDef("led_state", bool)

    @classmethod
    def single_press_type(cls) -> PropDef:
        return PropDef("single_press_type", int)

    @classmethod
    def double_press_type(cls) -> PropDef:
        return PropDef("double_press_type", int)

    @classmethod
    def triple_press_type(cls) -> PropDef:
        return PropDef("triple_press_type", int)

    @classmethod
    def long_press_type(cls) -> PropDef:
        return PropDef("long_press_type", int)

    @classmethod
    def additional_interaction_switch(cls) -> PropDef:
        return PropDef("additional_interaction_switch", bool)

    @classmethod
    def app_version(cls) -> PropDef:
        return PropDef("app_version", str)

    @classmethod
    def wifi_mac(cls) -> PropDef:
        return PropDef("wifi_mac", str)

    @classmethod
    def ssid(cls) -> PropDef:
        return PropDef("ssid", str)

    @classmethod
    def rssi(cls) -> PropDef:
        return PropDef("RSSI", int)

    @classmethod
    def ip(cls) -> PropDef:
        return PropDef("IP", str)

    @classmethod
    def sn(cls) -> PropDef:
        return PropDef("sn", str)


class SwitchTimerActionType(Enum):
    """
    See: com.wyze.mercury.activity.home.MercuryNewMainActivity
    """

    TURN_OFF = ('Turn off', "turn_off")
    TURN_ON = ('Turn on', "turn_on")

    def __init__(self, description: str, code: str):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional[SwitchTimerActionType]:
        for type in list(SwitchTimerActionType):
            if code == type.code:
                return type

    def to_json(self):
        return self.code


class SwitchTimerActionProps(object):
    """
    :meta private:
    """

    @classmethod
    def action(cls) -> PropDef:
        return PropDef("action", SwitchTimerActionType, str)

    @classmethod
    def time(cls) -> PropDef:
        return PropDef("time", datetime, int)


class SwitchTimerAction(JsonObject):
    """
    A timer action for a switch.
    """

    attributes = {
        "action",
        "time",
    }

    def __init__(
        self,
        *,
        action: Union[SwitchTimerActionType, str] = None,
        time: Union[datetime, int] = None,
        **others: dict,
    ):
        if isinstance(action, SwitchTimerActionType):
            self.action = action
        else:
            self.action = SwitchTimerActionType.parse(super()._extract_attribute(SwitchTimerActionProps.action().pid, others))
        if isinstance(time, datetime):
            self.time = time
        else:
            self.time = epoch_to_datetime(super()._extract_attribute(SwitchTimerActionProps.time().pid, others))

    def to_json(self):
        return {
            "action": self.action.to_json(),
            "time": int(self.time.replace(microsecond=0).timestamp())
        }


class Switch(SwitchableMixin, AbstractWirelessNetworkedDevice):

    type = "Switch"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "iot_state",
            "switch_state",
            "away_mode",
            "timer_actions",
            "status_light",
        })

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {
            "iot_state": PropDef("iot_state", str),
            "switch-power": SwitchProps.switch_power(),
            "switch-iot": SwitchProps.switch_iot(),
            "vacation_mode": SwitchProps.away_mode(),
            "timer_action": SwitchProps.timer_action(),
            "led_state": SwitchProps.status_light(),
            "single_press_type": SwitchProps.single_press_type(),
            "double_press_type": SwitchProps.double_press_type(),
            "triple_press_type": SwitchProps.triple_press_type(),
            "long_press_type": SwitchProps.long_press_type(),
            "additional_interaction_switch": SwitchProps.additional_interaction_switch(),
        }

    def __init__(self, **others: dict):
        super().__init__(type=self.type, **others)
        self.switch_state = super()._extract_property(SwitchProps.switch_power(), others)
        self.away_mode = super()._extract_property(SwitchProps.away_mode(), others)
        _timer_action = super()._extract_property(SwitchProps.timer_action(), others)
        if _timer_action is not None:
            self.timer_actions = [SwitchTimerAction(**_action) for _action in _timer_action.value]
        self.status_light = self._extract_property(SwitchProps.status_light(), others)
        show_unknown_key_warning(self, others)
