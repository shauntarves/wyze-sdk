from __future__ import annotations

from typing import Optional, Set, Union

from wyze_sdk.models import PropDef, show_unknown_key_warning
from wyze_sdk.models.devices import (DeviceProp, DeviceModels,
                                     LightProps, Light)


class BulbProps(object):
    """
    :meta private:
    """

    @classmethod
    def brightness(cls) -> PropDef:
        return LightProps.brightness()

    @classmethod
    def color_temp(cls) -> PropDef:
        return LightProps.color_temp()

    @classmethod
    def color_temp_mesh(cls) -> PropDef:
        return LightProps.color_temp_mesh()

    @classmethod
    def remaining_time(cls) -> PropDef:
        return LightProps.remaining_time()

    @classmethod
    def away_mode(cls) -> PropDef:
        return LightProps.away_mode()

    @classmethod
    def color(cls) -> PropDef:
        return LightProps.color()

    @classmethod
    def control_light(cls) -> PropDef:
        return LightProps.control_light()

    @classmethod
    def power_loss_recovery(cls) -> PropDef:
        return LightProps.power_loss_recovery()

    @classmethod
    def delay_off(cls) -> PropDef:
        return LightProps.delay_off()


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
