from enum import Enum
from typing import (Optional, Set, Union)

from wyze_sdk.models import (PropDef, show_unknown_key_warning)

from .base import (AbstractWirelessNetworkedDevice, ClimateMixin, DeviceProp, LockableMixin)


class ThermostatProps(object):

    @classmethod
    @property
    def temperature(cls) -> PropDef:
        return PropDef("temperature", float)

    @classmethod
    @property
    def time_to_temp(cls) -> PropDef:
        return PropDef("time2temp_val", int)  # in minutes

    @classmethod
    @property
    def humidity(cls) -> PropDef:
        return PropDef("humidity", int)

    @classmethod
    @property
    def fan_mode(cls) -> PropDef:
        return PropDef("fan_mode", str)

    @classmethod
    @property
    def system_mode(cls) -> PropDef:
        return PropDef("mode_sys", str)

    @classmethod
    @property
    def locked(cls) -> PropDef:
        return PropDef("kid_lock", bool, str, ['0', '1'])

    @classmethod
    @property
    def heating_setpoint(cls) -> PropDef:
        return PropDef("heat_sp", int, str)

    @classmethod
    @property
    def cooling_setpoint(cls) -> PropDef:
        return PropDef("cool_sp", int, str)

    @classmethod
    @property
    def current_scenario(cls) -> PropDef:
        return PropDef("current_scenario", str)

    @classmethod
    @property
    def working_state(cls) -> PropDef:
        return PropDef("working_state", str)

    @classmethod
    @property
    def auto_switch(cls) -> PropDef:
        return PropDef("auto_switch_mode", int)

    @classmethod
    @property
    def temperature_unit(cls) -> PropDef:
        return PropDef("temp_unit", str, acceptable_values=['F', 'C'])


class ThermostatFanMode(Enum):
    """
    See: com.wyze.earth.common.widget.EarthHomeControls
    """

    AUTO = ('Auto', "auto")
    CYCLE = ('Cycle', "circ")
    ON = ('On', "on")

    def __init__(self, description: str, codes: str):
        self.description = description
        self.codes = codes

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional["ThermostatFanMode"]:
        for mode in list(ThermostatFanMode):
            if code == mode.codes:
                return mode


class ThermostatSystemMode(Enum):
    """
    See: com.wyze.earth.common.widget.EarthHomeControls
    """

    AUTO = ('Auto', "auto")
    COOL = ('Cool', "cool")
    HEAT = ('Heat', "heat")
    OFF = ('Off', "off")

    def __init__(self, description: str, codes: str):
        self.description = description
        self.codes = codes

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional["ThermostatSystemMode"]:
        for mode in list(ThermostatSystemMode):
            if code == mode.codes:
                return mode


class ThermostatScenarioType(Enum):
    """
    See: com.wyze.earth.activity.home.EarthMainActivity
    """

    AWAY = ('Away', "away")
    HOME = ('Home', "home")
    SLEEP = ('Sleep', "sleep")

    def __init__(self, description: str, codes: str):
        self.description = description
        self.codes = codes

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional["ThermostatScenarioType"]:
        for mode in list(ThermostatScenarioType):
            if code == mode.codes:
                return mode


