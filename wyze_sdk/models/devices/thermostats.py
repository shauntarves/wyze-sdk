from __future__ import annotations

from enum import Enum
import logging
from typing import Optional, Sequence, Set, Union

from wyze_sdk.models import JsonObject, PropDef, show_unknown_key_warning

from .base import (AbstractWirelessNetworkedDevice, ClimateMixin, Device, DeviceProp,
                   LockableMixin)


class ThermostatProps(object):
    """
    :meta private:
    """

    @classmethod
    def temperature(cls) -> PropDef:
        # current temperature
        return PropDef("temperature", float, str)

    @classmethod
    def time_to_temp(cls) -> PropDef:
        # estimated number of minutes until the system will reach the
        # desired target temperature
        return PropDef("time2temp_val", int, str)

    @classmethod
    def protect_time(cls) -> PropDef:
        # number of seconds the thermostat will wait before requesting
        # system action, for safety
        return PropDef("protect_time", int, str)

    @classmethod
    def humidity(cls) -> PropDef:
        # current humidity, in percent
        return PropDef("humidity", int, str)

    @classmethod
    def fan_mode(cls) -> PropDef:
        # the current fan mode
        return PropDef("fan_mode", str, acceptable_values=['auto', 'circ', 'on'])

    @classmethod
    def system_mode(cls) -> PropDef:
        # the current system mode
        return PropDef("mode_sys", str, acceptable_values=['auto', 'cool', 'heat', 'off'])

    @classmethod
    def locked(cls) -> PropDef:
        # the lock state, which prevents changes from being made at the physical device
        return PropDef("kid_lock", bool, str, ['0', '1'])

    @classmethod
    def heating_setpoint(cls) -> PropDef:
        # heating set point
        return PropDef("heat_sp", int, str)

    @classmethod
    def cooling_setpoint(cls) -> PropDef:
        # cooling set point
        return PropDef("cool_sp", int, str)

    @classmethod
    def current_scenario(cls) -> PropDef:
        # the current scenario
        return PropDef("current_scenario", str, acceptable_values=['home', 'away', 'sleep'])

    @classmethod
    def working_state(cls) -> PropDef:
        # the working state of the system
        return PropDef("working_state", str, acceptable_values=['cooling', 'heating', 'idle'])

    @classmethod
    def auto_switch(cls) -> PropDef:
        return PropDef("auto_switch_mode", int)

    @classmethod
    def temperature_unit(cls) -> PropDef:
        return PropDef("temp_unit", str, acceptable_values=['F', 'C'])

    @classmethod
    def stage_io(cls) -> PropDef:
        return PropDef("stage_io", dict, str)

    @classmethod
    def stage_io_test(cls) -> PropDef:
        return PropDef("stage_io_test", dict, str)

    @classmethod
    def relay(cls) -> PropDef:
        return PropDef("relay", str)

    @classmethod
    def save_comfort_balance(cls) -> PropDef:
        # the comfort balance setting
        # Settings -> Behavior
        return PropDef("save_comfort_balance", int, str, range(1, 6))

    @classmethod
    def trigger_off_val(cls) -> PropDef:
        # the allowed differential temperature from the target before
        # the system turns on/off
        # Settings -> Advanced -> Differential Temp
        return PropDef("trigger_off_val", float, str)

    @classmethod
    def calibrate_humidity(cls) -> PropDef:
        # the manual humidity calibration adjustment for heating and cooling
        # Settings -> Advanced -> Humidity Correction
        return PropDef("calibrate_humidity", dict, str)

    @classmethod
    def calibrate_temperature(cls) -> PropDef:
        # the manual temperature calibration adjustment for heating and cooling
        # Settings -> Advanced -> Temperature Correction
        return PropDef("calibrate_temperature", dict, str)

    @classmethod
    def secure_temp_high(cls) -> PropDef:
        # maximum allowable temperature before thermostat forcefully runs
        # Settings -> Advanced -> Safety Temperatures
        return PropDef("secure_temp_high", int, str)

    @classmethod
    def secure_temp_low(cls) -> PropDef:
        # minimum allowable temperature before thermostat forcefully runs
        # Settings -> Advanced -> Safety Temperatures
        return PropDef("secure_temp_low", int, str)

    @classmethod
    def air_wave(cls) -> PropDef:
        # Settings -> Advanced -> Coast To Cool
        return PropDef("air_wave", bool, str)

    @classmethod
    def auto_comfort(cls) -> PropDef:
        return PropDef("auto_comfort", bool, str, ['0', '1'])

    @classmethod
    def sensor_using(cls) -> PropDef:
        # the sensors associated with the thermostat
        return PropDef("sensor_using", dict, str)

    @classmethod
    def sensor_state(cls) -> PropDef:
        # the sensors associated with the thermostat
        return PropDef("sensor_state", dict, str)

    @classmethod
    def sensor_template(cls) -> PropDef:
        # the sensors associated with the thermostat
        return PropDef("sensor_template", dict, str)

    @classmethod
    def sensor_weight(cls) -> PropDef:
        # the sensors associated with the thermostat
        return PropDef("sensor_weight", dict, str)

    @classmethod
    def threshold_temper(cls) -> PropDef:
        # the temperature difference threshold at which sensors will trigger notification
        return PropDef("threshold_temper", dict, str)


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


