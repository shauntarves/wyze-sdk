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


class LightStripProps(LightProps):
    """
    :meta private:
    """

    @classmethod
    def something1(cls) -> PropDef:
        return PropDef("P1511", str)

    @classmethod
    def subsection(cls) -> PropDef:
        # 15 14 13 12
        #  8  9 10 11
        #  7  6  5  4
        #  0  1  2  3
        return PropDef("P1515", str)

    @classmethod
    def lamp_with_music_rhythm(cls) -> PropDef:
        # appears to be 0 if not in group, and group id if in group
        # and this seems to set ipPort/aes key
        # see: com.hualai.wyze.lslight.device.f.L
        return PropDef("P1516", str)

    @classmethod
    def lamp_with_music_mode(cls) -> PropDef:
        # sceneRunModelId
        return PropDef("P1522", int)

    @classmethod
    def lamp_with_music_type(cls) -> PropDef:
        # sceneRunTypeId
        return PropDef("P1523", int)

    @classmethod
    def lamp_with_music_music(cls) -> PropDef:
        # light strip sensitivity (0-100)
        return PropDef("P1524", int)

    @classmethod
    def lamp_with_music_auto_color(cls) -> PropDef:
        # lampWithMusicAutoColor
        return PropDef("P1525", bool, int, [0, 1])

    @classmethod
    def lamp_with_music_color(cls) -> PropDef:
        # join?
        # this is the color palette under music -> auto-color
        return PropDef("P1526", str)

    @classmethod
    def color_palette(cls) -> PropDef:
        # this is the swatch list
        return PropDef("P1527", bool, int, [0, 1])

    @classmethod
    def supports_music(cls) -> PropDef:
        return PropDef("P1532", bool, int, [0, 1])

    @classmethod
    def music_port(cls) -> PropDef:
        return PropDef("P1533", str)

    @classmethod
    def music_aes_key(cls) -> PropDef:
        return PropDef("P1534", str)

    @classmethod
    def music_mode(cls) -> PropDef:
        # musicMode
        return PropDef("P1535", str)

    @classmethod
    def light_strip_speed(cls) -> PropDef:
        # (1-10)
        return PropDef("P1536", str)


