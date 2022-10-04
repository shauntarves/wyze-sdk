from __future__ import annotations

from typing import Optional, Set, Union

from wyze_sdk.models import PropDef, show_unknown_key_warning
from wyze_sdk.models.devices import (DeviceProp, DeviceModels,
                                     LightProps, Light)
from wyze_sdk.models.devices.lights import LightControlMode


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


class BaseBulb(Light):

    def __init__(
        self,
        *,
        type: str = type,
        **others: dict,
    ):
        super().__init__(type=type, **others)

    @classmethod
    def parse(cls, device: Union[dict, "BaseBulb"]) -> Optional["BaseBulb"]:
        if device is None:
            return None
        elif isinstance(device, BaseBulb):
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


class Bulb(BaseBulb):

    def __init__(
        self,
        *,
        type: str = type,
        **others: dict,
    ):
        super().__init__(type=type, **others)
        self._control_mode = LightControlMode.TEMPERATURE
        show_unknown_key_warning(self, others)


class WhiteBulb(Bulb):

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        show_unknown_key_warning(self, others)


class MeshBulb(BaseBulb):

    type = "MeshLight"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "color",
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.color = super()._extract_property(LightProps.color(), others)
        show_unknown_key_warning(self, others)

    @property
    def color(self) -> str:
        return None if self._color is None else self._color.value

    @color.setter
    def color(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=LightProps.color(), value=value)
        self._color = value
