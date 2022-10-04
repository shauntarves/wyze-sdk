from __future__ import annotations

from typing import Optional, Set, Union

from wyze_sdk.models import PropDef, show_unknown_key_warning
from wyze_sdk.models.devices import (DeviceProp, DeviceModels,
                                     LightProps, Light)


class BulbProps(object):
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


class Bulb(Light):

    type = "Light"

    def __init__(
        self,
        *,
        type: str = type,
        **others: dict,
    ):
        super().__init__(type=type, **others)

    @classmethod
    def parse(cls, device: Union[dict, "Bulb"]) -> Optional["Bulb"]:
        if device is None:
            return None
        elif isinstance(device, Bulb):
            return device
        else:
            if "product_type" in device:
                type = device["product_type"]
                if type == Bulb.type:
                    return WhiteBulb(**device) if device["product_model"] in DeviceModels.BULB_WHITE_V2 else Bulb(**device)
                elif type == MeshBulb.type:
                    return MeshBulb(**device)
                else:
                    cls.logger.warning(f"Unknown bulb type detected ({device})")
                    return Bulb(**device)
            else:
                cls.logger.warning(f"Unknown device detected and skipped ({device})")
                return None


class MeshBulb(Bulb):

    type = "MeshLight"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "color",
            "temperature_mode",
            "delay_off",
            "sun_match",
            "has_location",
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.color = super()._extract_property(LightProps.color(), others)
        self.temperature_mode = super()._extract_property(LightProps.temperature_mode(), others)
        self.delay_off = super()._extract_property(LightProps.delay_off(), others)
        self.sun_match = super()._extract_property(LightProps.sun_match(), others)
        self.has_location = super()._extract_property(LightProps.has_location(), others)
        show_unknown_key_warning(self, others)

    @property
    def color(self) -> str:
        return None if self._color is None else self._color.value

    @color.setter
    def color(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=LightProps.color(), value=value)
        self._color = value

    @property
    def temperature_mode(self) -> int:
        return False if self._temperature_mode is None else self._temperature_mode.value

    @temperature_mode.setter
    def temperature_mode(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.temperature_mode(), value=value)
        self._temperature_mode = value

    @property
    def delay_off(self) -> bool:
        return False if self._delay_off is None else self._delay_off.value

    @delay_off.setter
    def delay_off(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.delay_off(), value=value)
        self._delay_off = value

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

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {**Bulb.props(), **{
            "color": LightProps.color(),
            "remaining_time": LightProps.remaining_time(),
            "control_light": LightProps.control_light(),
            "power_loss_recovery": LightProps.power_loss_recovery(),  # remember_off
            "delay_off": LightProps.delay_off(),
        }}


class WhiteBulb(Bulb):

    type = "Light"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "delay_off",
            "sun_match",
            "has_location",
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.delay_off = super()._extract_property(LightProps.delay_off(), others)
        self.sun_match = super()._extract_property(LightProps.sun_match(), others)
        self.has_location = super()._extract_property(LightProps.has_location(), others)
        show_unknown_key_warning(self, others)

    @property
    def delay_off(self) -> bool:
        return False if self._delay_off is None else self._delay_off.value

    @delay_off.setter
    def delay_off(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=LightProps.delay_off(), value=value)
        self._delay_off = value

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

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {**Bulb.props(), **{
            "remaining_time": LightProps.remaining_time(),
            "control_light": LightProps.control_light(),
            "power_loss_recovery": LightProps.power_loss_recovery(),  # remember_off
            "delay_off": LightProps.delay_off(),
        }}
