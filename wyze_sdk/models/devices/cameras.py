from typing import (Optional, Sequence, Set)

from wyze_sdk.models import (PropDef, show_unknown_key_warning)
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice, ClimateMixin, DeviceProps, MotionMixin, SwitchableMixin, VoltageMixin)
from wyze_sdk.models.events import Event


class CameraProps(object):
    """
    private String P1 = "P1";
    private String P1001 = "P1001"; # not used
    private String P1002 = "P1002"; # not used
    private String P1003 = "P1003"; # not used
    private String P1004 = "P1004"; # not used
    private String P1005 = "P1005"; # not used
    private String P1006 = "P1006"; # not used
    private String P1007 = "P1007"; # not used
    private String P1008 = "P1008"; # not used
    private String P1009 = "P1009"; # not used
    private String P1011 = "P1011"; # not used
    private String P1012 = "P1012"; # not used
    private String P1018 = "P1018"; # not used
    private String P1019 = "P1019"; # not used
    private String P1020 = "P1020"; # not used
    private String P1021 = "P1021";
    private String P1035 = "P1035"; # not used
    private String P1047 = "P1047"; # event recording motion record enabled
    private String P1048 = "P1048"; # event recording sound record enabled
    private String P13 = "P13"; # not used
    private String P1301 = "P1301"; # not used
    private String P1302 = "P1302"; # not used
    private String P1303 = "P1303"; # not used
    private String P1304 = "P1304"; # not used
    private String P1306 = "P1306"; # not used
    private String P1307 = "P1307"; # not used
    private String P1308 = "P1308"; # not used
    private String P1309 = "P1309"; # not used
    private String P1310 = "P1310"; # not used
    private String P1311 = "P1311"; # not used
    private String P1312 = "P1312"; # not used
    private String P1314 = "P1314"; # not used
    private String P1315 = "P1315"; # not used
    private String P1316 = "P1316"; # not used
    private String P1317 = "P1317"; # not used
    private String P1318 = "P1318"; # not used
    private String P1319 = "P1319"; # not used
    private String P1320 = "P1320"; # not used
    private String P1321 = "P1321"; # not used
    private String P1322 = "P1322"; # not used
    private String P1323 = "P1323"; # not used
    private String P1324 = "P1324"; # not used
    private String P1325 = "P1325"; # not used
    private String P1326 = "P1326"; # not used
    private String P1327 = "P1327"; # not used
    private String P1328 = "P1328"; # not used
    private String P1329 = "P1329"; # not used
    private String P1501 = "P1501"; # not used
    private String P1502 = "P1502"; # not used
    private String P1503 = "P1503"; # not used
    private String P1504 = "P1504"; # not used
    private String P1505 = "P1505"; # not used
    private String P1506 = "P1506"; # not used
    private String P1601 = "P1601"; # not used
    private String P1611 = "P1611"; # not used
    private String P1612 = "P1612"; # not used
    private String P1613 = "P1613"; # not used
    private String P1614 = "P1614"; # not used
    private String P2 = "P2"; # not used
    private String P3 = "P3"; on/off
    private String P4 = "P4";
    private String P5 = "P5"; online

    See: com.hualai.plugin.camera.activity.WyzeDeviceProperty
         com.hualai.plugin.camera_v3.activity.WyzeDeviceProperty
    """

    @classmethod
    @property
    def event_switch(cls) -> PropDef:
        return PropDef("P4", int, [0, 1])

    @classmethod
    @property
    def dongle_light_switch(cls) -> PropDef:
        return PropDef("P1021", int, [0, 1])

    @classmethod
    @property
    def motion_alarm_enable(cls) -> PropDef:
        return PropDef("P1047", int, [0, 1])

    @classmethod
    @property
    def sound_alarm_enable(cls) -> PropDef:
        return PropDef("P1048", int, [0, 1])

    @classmethod
    @property
    def power_switch(cls) -> PropDef:
        return PropDef("power_switch", int, [0, 1])

    @classmethod
    @property
    def temperature(cls) -> PropDef:
        return PropDef("temperature", float)

    @classmethod
    @property
    def humidity(cls) -> PropDef:
        return PropDef("humidity", float)

    @classmethod
    @property
    def comfort_standard_level(cls) -> PropDef:
        return PropDef("comfort_standard_level", int)

    @classmethod
    @property
    def room_type(cls) -> PropDef:
        return PropDef("temp_humi_room_type", int)

    @classmethod
    @property
    def supports_continuous_record(cls) -> PropDef:
        return PropDef("records_event_switch", bool, int, [0, 1])

    @classmethod
    @property
    def suppprts_motion_alarm(cls) -> PropDef:
        return PropDef("motion_alarm_switch", bool, int, [0, 1])

    @classmethod
    @property
    def suppprts_temperature_humidity(cls) -> PropDef:
        return PropDef("is_temperature_humidity", bool, int, [0, 1])

    @classmethod
    @property
    def suppprts_audio_alarm(cls) -> PropDef:
        return PropDef("audio_alarm_switch", bool, int, [0, 1])

    @classmethod
    @property
    def suppprts_smoke_alarm(cls) -> PropDef:
        return PropDef("smoke_alarm_switch", bool, int, [0, 1])

    @classmethod
    @property
    def suppprts_co_alarm(cls) -> PropDef:
        return PropDef("co_alarm_switch", bool, int, [0, 1])

    @classmethod
    @property
    def voltage(cls) -> PropDef:
        return PropDef("electricity", int)

    @classmethod
    @property
    def battery_charging(cls) -> PropDef:
        return PropDef("battery_charging_status", int)


