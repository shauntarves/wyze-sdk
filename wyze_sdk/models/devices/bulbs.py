from __future__ import annotations

from typing import Optional, Sequence, Set, Union

from wyze_sdk.models import PropDef, show_unknown_key_warning
from wyze_sdk.models.devices import (DeviceProp, DeviceModels,
                                     LightProps, Light)
from wyze_sdk.models.devices.lights import LightControlMode, LightVisualEffectModel, LightVisualEffectRunType


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
                elif type == LightStrip.type:
                    return LightStrip(**device)
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


class LightStrip(BaseBulb):

    type = "LightStrip"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "color",
            "subsection",
            "supports_music",
            "lamp_with_music_rhythm",
            "effect_model",
            "music_mode",
            "sensitivity",
            "speed",
            "auto_color",
            "color_palette",
            "effect_run_type",
            "music_port",
            "music_aes_key",
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.color = super()._extract_property(LightProps.color(), others)
        self.subsection = super()._extract_property(LightProps.subsection(), others)
        self.supports_music = super()._extract_property(LightProps.supports_music(), others)
        self.lamp_with_music_rhythm = super()._extract_property(LightProps.lamp_with_music_rhythm(), others)
        self.effect_model = super()._extract_property(LightProps.lamp_with_music_mode(), others)
        self.music_mode = super()._extract_property(LightProps.music_mode(), others)
        self.sensitivity = super()._extract_property(LightProps.lamp_with_music_music(), others)
        self.speed = super()._extract_property(LightProps.light_strip_speed(), others)
        self.auto_color = super()._extract_property(LightProps.lamp_with_music_auto_color(), others)
        self.color_palette = super()._extract_property(LightProps.lamp_with_music_color(), others)
        self.effect_run_type = super()._extract_property(LightProps.lamp_with_music_type(), others)
        self.music_port = super()._extract_property(LightProps.music_port(), others)
        self.music_aes_key = super()._extract_property(LightProps.music_aes_key(), others)
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
    def subsection(self) -> Optional[Sequence[str]]:
        if self._subsection is None or self._subsection.value.strip() == '':
            return None
        return list(map(lambda color: color[-6:], self._subsection.value.strip().split('#')))

    @subsection.setter
    def subsection(self, value: Union[str, DeviceProp]):
        if isinstance(value, LightProps.subsection().type):
            value = DeviceProp(definition=LightProps.subsection(), value=value)
        self._subsection = value

    @property
    def sensitivity(self) -> int:
        return None if self._sensitivity is None else self._sensitivity.value

    @sensitivity.setter
    def sensitivity(self, value: Union[int, DeviceProp]):
        if isinstance(value, LightProps.lamp_with_music_music().type):
            value = DeviceProp(definition=LightProps.lamp_with_music_music(), value=value)
        self._sensitivity = value

    @property
    def speed(self) -> int:
        return None if self._speed is None else self._speed.value

    @speed.setter
    def speed(self, value: Union[int, DeviceProp]):
        if isinstance(value, LightProps.light_strip_speed().type):
            value = DeviceProp(definition=LightProps.light_strip_speed(), value=value)
        self._speed = value

    @property
    def supports_music(self) -> bool:
        return None if self._supports_music is None else self._supports_music.value

    @supports_music.setter
    def supports_music(self, value: Union[bool, DeviceProp]):
        if isinstance(value, LightProps.supports_music().type):
            value = DeviceProp(definition=LightProps.supports_music(), value=value)
        self._supports_music = value

    @property
    def effect_model(self) -> LightVisualEffectModel:
        return None if self._effect_model is None else LightVisualEffectModel.parse(str(self._effect_model.value))

    @effect_model.setter
    def effect_model(self, value: Union[LightVisualEffectModel, DeviceProp]):
        if isinstance(value, LightVisualEffectModel):
            value = DeviceProp(definition=LightProps.lamp_with_music_mode(), value=value.id)
        self._effect_model = value

    @property
    def effect_run_type(self) -> LightVisualEffectRunType:
        return None if self._effect_run_type is None else LightVisualEffectRunType.parse(str(self._effect_run_type.value))

    @effect_run_type.setter
    def effect_run_type(self, value: Union[LightVisualEffectRunType, DeviceProp]):
        if isinstance(value, LightVisualEffectRunType):
            value = DeviceProp(definition=LightProps.lamp_with_music_type(), value=value.id)
        self._effect_run_type = value

    @property
    def music_mode(self) -> bool:
        return None if self._music_mode is None else self._music_mode.value

    @music_mode.setter
    def music_mode(self, value: Union[bool, DeviceProp]):
        if isinstance(value, LightProps.music_mode().type):
            value = DeviceProp(definition=LightProps.music_mode(), value=value)
        self._music_mode = value

    @property
    def auto_color(self) -> bool:
        return None if self._auto_color is None else self._auto_color.value

    @auto_color.setter
    def auto_color(self, value: Union[bool, DeviceProp]):
        if isinstance(value, LightProps.lamp_with_music_auto_color().type):
            value = DeviceProp(definition=LightProps.lamp_with_music_auto_color(), value=value)
        self._auto_color = value

    @property
    def color_palette(self) -> str:
        return None if self._color_palette is None else self._color_palette.value

    @color_palette.setter
    def color_palette(self, value: Union[str, DeviceProp]):
        if isinstance(value, LightProps.lamp_with_music_color().type):
            value = DeviceProp(definition=LightProps.lamp_with_music_color(), value=value)
        self._color_palette = value

    @property
    def music_port(self) -> str:
        return None if self._music_port is None else self._music_port.value

    @music_port.setter
    def music_port(self, value: Union[str, DeviceProp]):
        if isinstance(value, LightProps.music_port().type):
            value = DeviceProp(definition=LightProps.music_port(), value=value)
        self._music_port = value

    @property
    def music_aes_key(self) -> str:
        return None if self._music_aes_key is None else self._music_aes_key.value

    @music_aes_key.setter
    def music_aes_key(self, value: Union[str, DeviceProp]):
        if isinstance(value, LightProps.music_aes_key().type):
            value = DeviceProp(definition=LightProps.music_aes_key(), value=value)
        self._music_aes_key = value