class ThermostatSetupItemStatus(Enum):
    """
    See: com.wyze.earth.common.enums.SetupItemStatusEnum
    """

    DEFAULT = ('Default', 0)
    ONGOING = ('Ongoing', 1)
    READY = ('Ready', 2)
    COMPLETE = ('Complete', 3)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional["ThermostatSetupItemStatus"]:
        for item in list(ThermostatSetupItemStatus):
            if code == item.code:
                return item


class ThermostatInstallationValue(Enum):
    """
    See: com.wyze.earth.common.enums.InstallationEnum
    """

    PREPARATION = ('preparation', 0)
    CWIRE = ('cwire', 1)
    MOUNTING = ('mounting', 2)
    THERMOSTAT = ('thermostat', 3)
    HVACSYSTEM = ('hvacsystem', 4)
    PERSONALIZATION = ('personalization', 5)
    SYSTEMTEST = ('systemtest', 6)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional[ThermostatInstallationValue]:
        for item in list(ThermostatInstallationValue):
            if code == item.code:
                return item


class ThermostatComfortBalanceMode(Enum):
    """
    See: com.wyze.earth.activity.setup.personalization.fragment.PersonalizationPreferencesFragment
    """

    MAX_SAVINGS = ('Maximum savings', 1)
    SUSTAINABILITY = ('Sustainability', 2)
    BALANCE = ('Balance comfort and savings', 3)
    BETTER_COMFORT = ('Weighted comfort balance', 4)
    MAX_COMFORT = ('Maximum comfort', 5)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: Union[int, str]) -> Optional[ThermostatComfortBalanceMode]:
        for item in list(ThermostatComfortBalanceMode):
            if code == item.code or code == str(item.code):
                return item


class RoomSensorBatteryLevel(Enum):
    """
    See: com.wyze.sensor.activity.setting.SensorBaseDeviceInfoActivity.getBatterySourceId
    """

    LEVEL_0 = ('Empty battery (level 0)', 1)
    LEVEL_1 = ('Low battery (level 1)', 2)
    LEVEL_2 = ('Half battery (level 2)', 3)
    LEVEL_3 = ('Full battery (level 3)', 4)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: Union[int, str]) -> Optional[RoomSensorBatteryLevel]:
        for item in list(RoomSensorBatteryLevel):
            if code == item.code or code == str(item.code):
                return item
        if code is None or code.strip() == '':
            return RoomSensorBatteryLevel.LEVEL_3


class RoomSensorStatusType(Enum):
    """
    See: com.wyze.earth.model.SensorEntity.up
    """

    AUTO_UP = ('Included in comfort control', 'auto_up')
    MANUAL_UP = ('Manually included in comfort control', 'manual_up')
    MANUAL_DOWN = ('Manually excluded from comfort control', 'manual_down')

    def __init__(self, description: str, code: str):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional[RoomSensorStatusType]:
        for item in list(RoomSensorStatusType):
            if code == item.code:
                return item


