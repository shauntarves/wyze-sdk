from __future__ import annotations

from abc import ABCMeta
from typing import Set, Optional

from wyze_sdk.models import PropDef, epoch_to_datetime, show_unknown_key_warning
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice,
                                     ContactMixin, DeviceProps, MotionMixin,
                                     SwitchableMixin, VoltageMixin)


class SensorProps(object):
    """
    P6, P1303 not used

    contact
        See: com.hualai.dws3u.device.WyzeEventSettingPage
        return {**Sensor.props(), **{
            "power_state": DeviceProps.power_state(),  # "is low battery"
            "open_close_state": SensorProps.open_close_state(),
            "open_notification": PropDef("P1306", bool),  # "opens"
            "close_notification": PropDef("P1307", bool),  # "closes"
            "open_notification_delay": PropDef("P1308", ""),  # "left open"
            "close_notification_delay": PropDef("P1309", ""),  # "left closed"
            "open_notification_time": PropDef("P1310", ""),
            "close_notification_time": PropDef("P1311", ""),
            # "": PropDef("P1312", ""), # not used
            # "": PropDef("P1321", ""), # not used
            # "": PropDef("P1322", ""), # not used
            # "": PropDef("P1323", ""), # not used
            # "": PropDef("P1324", ""), # not used
        }}

    motion
        See: com.hualai.pir3u.device.WyzeEventSettingPage
        return {**Sensor.props(), **{
            # "": PropDef("P2", ""), # not used
            # "": PropDef("P4", ""), # not used
            # "": PropDef("P1300", "") # not used
            # "": PropDef("P1316", ""), # not used
            # "": PropDef("P1317", ""), # not used
            # "": PropDef("P1318", ""), # not used
            # "": PropDef("P1319", ""), # not used
            # "": PropDef("P1320", ""), # not used
            # "": PropDef("P1325", ""), # not used
            # "": PropDef("P1326", ""), # not used
            # "": PropDef("P1327", ""), # not used
            # "": PropDef("P1328", ""), # not used
        }}

    :meta private:
    """

    @classmethod
    def notification(cls) -> PropDef:
        return PropDef("P1", bool, int, [0, 1])

    @classmethod
    def rssi(cls) -> PropDef:
        return PropDef("P1304", int)

    @classmethod
    def voltage(cls) -> PropDef:
        return PropDef("P1329", int)

    @classmethod
    def open_close_state(cls) -> PropDef:
        return PropDef("P1301", bool, int, [0, 1])

    @classmethod
    def motion_state(cls) -> PropDef:
        return PropDef("P1302", bool, int, [0, 1])


class Sensor(VoltageMixin, SwitchableMixin, AbstractWirelessNetworkedDevice, metaclass=ABCMeta):
    """
    :meta private:
    """

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "voltage",
            "last_changed",
        })

    def __init__(
        self,
        *,
        type: str,
        last_changed: Optional[int],
        **others: dict,
    ):
        super().__init__(type=type, **others)
        self.switch_state = self._extract_property(DeviceProps.power_state(), others)
        self.voltage = super()._extract_property(SensorProps.voltage(), others)
        self.last_changed = None if last_changed is None else epoch_to_datetime(last_changed, ms=True)


class ContactSensor(ContactMixin, Sensor):

    type = "ContactSensor"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "open_close_state",
        })

    def __init__(
        self, **others: dict,
    ):
        super().__init__(type=self.type, last_changed=self._extract_attribute('open_close_state_ts', others), **others)
        self.open_close_state = super()._extract_property(SensorProps.open_close_state(), others)
        show_unknown_key_warning(self, others)


class MotionSensor(MotionMixin, Sensor):

    type = "MotionSensor"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "motion_state",
        })

    def __init__(
        self, **others: dict,
    ):
        super().__init__(type=self.type, last_changed=self._extract_attribute('motion_state_ts', others), **others)
        self.motion_state = super()._extract_property(SensorProps.motion_state(), others)
        show_unknown_key_warning(self, others)
