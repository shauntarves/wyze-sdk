from datetime import datetime
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.models.devices import DeviceModels, DeviceProp, Thermostat
from wyze_sdk.models.devices.thermostats import (ThermostatFanMode,
                                                 ThermostatScenarioType,
                                                 ThermostatSystemMode)
from wyze_sdk.service import WyzeResponse
from wyze_sdk.api.base import BaseClient


class ThermostatsClient(BaseClient):
    """A Client that services Wyze thermostats.

    Methods:
        list: Lists all thermostats available to a Wyze account
        info: Retrieves details of a thermostat
        set_system_mode: Sets the system mode of the thermostat
        set_fan_mode: Sets the fan mode of the thermostat
        set_mode: Sets the system and fan modes of the thermostat
        set_current_scenario: Sets the current scenario of the thermostat
        set_heating_setpoint: Sets the heating setpoint of the thermostat
        set_cooling_setpoint: Sets the cooling setpoint of the thermostat
        set_temperature: Sets the heating and cooling setpoints of the thermostat
        hold: Holds the current thermostat settings until a certain date/time
        set_lock: Sets the device lock for a thermostat
        set_behavior: Sets the comfort balance behavior for a thermostat
        clear_hold: Clears any existing hold on the thermostat and resumes "smart" operations
    """

    def list(self, **kwargs) -> Sequence[Thermostat]:
        """Lists all thermostats available to a Wyze account.

        Returns:
            (Sequence[Thermostat])
        """
        return [Thermostat(**device) for device in self._list_thermostats()]

    def _list_thermostats(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.THERMOSTAT]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Thermostat]:
        """Retrieves details of a thermostat.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'

        Returns:
            (Optional[Thermostat])
        """
        thermostats = [_thermostat for _thermostat in self._list_thermostats() if _thermostat['mac'] == device_mac]
        if len(thermostats) == 0:
            return None

        thermostat = thermostats[0]

        iot_prop = super()._earth_client().get_iot_prop(did=device_mac, keys=[prop_def.pid for prop_def in Thermostat.props().values()])
        if "data" in iot_prop.data and "props" in iot_prop.data["data"]:
            thermostat.update(iot_prop.data["data"]["props"])

        device_info = super()._earth_client().get_device_info(did=device_mac, keys=[prop_def.pid for prop_def in Thermostat.device_info_props().values()])
        if "data" in device_info.data and "settings" in device_info.data["data"]:
            thermostat.update(device_info.data["data"]["settings"])

        return Thermostat(**thermostat)

    def set_system_mode(self, *, device_mac: str, device_model: str, system_mode: ThermostatSystemMode, **kwargs) -> WyzeResponse:
        """Sets the system mode of the thermostat.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            system_mode (int): The new system mode. e.g. ThermostatSystemMode.AUTO
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["system_mode"], value=system_mode.codes))

    def set_fan_mode(self, *, device_mac: str, device_model: str, fan_mode: ThermostatFanMode, **kwargs) -> WyzeResponse:
        """Sets the fan mode of the thermostat.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            fan_mode (int): The new fan mode. e.g. ThermostatFanMode.CYCLE
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["fan_mode"], value=fan_mode.codes))

    def set_mode(self, *, device_mac: str, device_model: str, system_mode: ThermostatSystemMode, fan_mode: ThermostatFanMode, **kwargs) -> WyzeResponse:
        """Sets the system and fan modes of the thermostat.

        Note: Fan mode and system mode cannot be set independently via this method..

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            system_mode (int): The new system mode. e.g. ThermostatSystemMode.AUTO
            fan_mode (int): The new fan mode. e.g. ThermostatFanMode.CYCLE
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["fan_mode"], value=fan_mode.codes),
            DeviceProp(definition=Thermostat.props()["system_mode"], value=system_mode.codes),
        ])

    def set_current_scenario(self, *, device_mac: str, device_model: str, scenario: ThermostatScenarioType, **kwargs) -> WyzeResponse:
        """Sets the current scenario of the thermostat.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            scenario (ThermostatScenarioType): The new scenario. e.g. ThermostatScenarioType.HOME
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["current_scenario"], value=scenario.codes))

    def set_heating_setpoint(self, *, device_mac: str, device_model: str, heating_setpoint: int, **kwargs) -> WyzeResponse:
        """Sets the heating setpoint of the thermostat.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            heating_setpoint (int): The new heating setpoint. e.g. 68
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["heating_setpoint"], value=heating_setpoint))

    def set_cooling_setpoint(self, *, device_mac: str, device_model: str, cooling_setpoint: int, **kwargs) -> WyzeResponse:
        """Sets the cooling setpoint of the thermostat.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            cooling_setpoint (int): The new cooling setpoint. e.g. 72
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["cooling_setpoint"], value=cooling_setpoint))

    def set_temperature(self, *, device_mac: str, device_model: str, cooling_setpoint: int, heating_setpoint: int, **kwargs) -> WyzeResponse:
        """Sets the heating and cooling setpoints of the thermostat.

        Note: Heating and cooling setpoints cannot be set independently via this method.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            cooling_setpoint (int): The new cooling setpoint. e.g. 72
            heating_setpoint (int): The new heating setpoint. e.g. 68
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["cooling_setpoint"], value=cooling_setpoint),
            DeviceProp(definition=Thermostat.props()["heating_setpoint"], value=heating_setpoint),
        ])

    def _set_thermostat_property(self, device_mac: str, device_model: str, prop: DeviceProp) -> WyzeResponse:
        return super()._earth_client().set_iot_prop(did=device_mac, model=device_model, key=prop.definition.pid, value=str(prop.value))

    def _set_thermostat_properties(self, device_mac: str, device_model: str, props: Union[DeviceProp, Sequence[DeviceProp]]) -> WyzeResponse:
        if not isinstance(props, (list, Tuple)):
            props = [props]
        the_props = {}
        for prop in props:
            the_props[prop.definition.pid] = str(prop.value)
        return super()._earth_client().set_iot_prop_by_topic(
            did=device_mac, model=device_model, props=the_props)

    def clear_hold(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Clears any existing hold on the thermostat and resumes "smart" operations.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["asw_hold"], value=0),
            DeviceProp(definition=Thermostat.props()["device_hold"], value=0),
            DeviceProp(definition=Thermostat.props()["device_hold_time"], value=0),
        ])

    def hold(self, *, device_mac: str, device_model: str, until: datetime, **kwargs) -> WyzeResponse:
        """Holds the current thermostat settings until a certain date/time.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            until (datetime): The new end date/time of the hold.
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["device_hold"], value=1),
            DeviceProp(definition=Thermostat.props()["device_hold_time"], value=until.timestamp()),
        ])

    def set_lock(self, *, device_mac: str, device_model: str, locked: int, **kwargs) -> WyzeResponse:
        """Sets the device lock for a thermostat.

        If set, the thermostat can only be updated via the app and not by using the physical controls.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            locked (int): The new locked state. e.g. 1
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["locked"], value=locked))

    def set_behavior(self, *, device_mac: str, device_model: str, behavior: int, **kwargs) -> WyzeResponse:
        """Sets the comfort balance behavior for a thermostat.

        This setting allows the user to toggle between preset behaviors for weighing cost savings vs.
        climate comfort. An update to this property will modify the device's scenario setpoints.

        Args:
            device_mac (str): The device mac. e.g. 'CO_EA1_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'CO_EA1'
            behavior (int): The new behavior. e.g. 1
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["save_comfort_balance"], value=behavior))
