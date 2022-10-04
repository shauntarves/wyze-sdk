from __future__ import annotations

from enum import Enum
from typing import Set, Union, Optional

from wyze_sdk.models import PropDef
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice,
                                     DeviceProp, DeviceProps, SwitchableMixin)


class LightControlMode(Enum):
    """
    See: com.hualai.wyze.rgblight.device.h.B and com.hualai.wyze.lslight.device.f
    """

    COLOR = ('Color', 1)
    TEMPERATURE = ('Temperature', 2)
    # if the bulb is light strip in fragmented control mode, value is 3

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LightControlMode"]:
        for mode in list(LightControlMode):
            if code == mode.code:
                return mode


class LightPowerLossRecoveryMode(Enum):

    POWER_ON = ('Turn the light on', 0)
    RESTORE_PREVIOUS_STATE = ('Maintain previous state', 1)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LightPowerLossRecoveryMode"]:
        for mode in list(LightPowerLossRecoveryMode):
            if code == mode.code:
                return mode


class LightProps(object):
    """
    :meta private:
    """
    # "": PropDef("P1512", ""), # not used
    # "": PropDef("P1513", ""), # not used
    # "": PropDef("P1514", ""), # not used
    # "": PropDef("P1517", ""), # not used
    # "": PropDef("P1518", ""), # not used
    # "": PropDef("P1519", ""), # not used
    # "": PropDef("P1520", ""), # not used
    # "": PropDef("P1521", ""), # not used

    @classmethod
    def brightness(cls) -> PropDef:
        return PropDef("P1501", int, acceptable_values=range(0, 100 + 1))

    @classmethod
    def color_temp(cls) -> PropDef:
        return PropDef("P1502", int, acceptable_values=range(2700, 6500 + 1))

    @classmethod
    def color_temp_mesh(cls) -> PropDef:
        return PropDef("P1502", int, acceptable_values=range(1800, 6500 + 1))

    @classmethod
    def remaining_time(cls) -> PropDef:
        return PropDef("P1505", int)

    @classmethod
    def away_mode(cls) -> PropDef:
        return PropDef("P1506", bool, int, [0, 1])

    @classmethod
    def color(cls) -> PropDef:
        return PropDef("P1507", str)

    @classmethod
    def control_light(cls) -> PropDef:
        return PropDef("P1508", int, acceptable_values=[1, 2])

    @classmethod
    def power_loss_recovery(cls) -> PropDef:
        return PropDef("P1509", int, acceptable_values=[0, 1])

    @classmethod
    def delay_off(cls) -> PropDef:
        return PropDef("P1510", bool, int, [0, 1])

    @classmethod
    def sun_match(cls) -> PropDef:
        return PropDef("P1528", bool, int, [0, 1])

    @classmethod
    def has_location(cls) -> PropDef:
        return PropDef("P1529", bool, int, [0, 1])

    @classmethod
    def supports_sun_match(cls) -> PropDef:
        return PropDef("P1530", bool, int, [0, 1])

    @classmethod
    def supports_timer(cls) -> PropDef:
        return PropDef("P1531", bool, int, [0, 1])


class Light(SwitchableMixin, AbstractWirelessNetworkedDevice):

    type = "Light"

    @property
    def attributes(self) -> Set[str]:
        """
        WLAP19 bulbs (non-mesh, non-color) use the `switch_state` property
        to indicate whethere they are on or off. Newer bulbs appear to
        use some of the same PIDs but also have `open_close_state` and
        `power_switch`.
        """
        return super().attributes.union({
            "switch_state",
            "brightness",
            "color_temp",
            "away_mode",
            "power_loss_recovery",
            "power_loss_recovery_mode",
            "control_mode",
            "has_location",
            "supports_sun_match",
            "sun_match",
            "supports_timer",
            "delay_off",
        })

    def __init__(
        self,
        *,
        type: str = type,
        **others: dict,
    ):
        super().__init__(type=type, **others)
        self.switch_state = self._extract_property(DeviceProps.power_state(), others)
        self.brightness = super()._extract_property(LightProps.brightness(), others)
        self.color_temp = super()._extract_property(LightProps.color_temp(), others)
        self.away_mode = super()._extract_property(LightProps.away_mode(), others)
        self.power_loss_recovery = super()._extract_property(LightProps.power_loss_recovery(), others)
        self.power_loss_recovery_mode = super()._extract_property(LightProps.power_loss_recovery(), others)
        self.control_mode = super()._extract_property(LightProps.control_light(), others)
        self.has_location = super()._extract_property(LightProps.has_location(), others)
        self.supports_sun_match = super()._extract_property(LightProps.supports_sun_match(), others)
        self.sun_match = super()._extract_property(LightProps.sun_match(), others)
        self.supports_timer = super()._extract_property(LightProps.supports_timer(), others)
        self.delay_off = super()._extract_property(LightProps.delay_off(), others)
        # self.remaining_time = super()._extract_property(LightProps.remaining_time(), others)

    @property
    def brightness(self) -> int:
        return 0 if self._brightness is None else self._brightness.value

    @brightness.setter
    def brightness(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.brightness(), value=value)
        self._brightness = value

    @property
    def color_temp(self) -> int:
        return 0 if self._color_temp is None else self._color_temp.value

    @color_temp.setter
    def color_temp(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.color_temp(), value=value)
        self._color_temp = value

    @property
    def away_mode(self) -> bool:
        return False if self._away_mode is None else self._away_mode.value

    @away_mode.setter
    def away_mode(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.away_mode(), value=value)
        self._away_mode = value

    @property
    def power_loss_recovery(self) -> bool:
        return False if self._power_loss_recovery is None else self._power_loss_recovery.value

    @power_loss_recovery.setter
    def power_loss_recovery(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.power_loss_recovery(), value=value)
        self._power_loss_recovery = value

    @property
    def power_loss_recovery_mode(self) -> Optional[LightPowerLossRecoveryMode]:
        return self._power_loss_recovery_mode

    @power_loss_recovery_mode.setter
    def power_loss_recovery_mode(self, value: Union[str, DeviceProp]):
        if value is None:
            return
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.power_loss_recovery(), value=value)
        self._power_loss_recovery_mode = LightPowerLossRecoveryMode.parse(value.value)

    @property
    def control_mode(self) -> Optional[LightControlMode]:
        return self._control_mode

    @control_mode.setter
    def control_mode(self, value: Union[str, DeviceProp]):
        if value is None:
            return
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.control_light(), value=value)
        self._control_mode = LightControlMode.parse(value.value)

    @property
    def sun_match(self) -> bool:
        return False if self._sun_match is None else self._sun_match.value

    @sun_match.setter
    def sun_match(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.sun_match(), value=value)
        self._sun_match = value

    @property
    def has_location(self) -> bool:
        return False if self._has_location is None else self._has_location.value

    @has_location.setter
    def has_location(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.has_location(), value=value)
        self._has_location = value

    @property
    def supports_sun_match(self) -> bool:
        return False if self._supports_sun_match is None else self._supports_sun_match.value

    @supports_sun_match.setter
    def supports_sun_match(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.supports_sun_match(), value=value)
        self._supports_sun_match = value

    @property
    def supports_timer(self) -> bool:
        return False if self._supports_timer is None else self._supports_timer.value

    @supports_timer.setter
    def supports_timer(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.supports_timer(), value=value)
        self._supports_timer = value

    @property
    def delay_off(self) -> bool:
        return False if self._delay_off is None else self._delay_off.value

    @delay_off.setter
    def delay_off(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.delay_off(), value=value)
        self._delay_off = value
