import distutils.util
import logging
from abc import ABCMeta
from datetime import datetime
from typing import Any, Optional, Sequence, Set, Union

from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime)

# -------------------------------------------------
# Base Classes
# -------------------------------------------------


class DeviceModels(object):
    """
    Defines the model-to-device type mapping for the Wyze service provider.

    See: com.wyze.platformkit.component.service.camplus.utils.WpkModelConfig
         com.HLApi.Obj.BindableDevice
    """

    CAMERA_V1 = ['WYZEC1']
    CAMERA_V2 = ['WYZEC1-JZ']
    CAMERA_V3 = ['WYZE_CAKP2JFUS']

    LOCK = ['YD.LO1']
    LOCK_GATEWAY = ['YD.GW1']
    THERMOSTAT = ['CO_EA1']
    CONTACT_SENSOR = ['DWS3U']
    MOTION_SENSOR = ['PIR3U']
    VACUUM = ['JA_RO2']
    CAMERA = CAMERA_V1 + CAMERA_V2 + CAMERA_V3
    SCALE = ['JA.SC', 'JA.SC2']
    WATCH = ['RA.WP1', 'RY.WA1']
    BAND = ['RY.HP1']
    OUTDOOR_PLUG = ['WLPPO-SUB']
    MESH_BULB = ['WLPA19C']
    PLUG = ['WLPP1', 'WLPP1CFH'] + OUTDOOR_PLUG
    BULB = ['WLPA19'] + MESH_BULB


class Product(object):
    """
    The product information for a Wyze-branded device.
    """

    attributes = {
        "type",
        "model",
        "logo_url",
    }

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        model: Optional[str] = None,
        logo_url: Optional[str] = None
    ):
        self._type = type
        self._model = model
        self._logo_url = logo_url

    @property
    def type(self) -> str:
        return self._type

    @property
    def model(self) -> str:
        return self._model

    @property
    def logo_url(self) -> str:
        return self._logo_url


class Timezone(object):
    """
    The timezone data associated with a device.
    """

    def __init__(
        self,
        *,
        offset: Optional[str] = None,
        name: Optional[str] = None
    ):
        self._offset = offset
        self._name = name

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def name(self) -> str:
        return self._name