class Camera(ClimateMixin, MotionMixin, VoltageMixin, SwitchableMixin, AbstractWirelessNetworkedDevice):

    type = "Camera"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "power_switch",
            "temperature",
            "humidity",
            "room_type",
            "comfort_standard_level",
            "supports_temperature_humidity",
            "supports_continuous_record",
            "suppprts_audio_alarm",
            "suppprts_co_alarm",
            "suppprts_motion_alarm",
            "suppprts_smoke_alarm",
            "voltage",
            "battery_charging",
            "power_saving_mode_switch",
        })

    def __init__(
        self,
        *,
        event_list: Optional[Sequence[dict]] = None,
        **others: dict
    ):
        super().__init__(type=self.type, **others)
        self.switch_state = super()._extract_property(DeviceProps.power_state, others)
        self._temperature = super()._extract_attribute('temperature', others)
        self._humidity = super()._extract_attribute('humidity', others)
        self._voltage = super()._extract_property(CameraProps.voltage, others)
        self._supports_audio_alarm = super()._extract_property(CameraProps.suppprts_audio_alarm, others)
        self._supports_co_alarm = super()._extract_property(CameraProps.suppprts_co_alarm, others)
        self._supports_motion_alarm = super()._extract_property(CameraProps.suppprts_motion_alarm, others)
        self._suppprts_smoke_alarm = super()._extract_property(CameraProps.suppprts_smoke_alarm, others)
        if event_list is not None:
            self.latest_events = event_list
        show_unknown_key_warning(self, others)

    @property
    def latest_events(self) -> Sequence[Event]:
        return self._latest_events

    @latest_events.setter
    def latest_events(self, value: Sequence[dict]):
        self._latest_events = [latest_event if isinstance(latest_event, Event) else Event(**latest_event) for latest_event in value]

    @property
    def is_audio_alarm(self) -> bool:
        return self._supports_audio_alarm.value if self._supports_audio_alarm is not None else False

    @property
    def is_co_alarm(self) -> bool:
        return self._supports_co_alarm if self._supports_co_alarm is not None else False

    @property
    def is_motion_alarm(self) -> bool:
        return self._supports_motion_alarm if self._supports_motion_alarm is not None else False

    @property
    def is_smoke_alarm(self) -> bool:
        return self._suppprts_smoke_alarm if self._suppprts_smoke_alarm is not None else False