class RoomSensorStateType(Enum):
    """
    See: com.wyze.earth.model.SensorEntity.connect
    """

    ONLINE = ('Online', 'connect')
    OFFLINE = ('Offline', '')

    def __init__(self, description: str, code: str):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: str) -> Optional[RoomSensorStateType]:
        for item in list(RoomSensorStateType):
            if code == item.code:
                return item
        return RoomSensorStateType.OFFLINE


class ThermostatSensorComfortBalanceMode(Enum):

    MAX_SAVINGS = (ThermostatComfortBalanceMode.MAX_SAVINGS.description, 1)
    BALANCE = (ThermostatComfortBalanceMode.BALANCE.description, 0)
    MAX_COMFORT = (ThermostatComfortBalanceMode.MAX_COMFORT.description, 2)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: Union[int, str]) -> Optional[ThermostatSensorComfortBalanceMode]:
        for item in list(ThermostatSensorComfortBalanceMode):
            if code == item.code or code == str(item.code):
                return item


class ThermostatSensorTemplate(Enum):

    NONE = ("Does not trigger HOME or SLEEP events", False, False, 0)
    HOME = ("Triggers HOME events", True, False, 1)
    SLEEP = ("Triggers SLEEP events", False, True, 2)
    HOME_SLEEP = ("Triggers HOME and SLEEP events", True, True, 3)

    def __init__(self, description: str, triggers_home: bool, triggers_sleep: bool, code: int):
        self.description = description
        self.triggers_home = triggers_home
        self.triggers_sleep = triggers_sleep
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: Union[int, str]) -> Optional[ThermostatSensorTemplate]:
        for item in list(ThermostatSensorTemplate):
            if code == item.code or code == str(item.code):
                return item


class ThermostatCalibrationProps(object):
    """
    :meta private:
    """

    @classmethod
    def heating(cls) -> PropDef:
        return PropDef("b", float, str)

    @classmethod
    def cooling(cls) -> PropDef:
        return PropDef("k", float, str)


class ThermostatCalibrationSettings(JsonObject):
    """
    Adjustment model for calibrating temperature and/or humidity.
    """

    attributes = {
        "heating",
        "cooling",
    }

    def __init__(
        self,
        *,
        heating: float = None,
        cooling: float = None,
        **others: dict,
    ):
        if heating is not None:
            self.heating = heating
        else:
            heating = super()._extract_attribute(ThermostatCalibrationProps.heating().pid, others)
            self.heating = heating if isinstance(heating, float) else float(heating)
        if cooling is not None:
            self.cooling = cooling
        else:
            cooling = super()._extract_attribute(ThermostatCalibrationProps.cooling().pid, others)
            self.cooling = cooling if isinstance(cooling, float) else float(cooling)


class RoomSensorProps(object):
    """
    :meta private:
    """

    @classmethod
    def device_id(cls) -> PropDef:
        return PropDef("device_id", str)

    @classmethod
    def device_name(cls) -> PropDef:
        return PropDef("device_name", str)

    @classmethod
    def device_model(cls) -> PropDef:
        return PropDef("device_model", str)

    @classmethod
    def temperature(cls) -> PropDef:
        return PropDef("temperature", float, str)

    @classmethod
    def temperature_unit(cls) -> PropDef:
        return PropDef("temperature_unit", str, acceptable_values=['F', 'C'])

    @classmethod
    def battery(cls) -> PropDef:
        return PropDef("battery", bytes, str)


