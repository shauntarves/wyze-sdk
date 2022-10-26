from __future__ import annotations

from enum import Enum
from typing import Sequence, Set, Tuple, Union, Optional

from wyze_sdk.models import JsonObject, PropDef
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice,
                                     DeviceProp, DeviceProps, SwitchableMixin)


class LightControlMode(Enum):
    """
    See: com.hualai.wyze.rgblight.device.h.B and com.hualai.wyze.lslight.device.f
    """

    COLOR = ('Color', 1)
    TEMPERATURE = ('Temperature', 2)
    FRAGMENTED = ('Fragmented', 3)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LightControlMode"]:
        for item in list(LightControlMode):
            if code == item.code:
                return item


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
        for item in list(LightPowerLossRecoveryMode):
            if code == item.code:
                return item


class LightVisualEffectRunType(Enum):
    """
    Additional visual effect run instructions for lights.

    See: com.wyze.commonlight.strip.model.DynamicTypeBean
    """

    DIRECTION_LEFT = ('0', 'Left [ -> ]')
    DIRECTION_DISPERSIVE = ('1', 'Dispersive [<-->]')
    DIRECTION_GATHERED = ('2', 'Gathered [-><-]')

    def __init__(
        self,
        id: str,
        description: str,
    ):
        self.id = id
        self.description = description

    def describe(self):
        return self.description

    def to_json(self):
        return self.id

    @classmethod
    def parse(cls, id: str) -> Optional[LightVisualEffectRunType]:
        for item in list(LightVisualEffectRunType):
            if id == item.id:
                return item

    @classmethod
    def directions(cls) -> Sequence[LightVisualEffectRunType]:
        return [
            LightVisualEffectRunType.DIRECTION_LEFT,
            LightVisualEffectRunType.DIRECTION_DISPERSIVE,
            LightVisualEffectRunType.DIRECTION_GATHERED,
        ]


class LightVisualEffectModel(Enum):
    """
    A preset light/sound effect model for lights.

    See: com.wyze.commonlight.strip.model.DynamicModelBean
    """

    GRADUAL_CHANGE = ('1', 'Shadow')
    JUMP = ('2', 'Leap')
    TWINKLE = ('3', 'Flicker')
    MARQUEE = ('4', 'Marquee', LightVisualEffectRunType.directions())
    COLORFUL = ('5', 'Color Focus', LightVisualEffectRunType.directions())
    RUNNING_WATER = ('6', 'Water', LightVisualEffectRunType.directions())
    SEA_WAVE = ('7', 'Sea Wave', LightVisualEffectRunType.directions())
    METEOR = ('8', 'Shooting Star', LightVisualEffectRunType.directions())
    STARSHINE = ('9', 'Starlight', LightVisualEffectRunType.directions())

    def __init__(
        self,
        id: str,
        description: str,
        run_types: Union[LightVisualEffectRunType, Sequence[LightVisualEffectRunType]] = None
    ):
        self.id = id
        self.description = description
        if run_types is None and not isinstance(run_types, (list, Tuple)):
            run_types = [run_types]
        self.run_types = run_types

    def describe(self):
        return self.description

    def to_json(self):
        return self.id

    @classmethod
    def parse(cls, id: str) -> Optional[LightVisualEffectModel]:
        for item in list(LightVisualEffectModel):
            if id == item.id:
                return item


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
        return PropDef("P1508", int, acceptable_values=[1, 2, 3])

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

    # @classmethod
    # def something1(cls) -> PropDef:
    #     return PropDef("P1511", str)  # UNUSED?

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
        return PropDef("P1522", int, str)

    @classmethod
    def lamp_with_music_type(cls) -> PropDef:
        # sceneRunTypeId
        return PropDef("P1523", int, str)

    @classmethod
    def lamp_with_music_music(cls) -> PropDef:
        # light strip sensitivity (0-100)
        return PropDef("P1524", int, str, acceptable_values=range(0, 101))

    @classmethod
    def lamp_with_music_auto_color(cls) -> PropDef:
        # lampWithMusicAutoColor
        return PropDef("P1525", bool, str, ['0', '1'])

    @classmethod
    def lamp_with_music_color(cls) -> PropDef:
        # this is the color palette under music -> auto-color
        return PropDef("P1526", str)

    # @classmethod
    # def color_palette(cls) -> PropDef:
    #     return PropDef("P1527", bool, int, [0, 1])  # UNUSED?

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
        return PropDef("P1535", bool, str, ['0', '1'])

    @classmethod
    def light_strip_speed(cls) -> PropDef:
        # (1-10)
        return PropDef("P1536", str, acceptable_values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])


class LightVisualEffect(JsonObject):
    """
    A customizable visual/sound effect for lights.

    Visual effects comprise the pre-defined scene model, optional scene run
    instructions, and additional configurable properties.

    An example of this is the water effect, which has a fixed model, a single
    scene run type for the "direction" of the effect, and options like auto-
    color, music mode, etc.
    """

    attributes = {
        "model",
        "rhythm",
        "sensitivity",
        "auto_color",
        "color_palette",
        "mode",
        "speed",
        "run_type",
    }

    def __init__(
        self,
        *,
        model: LightVisualEffectModel,
        rhythm: str = '0',
        music_mode: bool = False,
        sensitivity: int = 100,
        speed: int = 8,
        auto_color: bool = False,
        color_palette: str = '2961AF,B5267A,91FF6A',
        run_type: LightVisualEffectRunType = None,
    ):
        self.model = model
        self.rhythm = rhythm
        self.music_mode = music_mode
        self.sensitivity = sensitivity
        self.speed = speed
        self.auto_color = auto_color
        self.color_palette = color_palette
        self.run_type = run_type

    def to_json(self):
        return map(lambda prop: prop.to_json(), self.to_plist())

    def to_plist(self) -> Sequence[DeviceProp]:
        to_return = [
            DeviceProp(definition=LightProps.lamp_with_music_mode(), value=self.model.id),
            DeviceProp(definition=LightProps.music_mode(), value=self.music_mode),
            DeviceProp(definition=LightProps.light_strip_speed(), value=self.speed),
            DeviceProp(definition=LightProps.lamp_with_music_music(), value=self.sensitivity),
            DeviceProp(definition=LightProps.lamp_with_music_rhythm(), value=self.rhythm),
            DeviceProp(definition=LightProps.lamp_with_music_auto_color(), value=self.auto_color),
            DeviceProp(definition=LightProps.lamp_with_music_color(), value=self.color_palette),
        ]
        if self.run_type is not None:
            to_return.append(DeviceProp(definition=LightProps.lamp_with_music_type(), value=self.run_type.id))
        return to_return


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