class DeviceProp(object):
    """
    A wrapper for any type of singular device attribute and its definition.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        definition: PropDef,
        ts: Optional[int] = None,
        value: Any = None,
        **kwargs,
    ):
        self._definition = definition
        if isinstance(ts, datetime):
            self._ts = ts
        elif ts is not None:
            self._ts = epoch_to_datetime(ts, ms=True)
        if value is not None and not isinstance(value, definition.type):
            try:
                value = bool(distutils.util.strtobool(str(value))) if definition.type == bool else definition._type(value)
            except ValueError:
                self.logger.warning(f"could not cast value `{value}` into expected type {definition.type}")
        self._value = value

    @property
    def definition(self) -> PropDef:
        return self._definition

    @property
    def ts(self) -> datetime:
        return self._ts

    @ts.setter
    def ts(self, value: Union[str, int, datetime]) -> datetime:
        if isinstance(value, str):
            try:
                value = int(str)
            except ValueError:
                self.logger.warning(f"could not cast value `{value}` into timestamp")
                return
            value = epoch_to_datetime(value, ms=True)
        if isinstance(value, int):
            value = epoch_to_datetime(value, ms=True)
        self._ts = value

    @property
    def value(self) -> Any:
        return self._value

    @property
    def api_value(self) -> Any:
        if self.definition.api_type is None:
            self.logger.debug(f"unknown api type, returning {self.value} unchanged")
            return self.value
        # bools are weird - isinstance(bool, int) returns true
        if self.definition.type == bool:
            if self.definition.api_type == int:
                self.logger.debug(f"returning boolean value {self.value} as int")
                return int(self.value)
            elif self.definition.api_type == str:
                self.logger.debug(f"returning boolean value {self.value} as str")
                return str(int(self.value))
        if isinstance(self.value, self.definition.api_type):
            self.logger.debug(f"value {self.value} is already of configured api type {self.definition.api_type}, returning unchanged")
            return self.value
        try:
            self.logger.debug(f"value {self.value} is type {self.definition.type}, attempting to convert to {self.definition.api_type}")
            return self.definition.api_type(self.value)
        except ValueError:
            self.logger.warning(f"could not cast value `{self.value}` into expected api type {self.definition.api_type}")


class DeviceProps(object):

    @classmethod
    @property
    def push_notifications_enabled(cls) -> PropDef:
        return PropDef("P1", bool, int, [0, 1])

    @classmethod
    @property
    def power_state(cls) -> PropDef:
        return PropDef("P3", bool, int, [0, 1])

    @classmethod
    @property
    def online_state(cls) -> PropDef:
        return PropDef("P5", bool, int, [0, 1])


class Device(JsonObject):

    attributes = {
        "binding_ts",
        "binding_user_nickname",
        "conn_state",
        "conn_state_ts",
        "enr",
        "event_master_switch",
        "firmware_ver",
        "first_activation_ts",
        "first_binding_ts",
        "hardware_ver",
        "is_in_auto",
        "mac",
        "nickname",
        "p2p_id",
        "p2p_type",
        "parent_device_enr",
        "parent_device_mac",
        "product_model",
        "product_type",
        "push_switch",
        "timezone_gmt_offset",
        "timezone_name",
        "type",
        "user_role",
    }
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        binding_ts: Optional[int] = None,
        binding_user_nickname: Optional[str] = None,
        conn_state: Optional[int] = None,
        conn_state_ts: Optional[int] = None,
        enr: Optional[str] = None,
        event_master_switch: Optional[int] = None,
        firmware_ver: Optional[str] = None,
        first_activation_ts: Optional[int] = None,
        first_binding_ts: Optional[int] = None,
        hardware_ver: Optional[str] = None,
        is_in_auto: Optional[int] = None,
        mac: Optional[str] = None,
        nickname: Optional[str] = None,
        parent_device_mac: Optional[str] = None,
        parent_device_enr: Optional[str] = None,
        product_model: Optional[str] = None,
        product_model_logo_url: Optional[str] = None,
        product_type: Optional[str] = None,
        push_switch: Optional[int] = None,
        timezone_gmt_offset: Optional[float] = None,
        timezone_name: Optional[str] = None,
        user_role: Optional[int] = None,
        type: Optional[str] = None,
        **others: dict,
    ):
        self._type = type if type is not None else self._extract_attribute('product_type', others)
        self._mac = mac
        self._nickname = nickname
        if conn_state is not None and conn_state_ts is not None:
            self._is_online = DeviceProp(definition=DeviceProps.online_state, value=conn_state, ts=conn_state_ts)
        else:
            self._is_online = self._extract_property(DeviceProps.online_state, others)
        self._enr = enr
        self._push_switch = push_switch
        self._firmware_version = firmware_ver if firmware_ver is not None else self._extract_attribute('firmware_ver', others)
        self._hardware_version = hardware_ver if hardware_ver is not None else self._extract_attribute('hardware_ver', others)
        if parent_device_mac is not None:
            self._parent_device = {"mac": parent_device_mac, "enr": parent_device_enr}
        self._product = Product(**{
            "logo_url": product_model_logo_url if product_model_logo_url is not None else self._extract_attribute('product_model_logo_url', others),
            "model": product_model if product_model is not None else self._extract_attribute('product_model', others),
            "type": product_type if product_type is not None else self._extract_attribute('product_type', others),
        })
        self._timezone = Timezone(**{
            "offset": timezone_gmt_offset if timezone_gmt_offset is not None else self._extract_attribute('timezone_gmt_offset', others),
            "name": timezone_name if timezone_name is not None else self._extract_attribute('timezone_name', others),
        })
        self._user_role = user_role

    @property
    def mac(self) -> str:
        return self._mac

    @property
    def type(self) -> str:
        return self._type

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def enr(self) -> str:
        return self._enr

    @property
    def push_switch(self) -> bool:
        return self._push_switch

    @property
    def hardware_version(self) -> str:
        return self._hardware_version

    @property
    def firmware_version(self) -> str:
        return self._firmware_version

    @property
    def parent_device(self) -> dict:
        return self._parent_device

    @property
    def product(self) -> Product:
        return self._product

    @property
    def timezone(self) -> Timezone:
        return self._timezone

    @property
    def is_online(self) -> bool:
        return False if self._is_online is None else self._is_online.value

    def _extract_property(self, prop_def: Union[str, PropDef], others: Union[dict, Sequence[dict]]) -> DeviceProp:
        if isinstance(prop_def, str):
            prop_def = PropDef(pid=prop_def)

        if isinstance(others, dict):
            if 'data' in others and 'property_list' in others['data']:
                return self._extract_property(prop_def=prop_def, others=others['data'])
            if 'props' in others:
                return self._extract_property(prop_def=prop_def, others=others['props'])
            if 'property_list' in others:
                return self._extract_property(prop_def=prop_def, others=others['property_list'])
            self.logger.debug(prop_def.pid)
            for key, value in others.items():
                self.logger.debug(f"key: {key}, value: {value}")
                if key == prop_def.pid:
                    self.logger.debug(f"returning new DeviceProp with value {value}")
                    return DeviceProp(definition=prop_def, value=value)
        else:
            for value in others:
                self.logger.debug(f"value {value}")
                if "pid" in value and prop_def.pid == value["pid"]:
                    self.logger.debug(f"returning new DeviceProp with {value}")
                    return DeviceProp(definition=prop_def, **value)


class AbstractNetworkedDevice(Device, metaclass=ABCMeta):

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "ip",
        })

    def __init__(
        self,
        *,
        type: str,
        ip: Optional[str] = None,
        **others: dict,
    ):
        super().__init__(type=type, **others)
        self._ip = ip if ip else super()._extract_attribute('ip', others)

    @property
    def ip(self) -> str:
        return self._ip


class AbstractWirelessNetworkedDevice(AbstractNetworkedDevice, metaclass=ABCMeta):

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "rssi",
            "ssid",
        })

    def __init__(
        self,
        *,
        type: str,
        rssi: Optional[int] = None,
        ssid: Optional[str] = None,
        **others: dict,
    ):
        super().__init__(type=type, **others)
        self._rssi = rssi if rssi else super()._extract_attribute('rssi', others)
        self._ssid = ssid if ssid else super()._extract_attribute('ssid', others)

    @property
    def rssi(self) -> str:
        return self._rssi

    @property
    def ssid(self) -> str:
        return self._ssid


# -------------------------------------------------
# Mixins
# -------------------------------------------------


class VoltageMixin(metaclass=ABCMeta):
    """
    A mixin for devices that measure voltage.
    """

    @property
    def voltage(self) -> int:
        return None if self._voltage is None else self._voltage.value

    @voltage.setter
    def voltage(self, value: DeviceProp):
        self._voltage = value


class ClimateMixin(metaclass=ABCMeta):
    """
    A mixin for devices that track temperature and humidity.
    """

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def humidity(self) -> float:
        return self._humidity


class MotionMixin(metaclass=ABCMeta):
    """
    A mixin for devices that sense motion.
    """

    @property
    def has_motion(self) -> bool:
        return self.motion_state

    @property
    def motion_state(self) -> bool:
        return False if self._motion_state is None else self._motion_state.value

    @motion_state.setter
    def motion_state(self, value: DeviceProp):
        self._motion_state = value


class ContactMixin(metaclass=ABCMeta):
    """
    A mixin for devices that sense contact.
    """

    @property
    def is_open(self) -> bool:
        return self.open_close_state

    @property
    def open_close_state(self) -> bool:
        return False if self._open_close_state is None else self._open_close_state.value

    @open_close_state.setter
    def open_close_state(self, value: DeviceProp):
        self._open_close_state = value


class LockableMixin(metaclass=ABCMeta):
    """
    A mixin for devices that can be locked.
    """

    @property
    def is_locked(self) -> bool:
        return self.lock_state

    @property
    def lock_state(self) -> bool:
        return False if self._lock_state is None else self._lock_state.value

    @lock_state.setter
    def lock_state(self, value: DeviceProp):
        self._lock_state = value


class SwitchableMixin(metaclass=ABCMeta):
    """
    A mixin for devices that can be switched.
    """

    @property
    def is_on(self) -> bool:
        return False if self.switch_state is None else self.switch_state.value

    @property
    def switch_state(self) -> DeviceProp:
        return self._switch_state

    @switch_state.setter
    def switch_state(self, value: DeviceProp):
        self._switch_state = value