class RoomSensor(ClimateMixin, Device):
    """
    A room sensor, which can report to a Thermostat.
    """
    type = "Room Sensor"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "did",
            "model",
            "temperature",
            "humidity",
            "battery",
            "state",
            "status",
            "auto_comfort_mode",
            "comfort_balance_weight",
            "temperature_threshold",
        })

    @classmethod
    def props(cls) -> Sequence[PropDef]:
        return [
            RoomSensorProps.temperature(),
            ThermostatProps.humidity(),
            RoomSensorProps.temperature_unit(),
            RoomSensorProps.battery(),
        ]

    @classmethod
    def device_info_props(cls) -> Sequence[PropDef]:
        return [
            RoomSensorProps.device_name()
        ]

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        did: str = None,
        name: str = None,
        model: str = None,
        temperature: float = None,
        humidity: int = None,
        battery: RoomSensorBatteryLevel = None,
        state: RoomSensorStateType = None,
        status: RoomSensorStatusType = None,
        auto_comfort_mode: ThermostatSensorTemplate = None,
        comfort_balance_weight: ThermostatSensorComfortBalanceMode = None,
        temperature_threshold: int = None,
        **others: dict
    ):
        super().__init__(
            type=self.type,
            nickname=name if name is not None else super()._extract_attribute(RoomSensorProps.device_name().pid, others),
            **others
        )
        self.did = did if did is not None else super()._extract_attribute(RoomSensorProps.device_id().pid, others)
        self.model = model if model is not None else super()._extract_attribute(RoomSensorProps.device_model().pid, others)
        if temperature is None:
            temperature = super()._extract_attribute(RoomSensorProps.temperature().pid, others)
            if temperature is not None and not isinstance(temperature, float):
                try:
                    temperature = float(temperature) / 100
                except ValueError:
                    self.logger.warning(f"invalid temperature '{temperature}'")
        self._temperature = temperature
        if humidity is None:
            humidity = super()._extract_attribute(ThermostatProps.humidity().pid, others)
            if humidity is not None and not isinstance(humidity, int):
                try:
                    humidity = int(humidity)
                except ValueError:
                    self.logger.warning(f"invalid humidity '{temperature}'")
        self._humidity = humidity
        if battery is None:
            battery = RoomSensorBatteryLevel.parse(super()._extract_attribute(RoomSensorProps.battery().pid, others))
        self.battery = battery
        if state is None:
            state = RoomSensorStateType.parse(super()._extract_attribute(ThermostatProps.sensor_state().pid, others))
        self.state = state
        if status is None:
            status = RoomSensorStatusType.parse(super()._extract_attribute(ThermostatProps.sensor_using().pid, others))
        self.status = status
        if auto_comfort_mode is None:
            auto_comfort_mode = ThermostatSensorTemplate.parse(super()._extract_attribute(ThermostatProps.sensor_template().pid, others))
        self.auto_comfort_mode = auto_comfort_mode
        if comfort_balance_weight is None:
            comfort_balance_weight = ThermostatSensorComfortBalanceMode.parse(super()._extract_attribute(ThermostatProps.sensor_weight().pid, others))
        self.comfort_balance_weight = comfort_balance_weight
        if temperature_threshold is None:
            temperature_threshold = super()._extract_attribute(ThermostatProps.threshold_temper().pid, others)
            if temperature_threshold is not None and not isinstance(temperature_threshold, int):
                try:
                    temperature_threshold = int(temperature_threshold)
                except ValueError:
                    self.logger.warning(f"invalid temperature threshold '{temperature_threshold}'")
        self.temperature_threshold = temperature_threshold
        show_unknown_key_warning(self, others)


