from typing import (Optional, Set, Union)

from wyze_sdk.models import (PropDef, show_unknown_key_warning)
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice, DeviceProp, DeviceProps, SwitchableMixin)


class BulbProps(object):
    """
    P1503, P1505 are not used
    """

    @classmethod
    @property
    def away_mode(cls) -> PropDef:
        return PropDef("P1506", bool, int, [0, 1])

    @classmethod
    @property
    def power_loss_recovery(cls) -> PropDef:
        return PropDef("P1509", bool, int, [0, 1])

    @classmethod
    @property
    def brightness(cls) -> PropDef:
        return PropDef("P1501", int, acceptable_values=range(0, 100 + 1))

    @classmethod
    @property
    def color_temp(cls) -> PropDef:
        return PropDef("P1502", int, acceptable_values=range(2700, 6500 + 1))

    @classmethod
    @property
    def color(cls) -> PropDef:
        return PropDef("P1507", str)

    @classmethod
    @property
    def remaining_time(cls) -> PropDef:
        return PropDef("P1505", int)

    @classmethod
    @property
    def control_light(cls) -> PropDef:
        return PropDef("P1508", bool, int, [0, 1])

    @classmethod
    @property
    def delay_off(cls) -> PropDef:
        return PropDef("P1510", bool, int, [0, 1])


class Bulb(SwitchableMixin, AbstractWirelessNetworkedDevice):

    type = "Bulb"

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
        self.switch_state = self._extract_property(DeviceProps.power_state, others)
        self.brightness = super()._extract_property(BulbProps.brightness, others)
        self.color_temp = super()._extract_property(BulbProps.color_temp, others)
        self.away_mode = super()._extract_property(BulbProps.away_mode, others)
        self.power_loss_recovery = super()._extract_property(BulbProps.power_loss_recovery, others)
        show_unknown_key_warning(self, others)

    @property
    def brightness(self) -> int:
        return 0 if self._brightness is None else self._brightness.value

    @brightness.setter
    def brightness(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=BulbProps.brightness, value=value)
        self._brightness = value

    @property
    def color_temp(self) -> int:
        return 0 if self._color_temp is None else self._color_temp.value

    @color_temp.setter
    def color_temp(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=BulbProps.color_temp, value=value)
        self._color_temp = value

    @property
    def away_mode(self) -> bool:
        return False if self._away_mode is None else self._away_mode.value

    @away_mode.setter
    def away_mode(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=BulbProps.away_mode, value=value)
        self._away_mode = value

    @property
    def power_loss_recovery(self) -> bool:
        return False if self._power_loss_recovery is None else self._power_loss_recovery.value

    @power_loss_recovery.setter
    def power_loss_recovery(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=BulbProps.power_loss_recovery, value=value)
        self._power_loss_recovery = value

    @classmethod
    def parse(cls, device: Union[dict, "Bulb"]) -> Optional["Bulb"]:
        if device is None:  # skipcq: PYL-R1705
            return None
        elif isinstance(device, Bulb):
            return device
        else:
            if "product_type" in device:
                type = device["product_type"]  # skipcq: PYL-W0622
                if type == Bulb.type:  # skipcq: PYL-R1705
                    return Bulb(**device)
                elif type == MeshBulb.type:  # skipcq: PYL-R1705
                    return MeshBulb(**device)
                else:
                    cls.logger.warning(f"Unknown bulb detected and skipped ({device})")
                    return None
            else:
                cls.logger.warning(f"Unknown bulb detected and skipped ({device})")
                return None


class MeshBulb(Bulb):

    type = "MeshLight"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "color"
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.color = super()._extract_property(BulbProps.color, others)
        show_unknown_key_warning(self, others)

    @property
    def color(self) -> str:
        return "" if self._color is None else self._color.value

    @color.setter
    def color(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=BulbProps.color, value=value)
        self._color = value

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {**Bulb.props(), **{
            "color": BulbProps.color,
            "remaining_time": BulbProps.remaining_time,
            "control_light": BulbProps.control_light,
            "power_loss_recovery": BulbProps.power_loss_recovery,  # remember_off
            "delay_off": BulbProps.delay_off,
        }}
