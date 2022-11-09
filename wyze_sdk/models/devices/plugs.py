from __future__ import annotations
from abc import ABCMeta
from datetime import datetime, timedelta
import json
import logging

from typing import Optional, Sequence, Set, Tuple, Union

from wyze_sdk.models import JsonObject, PropDef, epoch_to_datetime, show_unknown_key_warning
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice,
                                     DeviceProp, DeviceProps, SwitchableMixin)


class PlugProps(object):
    """
    :meta private:
    """

    @classmethod
    def status_light(cls) -> PropDef:
        return PropDef("P13", bool)

    @classmethod
    def away_mode(cls) -> PropDef:
        return PropDef("P1614", bool)

    @classmethod
    def rssi(cls) -> PropDef:
        return PropDef("P1612", int)

    @classmethod
    def photosensitive_switch(cls) -> PropDef:
        return PropDef("photosensitive_switch", bool)


class PlugUsageRecord(JsonObject):
    """
    A plug usage record that assumes data represents duration of usage.
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "hourly_data",
            "total_usage",
        }

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        hourly_data: dict[datetime, int] = None,
        **others: dict
    ):
        if hourly_data is not None:
            self.hourly_data = hourly_data
        else:
            _start_datetime = self._extract_attribute('date_ts', others)
            if isinstance(_start_datetime, int):
                _start_datetime = epoch_to_datetime(_start_datetime, ms=True)
            hourly_data = self._extract_attribute('data', others)
            if isinstance(hourly_data, str):
                hourly_data = json.loads(hourly_data)
            if not isinstance(hourly_data, (list, Tuple)):
                hourly_data = list(hourly_data)
            self.hourly_data = {}
            for index, _data in enumerate(hourly_data):
                _hour = _start_datetime + timedelta(hours=index)
                if isinstance(_data, int):
                    self.hourly_data[_hour] = _data
                else:
                    try:
                        self.hourly_data[_hour] = int(_data)
                    except ValueError:
                        self.logger.warning(f"invalid usage record data '{_data}'")
                        self.hourly_data[_hour] = 0
        show_unknown_key_warning(self, others)

    @property
    def total_usage(self) -> Optional[float]:
        """
        Return the total duration of usage, in minutes.
        """
        return None if self.hourly_data is None else sum(self.hourly_data.values()) * 1.0


class PlugElectricityConsumptionRecord(PlugUsageRecord):
    """
    A plug usage record that assumes data represents electricity consumption in watt-hours.
    """

    def __init__(
        self,
        *,
        hourly_data: dict[datetime, int] = None,
        **others: dict
    ):
        super().__init__(hourly_data=hourly_data, **others)

    @property
    def total_usage(self) -> Optional[float]:
        """
        Return the total usage, in kWh.
        """
        return None if super().total_usage is None else super().total_usage / 1000.0


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
        self.switch_state = self._extract_property(DeviceProps.power_state(), others)
        self._switch_state_timer = super()._extract_attribute("switch_state_timer", others)
        self.status_light = self._extract_property(PlugProps.status_light(), others)
        self.away_mode = self._extract_property(PlugProps.away_mode(), others)
        show_unknown_key_warning(self, others)

    @property
    def away_mode(self) -> bool:
        return False if self._away_mode is None else self._away_mode.value

    @away_mode.setter
    def away_mode(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=PlugProps.away_mode(), value=value)
        self._away_mode = value

    @property
    def status_light(self) -> bool:
        return False if self._status_light is None else self._status_light.value

    @status_light.setter
    def status_light(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=PlugProps.status_light(), value=value)
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
                    cls.logger.warning(f"Unknown plug detected ({device})")
                    return Plug(**device)
            else:
                cls.logger.warning(f"Unknown device detected and skipped ({device})")
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
        self.photosensitive_switch = super()._extract_property(PlugProps.photosensitive_switch(), others)
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
            value = DeviceProp(definition=PlugProps.photosensitive_switch(), value=value)
        self._photosensitive_switch = value