class Thermostat(ClimateMixin, LockableMixin, AbstractWirelessNetworkedDevice):
    type = "Thermostat"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(Thermostat.props().keys()).union(Thermostat.device_info_props().keys())

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {
            "trigger_off_val": ThermostatProps.trigger_off_val(),
            "emheat": PropDef("emheat", int, str),
            "temperature": ThermostatProps.temperature(),
            "humidity": ThermostatProps.humidity(),
            "time2temp_val": ThermostatProps.time_to_temp(),
            "protect_time": ThermostatProps.protect_time(),
            "system_mode": ThermostatProps.system_mode(),
            "heating_setpoint": ThermostatProps.heating_setpoint(),
            "cooling_setpoint": ThermostatProps.cooling_setpoint(),
            "current_scenario": ThermostatProps.current_scenario(),
            "config_scenario": PropDef("config_scenario", dict, str),
            "temp_unit": ThermostatProps.temperature_unit(),
            "fan_mode": ThermostatProps.fan_mode(),
            "iot_state": PropDef("iot_state", str),
            "w_city_id": PropDef("w_city_id", str),
            "w_lat": PropDef("w_lat", float, str),
            "w_lon": PropDef("w_lon", float, str),
            "working_state": ThermostatProps.working_state(),
            "device_hold": PropDef("dev_hold", int, str),
            "device_hold_time": PropDef("dev_holdtime", int),
            "asw_hold": PropDef("asw_hold", int),
            "app_version": PropDef("app_version", str),
            "setup_state": PropDef("setup_state", int),
            "wiring_logic_id": PropDef("wiring_logic_id", int),
            "save_comfort_balance": ThermostatProps.save_comfort_balance(),
            "locked": ThermostatProps.locked(),
            "calibrate_humidity": ThermostatProps.calibrate_humidity(),
            "calibrate_temperature": ThermostatProps.calibrate_temperature(),
            "query_schedule": PropDef("query_schedule", int, str),
            "air_wave": ThermostatProps.air_wave(),
            "phi_l": PropDef("phi_l", int, str),
            "phi_h": PropDef("phi_h", int, str),
            "w_city_name": PropDef("w_city_name", str),
            "secure_temp_low": ThermostatProps.secure_temp_low(),
            "secure_temp_high": ThermostatProps.secure_temp_high(),
            "fancirc_time": PropDef("fancirc_time", int, str),
            "fan_delay_time": PropDef("fan_delay_time", int, str),
            "ac_overcool_max": PropDef("ac_overcool_max", str),
            "wifi_mac": PropDef("wifi_mac", str),
            "ssid": PropDef("ssid", str),
            "RSSI": PropDef("RSSI", int, str),
            "IP": PropDef("IP", str),
            "sn": PropDef("sn", str),
            "relay": PropDef("relay", str),
            "avg_temper": PropDef("avg_temper", float, str),
            "avg_humid": PropDef("avg_humid", int, str),
            "auto_comfort": ThermostatProps.auto_comfort(),
        }

    @classmethod
    def device_info_props(cls) -> dict[str, PropDef]:
        return {
            "auto_switch_mode": ThermostatProps.auto_switch(),
            "setup_is_have_cadapter": PropDef("setup_is_have_cadapter", int),
            "setup_personalization_state": PropDef("setup_personalization_state", str),
            "setup_step": PropDef("setup_step", int),
            "setup_test_state": PropDef("setup_test_state", str),
            "setup_wires": PropDef("setup_wires", dict),
            "plugin_version": PropDef("plugin_version", str),
            "terminal_type": PropDef("terminal_type", str),
            "w_lat": PropDef("w_lat", str),
            "w_lon": PropDef("w_lon", str),
            "notification_enable": PropDef("notification_enable", str),
            "notification_safe_temp_reached": PropDef("notification_safe_temp_reached", str),
            "notification_insights_save_energy": PropDef("notification_insights_save_energy", str),
        }

    @classmethod
    def sensor_props(cls) -> dict[str, PropDef]:
        return {
            "sensor_state": ThermostatProps.sensor_state(),
            "sensor_using": ThermostatProps.sensor_using(),
            "sensor_template": ThermostatProps.sensor_template(),
            "sensor_weight": ThermostatProps.sensor_weight(),
            "threshold_temper": ThermostatProps.threshold_temper(),
            "auto_comfort": ThermostatProps.auto_comfort(),
        }

    def __init__(self, **others: dict):
        super().__init__(type=self.type, **others)
        self._humidity = super()._extract_attribute(ThermostatProps.humidity().pid, others)
        self._temperature = super()._extract_attribute(ThermostatProps.temperature().pid, others)
        self._cooling_setpoint = super()._extract_attribute(ThermostatProps.cooling_setpoint().pid, others)
        self._heating_setpoint = super()._extract_attribute(ThermostatProps.heating_setpoint().pid, others)
        self.fan_mode = super()._extract_property(ThermostatProps.fan_mode(), others)
        self.system_mode = super()._extract_property(ThermostatProps.system_mode(), others)
        self.working_state = super()._extract_attribute(ThermostatProps.working_state().pid, others)
        self.auto_switch_mode = super()._extract_attribute(ThermostatProps.auto_switch().pid, others)
        self.current_scenario = super()._extract_property(ThermostatProps.current_scenario(), others)
        # the following logic mirrors com.wyze.earth.activity.home.EarthMainActivity.setHomeData
        _protect_time = super()._extract_property(ThermostatProps.protect_time(), others)
        self.system_protect = True if _protect_time is not None and _protect_time.value != 0 else False
        if self.system_protect:
            self.time_to_temp = _protect_time.value / 60
        else:
            _time_to_temp = super()._extract_property(ThermostatProps.time_to_temp(), others)
            self.time_to_temp = None if _time_to_temp is None else _time_to_temp.value
        self.lock_state = super()._extract_property(ThermostatProps.locked(), others)
        self._temperature_unit = super()._extract_attribute(ThermostatProps.temperature_unit().pid, others)
        self.comfort_balance = super()._extract_property(ThermostatProps.save_comfort_balance(), others)
        self.temperature_differential = super()._extract_property(ThermostatProps.trigger_off_val(), others)
        self.temperature_calibration = None
        _temperature_calibration = super()._extract_property(ThermostatProps.calibrate_temperature(), others)
        if _temperature_calibration is not None:
            self.temperature_calibration = ThermostatCalibrationSettings(**_temperature_calibration.value)
        self.humidity_calibration = None
        _humidity_calibration = super()._extract_property(ThermostatProps.calibrate_humidity(), others)
        if _humidity_calibration is not None:
            self.humidity_calibration = ThermostatCalibrationSettings(**_humidity_calibration.value)
        self.minimum_allowed_temperature = super()._extract_attribute(ThermostatProps.secure_temp_low().pid, others)
        self.maximum_allowed_temperature = super()._extract_attribute(ThermostatProps.secure_temp_high().pid, others)
        self.coast_to_cool = super()._extract_property(ThermostatProps.air_wave(), others)
        self.auto_comfort = super()._extract_property(ThermostatProps.auto_comfort(), others)
        # self.setup_is_have_cadapter =
        show_unknown_key_warning(self, others)

    @property
    def temperature_unit(self) -> str:
        return self._temperature_unit

    @property
    def fan_mode(self) -> ThermostatFanMode:
        return self._fan_mode

    @fan_mode.setter
    def fan_mode(self, value: Union[ThermostatFanMode, str, DeviceProp]):
        if value is None or isinstance(value, ThermostatFanMode):
            self._fan_mode = value
            return
        if isinstance(value, DeviceProp):
            value = value.value
        self._fan_mode = ThermostatFanMode.parse(value)

    @property
    def system_mode(self) -> ThermostatSystemMode:
        return self._system_mode

    @system_mode.setter
    def system_mode(self, value: Union[ThermostatSystemMode, str, DeviceProp]):
        if value is None or isinstance(value, ThermostatSystemMode):
            self._system_mode = value
            return
        if isinstance(value, DeviceProp):
            value = value.value
        self._system_mode = ThermostatSystemMode.parse(value)

    @property
    def current_scenario(self) -> Optional[ThermostatScenarioType]:
        return self._current_scenario

    @current_scenario.setter
    def current_scenario(self, value: Union[ThermostatScenarioType, str, DeviceProp]):
        if value is None or isinstance(value, ThermostatScenarioType):
            self._current_scenario = value
            return
        if isinstance(value, DeviceProp):
            value = value.value
        self._current_scenario = ThermostatScenarioType.parse(value)

    @property
    def cooling_setpoint(self) -> int:
        return self._cooling_setpoint

    @property
    def heating_setpoint(self) -> int:
        return self._heating_setpoint

    @property
    def comfort_balance(self) -> Optional[ThermostatComfortBalanceMode]:
        return self._comfort_balance

    @comfort_balance.setter
    def comfort_balance(self, value: Union[ThermostatComfortBalanceMode, int, str, DeviceProp]):
        if value is None or isinstance(value, ThermostatComfortBalanceMode):
            self._comfort_balance = value
            return
        if isinstance(value, DeviceProp):
            value = value.value
        self._comfort_balance = ThermostatComfortBalanceMode.parse(value)

    @property
    def is_locked(self) -> bool:
        if super().lock_state is None:
            return False
        return super().lock_state.value
