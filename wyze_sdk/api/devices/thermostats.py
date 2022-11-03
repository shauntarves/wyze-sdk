from collections import defaultdict
from collections.abc import MutableMapping
from datetime import datetime
import itertools
import json
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.api.base import BaseClient
from wyze_sdk.models.devices import DeviceModels, DeviceProp, Thermostat
from wyze_sdk.models.devices.thermostats import (ThermostatFanMode, ThermostatProps,
                                                 ThermostatScenarioType, RoomSensor, RoomSensorProps,
                                                 ThermostatSystemMode)
from wyze_sdk.service import WyzeResponse


class ThermostatsClient(BaseClient):
    """A Client that services Wyze thermostats.
    """

    def list(self, **kwargs) -> Sequence[Thermostat]:
        """Lists all thermostats available to a Wyze account.

        :rtype: Sequence[Thermostat]
        """
        return [Thermostat(**device) for device in self._list_thermostats()]

    def _list_thermostats(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.THERMOSTAT]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Thermostat]:
        """Retrieves details of a thermostat.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``

        :rtype: Optional[Thermostat]
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

    def get_sensors(self, *, device_mac: str, device_model: str, **kwargs) -> Sequence[RoomSensor]:
        """Retrieves room sensors associated with a thermostat.

        Args:
        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``

        :rtype: Sequence[RoomSensor]
        """
        # reading through the code in `com.wyze.earth.activity.home.EarthSensorsActivity`,
        # the data flow seems to be:
        #   initView() sets up a refresh handler
        #       when the view needs refreshing, call getSensors()
        #           * triggers call to /get_sub_device
        #               * gathers the sub-device (sensor) IDs
        #               * calls mergeDate()
        #                   * parses the properties into a coherent format (SensorEntity)
        #                   * calls requestDeviceInfo()
        #                       triggers call to /device_info/batch with did of all sensors and key device_name
        #                   * calls getTempData()
        #                       triggers call to /get_iot_prop/batch with did of all sensors and keys temperature,humidity,temperature_unit,battery
        #           * triggers call to /get_iot_prop with keys sensor_state,sensor_using,sensor_template,sensor_weight,threshold_temper
        #               * calls mergeDate()
        #           * triggers call to getThermostat()
        #               calls /get_iot_prop on thermostat with keys temperature,humidity,iot_state,auto_comfort
        _sensors = [_sub_device for _sub_device in super()._earth_client().get_sub_device(did=device_mac).data["data"]]
        if len(_sensors) == 0:
            return None

        _dids = list(map(lambda _sensor: _sensor['device_id'], _sensors))

        _device_info_batch = super()._earth_client().get_device_info(did=_dids, parent_did=device_mac, model=device_model, keys=[prop_def.pid for prop_def in RoomSensor.device_info_props()])
        _iot_prop_batch = super()._earth_client().get_iot_prop(did=_dids, parent_did=device_mac, model=device_model, keys=[prop_def.pid for prop_def in RoomSensor.props()])
        _iot_prop = super()._earth_client().get_iot_prop(did=device_mac, keys=[prop_def.pid for prop_def in Thermostat.sensor_props().values()])

        for _sensor in _sensors:
            if "data" in _device_info_batch.data:
                _sensor_device_info = next(filter(lambda _data: _data['deviceId'] == _sensor['device_id'], _device_info_batch["data"]))
                if "settings" in _sensor_device_info:
                    _sensor.update(**{"device_setting": _sensor_device_info["settings"]})
            if "data" in _iot_prop_batch.data:
                _sensor_iot_prop = next(filter(lambda _data: _data['did'] == _sensor['device_id'], _iot_prop_batch["data"]))
                if "props" in _sensor_iot_prop:
                    _sensor.update(**{"device_params": _sensor_iot_prop["props"]})
            if "data" in _iot_prop.data and "props" in _iot_prop.data["data"]:
                for _prop, _sensor_list in dict(_iot_prop.data["data"]["props"]).items():
                    _sensor_list = json.loads(_sensor_list)
                    if isinstance(_sensor_list, MutableMapping):
                        if _sensor['device_id'] in _sensor_list.keys():
                            _sensor.update({_prop: _sensor_list.get(_sensor['device_id'])})

        return [RoomSensor(**_sensor) for _sensor in _sensors]

    def set_system_mode(self, *, device_mac: str, device_model: str, system_mode: ThermostatSystemMode, **kwargs) -> WyzeResponse:
        """Sets the system mode of the thermostat.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param ThermostatSystemMode system_mode: The new system mode. e.g. ``ThermostatSystemMode.AUTO``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, DeviceProp(definition=Thermostat.props()["system_mode"], value=system_mode.codes))

    def set_fan_mode(self, *, device_mac: str, device_model: str, fan_mode: ThermostatFanMode, **kwargs) -> WyzeResponse:
        """Sets the fan mode of the thermostat.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param ThermostatFanMode fan_mode: The new fan mode. e.g. ``ThermostatFanMode.CYCLE``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, DeviceProp(definition=Thermostat.props()["fan_mode"], value=fan_mode.codes))

    def set_mode(self, *, device_mac: str, device_model: str, system_mode: ThermostatSystemMode, fan_mode: ThermostatFanMode, **kwargs) -> WyzeResponse:
        """Sets the system and fan modes of the thermostat.

        .. note:: Fan mode and system mode cannot be set independently via this method.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param ThermostatSystemMode system_mode: The new system mode. e.g. ``ThermostatSystemMode.AUTO``
        :param ThermostatFanMode fan_mode: The new fan mode. e.g. ``ThermostatFanMode.CYCLE``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["fan_mode"], value=fan_mode.codes),
            DeviceProp(definition=Thermostat.props()["system_mode"], value=system_mode.codes),
        ])

    def set_current_scenario(self, *, device_mac: str, device_model: str, scenario: ThermostatScenarioType, **kwargs) -> WyzeResponse:
        """Sets the current scenario of the thermostat.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param ThermostatScenarioType scenario: The new scenario. e.g. ``ThermostatScenarioType.HOME``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_property(device_mac, device_model, DeviceProp(definition=Thermostat.props()["current_scenario"], value=scenario.codes))

    def set_heating_setpoint(self, *, device_mac: str, device_model: str, heating_setpoint: int, **kwargs) -> WyzeResponse:
        """Sets the heating setpoint of the thermostat.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param int heating_setpoint: The new heating setpoint. e.g. ``68``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, DeviceProp(definition=Thermostat.props()["heating_setpoint"], value=heating_setpoint))

    def set_cooling_setpoint(self, *, device_mac: str, device_model: str, cooling_setpoint: int, **kwargs) -> WyzeResponse:
        """Sets the cooling setpoint of the thermostat.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param int cooling_setpoint: The new cooling setpoint. e.g. ``72``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, DeviceProp(definition=Thermostat.props()["cooling_setpoint"], value=cooling_setpoint))

    def set_temperature(self, *, device_mac: str, device_model: str, cooling_setpoint: int, heating_setpoint: int, **kwargs) -> WyzeResponse:
        """Sets the heating and cooling setpoints of the thermostat.

        .. note:: Heating and cooling setpoints cannot be set independently via this method.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param int cooling_setpoint: The new cooling setpoint. e.g. ``72``
        :param int heating_setpoint: The new heating setpoint. e.g. ``68``

        :rtype: WyzeResponse
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
            the_props[prop.definition.pid] = str(prop.api_value)
        return super()._earth_client().set_iot_prop_by_topic(
            did=device_mac, model=device_model, props=the_props)

    def clear_hold(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Clears any existing hold on the thermostat and resumes "smart" operations.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["asw_hold"], value=0),
            DeviceProp(definition=Thermostat.props()["device_hold"], value=0),
            DeviceProp(definition=Thermostat.props()["device_hold_time"], value=0),
        ])

    def hold(self, *, device_mac: str, device_model: str, until: datetime, **kwargs) -> WyzeResponse:
        """Holds the current thermostat settings until a certain date/time.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param datetime until: The new end date/time of the hold.

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, [
            DeviceProp(definition=Thermostat.props()["device_hold"], value=1),
            DeviceProp(definition=Thermostat.props()["device_hold_time"], value=until.timestamp()),
        ])

    def set_lock(self, *, device_mac: str, device_model: str, locked: Union[bool, int], **kwargs) -> WyzeResponse:
        """Sets the device lock for a thermostat.

        If set, the thermostat can only be updated via the app and not by using the physical controls.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param int locked (int): The new locked state. e.g. ``1``

        :rtype: WyzeResponse
        """
        if not isinstance(locked, bool):
            locked = True if locked == 1 else False
        return self._set_thermostat_properties(device_mac, device_model, DeviceProp(definition=Thermostat.props()["locked"], value=locked))

    def set_behavior(self, *, device_mac: str, device_model: str, behavior: int, **kwargs) -> WyzeResponse:
        """Sets the comfort balance behavior for a thermostat.

        This setting allows the user to toggle between preset behaviors for weighing cost savings vs.
        climate comfort. An update to this property will modify the device's scenario setpoints.

        :param str device_mac: The device mac. e.g. ``CO_EA1_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``CO_EA1``
        :param int behavior: The new behavior. e.g. ``1``

        :rtype: WyzeResponse
        """
        return self._set_thermostat_properties(device_mac, device_model, DeviceProp(definition=Thermostat.props()["save_comfort_balance"], value=behavior))