class LightStrip(BaseBulb):

    type = "LightStrip"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "color",
            "subsection",
            "lamp_with_music_rhythm",
            "lamp_with_music_mode",
            "lamp_with_music_type",
            "lamp_with_music_music",
            "lamp_with_music_auto_color",
            "lamp_with_music_color",
            "color_palette",
            "supports_music",
            "music_port",
            "music_aes_key",
            "music_mode",
            "light_strip_speed",
            "something1",
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.color = super()._extract_property(LightStripProps.color(), others)
        self.subsection = super()._extract_property(LightStripProps.subsection(), others)
        self.lamp_with_music_rhythm = super()._extract_property(LightStripProps.lamp_with_music_rhythm(), others)
        self.lamp_with_music_mode = super()._extract_property(LightStripProps.lamp_with_music_mode(), others)
        self.lamp_with_music_type = super()._extract_property(LightStripProps.lamp_with_music_type(), others)
        self.lamp_with_music_music = super()._extract_property(LightStripProps.lamp_with_music_music(), others)
        self.lamp_with_music_auto_color = super()._extract_property(LightStripProps.lamp_with_music_auto_color(), others)
        self.lamp_with_music_color = super()._extract_property(LightStripProps.lamp_with_music_color(), others)
        self.color_palette = super()._extract_property(LightStripProps.color_palette(), others)
        self.supports_music = super()._extract_property(LightStripProps.supports_music(), others)
        self.music_port = super()._extract_property(LightStripProps.music_port(), others)
        self.music_aes_key = super()._extract_property(LightStripProps.music_aes_key(), others)
        self.music_mode = super()._extract_property(LightStripProps.music_mode(), others)
        self.light_strip_speed = super()._extract_property(LightStripProps.light_strip_speed(), others)
        self.something1 = super()._extract_property(LightStripProps.something1(), others)
        show_unknown_key_warning(self, others)
        # selecting a scene makes individual calls to:
        #  set color/temperature and mode
        #  set brightness

        # choosing water effect
        		# 		"plist": [{
				# 	"pvalue": "6",
				# 	"pid": "P1522"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1535"
				# }, {
				# 	"pvalue": "5",
				# 	"pid": "P1536"
				# }, {
				# 	"pvalue": "100",
				# 	"pid": "P1524"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1525"
				# }, {
				# 	"pvalue": "2961AF,B5267A,91FF6A",
				# 	"pid": "P1526"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1523"
				# }, {
				# 	"pid": "P1508",
				# 	"pvalue": "3"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1516"
				# }]
        # setting speed
        		# 		"plist": [{
				# 	"pid": "P1522",
				# 	"pvalue": "6"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1535"
				# }, {
				# 	"pid": "P1536",
				# 	"pvalue": "8"
				# }, {
				# 	"pid": "P1524",
				# 	"pvalue": "100"
				# }, {
				# 	"pid": "P1525",
				# 	"pvalue": "0"
				# }, {
				# 	"pvalue": "2961AF,B5267A,91FF6A",
				# 	"pid": "P1526"
				# }, {
				# 	"pid": "P1523",
				# 	"pvalue": "0"
				# }, {
				# 	"pid": "P1508",
				# 	"pvalue": "3"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1516"
				# }]
        # setting auto color
        		# 		"plist": [{
				# 	"pvalue": "6",
				# 	"pid": "P1522"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1535"
				# }, {
				# 	"pid": "P1536",
				# 	"pvalue": "8"
				# }, {
				# 	"pvalue": "100",
				# 	"pid": "P1524"
				# }, {
				# 	"pvalue": "1",
				# 	"pid": "P1525"
				# }, {
				# 	"pvalue": "2961AF,B5267A,91FF6A",
				# 	"pid": "P1526"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1523"
				# }, {
				# 	"pvalue": "3",
				# 	"pid": "P1508"
				# }, {
				# 	"pid": "P1516",
				# 	"pvalue": "0"
				# }]
        # setting direction
        		# 		"plist": [{
				# 	"pvalue": "6",
				# 	"pid": "P1522"
				# }, {
				# 	"pid": "P1535",
				# 	"pvalue": "0"
				# }, {
				# 	"pvalue": "8",
				# 	"pid": "P1536"
				# }, {
				# 	"pid": "P1524",
				# 	"pvalue": "100"
				# }, {
				# 	"pvalue": "1",
				# 	"pid": "P1525"
				# }, {
				# 	"pid": "P1526",
				# 	"pvalue": "2961AF,B5267A,91FF6A"
				# }, {
				# 	"pvalue": "2",
				# 	"pid": "P1523"
				# }, {
				# 	"pvalue": "3",
				# 	"pid": "P1508"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1516"
				# }]
        # setting music mode
        		# 		"plist": [{
				# 	"pid": "P1522",
				# 	"pvalue": "6"
				# }, {
				# 	"pid": "P1535",
				# 	"pvalue": "1"
				# }, {
				# 	"pvalue": "8",
				# 	"pid": "P1536"
				# }, {
				# 	"pvalue": "100",
				# 	"pid": "P1524"
				# }, {
				# 	"pid": "P1525",
				# 	"pvalue": "1"
				# }, {
				# 	"pvalue": "2961AF,B5267A,91FF6A",
				# 	"pid": "P1526"
				# }, {
				# 	"pid": "P1523",
				# 	"pvalue": "2"
				# }, {
				# 	"pid": "P1508",
				# 	"pvalue": "3"
				# }, {
				# 	"pvalue": "0",
				# 	"pid": "P1516"
				# }]
        # setting effect "leap"
        		# 		"plist": [{
				# 	"pvalue": "2",
				# 	"pid": "P1522"
				# }, {
				# 	"pid": "P1535",
				# 	"pvalue": "1"
				# }, {
				# 	"pvalue": "8",
				# 	"pid": "P1536"
				# }, {
				# 	"pvalue": "100",
				# 	"pid": "P1524"
				# }, {
				# 	"pid": "P1525",
				# 	"pvalue": "1"
				# }, {
				# 	"pvalue": "2961AF,B5267A,91FF6A",
				# 	"pid": "P1526"
				# }, {
				# 	"pid": "P1523",
				# 	"pvalue": "0"
				# }, {
				# 	"pid": "P1508",
				# 	"pvalue": "3"
				# }, {
				# 	"pid": "P1516",
				# 	"pvalue": "0"
				# }],

    @property
    def color(self) -> str:
        return None if self._color is None else self._color.value

    @color.setter
    def color(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=LightProps.color(), value=value)
        self._color = value
