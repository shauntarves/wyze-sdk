from __future__ import annotations

from typing import Set, Union

from wyze_sdk.models import PropDef
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice,
                                     DeviceProp, DeviceProps, SwitchableMixin)


class LightProps(object):
    """
    :meta private:
    """

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
    def temperature_mode(cls) -> PropDef:
        return PropDef("P1503", int, acceptable_values=[0, 1])

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
        # if the bulb is in color mode, value is 1
        # if the bulb is in temperature mode, value is 2
        # see: com.hualai.wyze.rgblight.device.h.B
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