class Thermostat(ClimateMixin, LockableMixin, AbstractWirelessNetworkedDevice):
    type = "Thermostat"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(Thermostat.props().keys()).union(Thermostat.device_info_props().keys())

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {
            "trigger_off_val": PropDef("trigger_off_val", int),
            "emheat": PropDef("emheat", int),
            "temperature": ThermostatProps.temperature,
            "humidity": ThermostatProps.humidity,
            "time2temp_val": ThermostatProps.time_to_temp,
            "protect_time": PropDef("protect_time", str),
            "system_mode": ThermostatProps.system_mode,
            "heating_setpoint": ThermostatProps.heating_setpoint,
            "cooling_setpoint": ThermostatProps.cooling_setpoint,
            "current_scenario": ThermostatProps.current_scenario,
            "config_scenario": PropDef("config_scenario", dict),
            "temp_unit": ThermostatProps.temperature_unit,
            "fan_mode": ThermostatProps.fan_mode,
            "iot_state": PropDef("iot_state", str),
            "w_city_id": PropDef("w_city_id", int),
            "w_lat": PropDef("w_lat", int),
            "w_lon": PropDef("w_lon", int),
            "working_state": ThermostatProps.working_state,
            "device_hold": PropDef("dev_hold", int),
            "device_hold_time": PropDef("dev_holdtime", int),
            "asw_hold": PropDef("asw_hold", int),
            "app_version": PropDef("app_version", int),
            "setup_state": PropDef("setup_state", int),
            "wiring_logic_id": PropDef("wiring_logic_id", int),
            "save_comfort_balance": PropDef("save_comfort_balance", int),
            "locked": ThermostatProps.locked,
            "calibrate_humidity": PropDef("calibrate_humidity", str),
            "calibrate_temperature": PropDef("calibrate_temperature", str),
            "fancirc_time": PropDef("fancirc_time", str),
            "query_schedule": PropDef("query_schedule", str),
        }

    @classmethod
    def device_info_props(cls) -> dict[str, PropDef]:
        return {
            "auto_switch_mode": ThermostatProps.auto_switch,
            "setup_is_have_cadapter": PropDef("setup_is_have_cadapter", str),
            "setup_personalization_state": PropDef("setup_personalization_state", str),
            "setup_step": PropDef("setup_step", str),
            "setup_test_state": PropDef("setup_test_state", str),
            "setup_wires": PropDef("setup_wires", dict),
            "plugin_version": PropDef("plugin_version", str),
            "terminal_type": PropDef("terminal_type", str),
        }

    def __init__(self, **others: dict):
        super().__init__(type=self.type, **others)
        self._humidity = super()._extract_attribute(ThermostatProps.humidity.pid, others)
        self._temperature = super()._extract_attribute(ThermostatProps.temperature.pid, others)
        self._cooling_setpoint = super()._extract_attribute(ThermostatProps.cooling_setpoint.pid, others)
        self._heating_setpoint = super()._extract_attribute(ThermostatProps.heating_setpoint.pid, others)
        self.fan_mode = super()._extract_property(ThermostatProps.fan_mode, others)
        self.system_mode = super()._extract_property(ThermostatProps.system_mode, others)
        self.working_state = super()._extract_attribute(ThermostatProps.working_state.pid, others)
        self.auto_switch_mode = super()._extract_attribute(ThermostatProps.auto_switch.pid, others)
        self.lock_state = super()._extract_property(ThermostatProps.locked, others)
        self._temperature_unit = super()._extract_attribute(ThermostatProps.temperature_unit.pid, others)
        self.current_scenario = super()._extract_property(ThermostatProps.current_scenario, others)
        show_unknown_key_warning(self, others)

    @property
    def temperature_unit(self) -> str:
        return self._temperature_unit

    @property
    def fan_mode(self) -> ThermostatFanMode:
        return self._fan_mode

    @fan_mode.setter
    def fan_mode(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=ThermostatProps.fan_mode, value=value)
        self._fan_mode = ThermostatFanMode.parse(value.value)

    @property
    def system_mode(self) -> ThermostatSystemMode:
        return self._system_mode

    @system_mode.setter
    def system_mode(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=ThermostatProps.system_mode, value=value)
        self._system_mode = ThermostatSystemMode.parse(value.value)

    @property
    def current_scenario(self) -> ThermostatScenarioType:
        return self._current_scenario

    @current_scenario.setter
    def current_scenario(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=ThermostatProps.current_scenario, value=value)
        self._current_scenario = ThermostatScenarioType.parse(value.value)

    @property
    def cooling_setpoint(self) -> int:
        return self._cooling_setpoint

    @property
    def heating_setpoint(self) -> int:
        return self._heating_setpoint
