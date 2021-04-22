from typing import (Optional, Set, Union)

from wyze_sdk.models import (PropDef, show_unknown_key_warning)
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice, DeviceProp, DeviceProps, SwitchableMixin)


class PlugProps(object):

    @classmethod
    @property
    def status_light(cls) -> PropDef:
        return PropDef("P13", bool)

    @classmethod
    @property
    def away_mode(cls) -> PropDef:
        return PropDef("P1614", bool)

    @classmethod
    @property
    def rssi(cls) -> PropDef:
        return PropDef("P1612", int)

    @classmethod
    @property
    def photosensitive_switch(cls) -> PropDef:
        return PropDef("photosensitive_switch", bool)


class Plug(SwitchableMixin, AbstractWirelessNetworkedDevice):

    type = "Plug"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "switch_state_timer",
        })

    def __init__(
        self,
        type: str = type,
        **others: dict,
    ):
        super().__init__(type=type, **others)
        self.switch_state = self._extract_property(DeviceProps.power_state, others)
        self._switch_state_timer = super()._extract_attribute("switch_state_timer", others)
        self.status_light = self._extract_property(PlugProps.status_light, others)
        self.away_mode = self._extract_property(PlugProps.away_mode, others)
        show_unknown_key_warning(self, others)

    @property
    def away_mode(self) -> bool:
        return False if self._away_mode is None else self._away_mode.value

    @away_mode.setter
    def away_mode(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=PlugProps.away_mode, value=value)
        self._away_mode = value

    @property
    def status_light(self) -> bool:
        return False if self._status_light is None else self._status_light.value

    @status_light.setter
    def status_light(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=PlugProps.status_light, value=value)
        self._status_light = value

    @classmethod
    def parse(cls, device: Union[dict, "Plug"]) -> Optional["Plug"]:
        if device is None:
            return None
        elif isinstance(device, Plug):
            return device
        else:
            if "product_type" in device:
                type = device["product_type"]
                if type == Plug.type:
                    return Plug(**device)
                elif type == OutdoorPlug.type:
                    return OutdoorPlug(**device)
                else:
                    cls.logger.warning(f"Unknown plug detected and skipped ({device})")
                    return None
            else:
                cls.logger.warning(f"Unknown plug detected and skipped ({device})")
                return None


class OutdoorPlug(Plug):

    type = "OutdoorPlug"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "photosensitive_switch"
        })

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.photosensitive_switch = super()._extract_property(PlugProps.photosensitive_switch, others)
        show_unknown_key_warning(self, others)

    @property
    def is_photosensitive(self) -> bool:
        return self.photosensitive_switch

    @property
    def photosensitive_switch(self) -> bool:
        return False if self._photosensitive_switch is None else self._photosensitive_switch.value

    @photosensitive_switch.setter
    def photosensitive_switch(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=PlugProps.photosensitive_switch, value=value)
        self._photosensitive_switch = value
