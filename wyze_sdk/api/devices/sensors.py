from abc import ABCMeta
from typing import Optional, Sequence

from wyze_sdk.api.base import BaseClient
from wyze_sdk.models.devices import (ContactSensor, DeviceModels, MotionSensor,
                                     Sensor)


class SensorsClient(BaseClient, metaclass=ABCMeta):

    def _list_sensors(self, models: DeviceModels) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device['product_model'] in models]

    def _get_sensor(self, device_mac: str, sensors: Sequence[dict]) -> Optional[dict]:
        """Look up a single sensor by MAC from a pre-fetched list.

        The previous implementation accepted Union[Sensor, Sequence[Sensor]] and
        had a branch for a single Sensor instance that was never reached in practice
        (both info() callers always pass a Sequence[dict]). That branch also
        subscripted the Sensor object like a dict, which would raise TypeError at
        runtime. Removed in favour of a simple Sequence-only signature.
        """
        _sensors = [_sensor for _sensor in sensors if _sensor['mac'] == device_mac]
        if len(_sensors) == 0:
            return None

        _sensor = _sensors[0]
        _sensor.update(
            self._api_client().get_device_info(
                mac=_sensor['mac'],
                model=_sensor['product_model'])["data"]
        )

        return _sensor


class ContactSensorsClient(SensorsClient):
    """A Client that services Wyze Sense contact sensors.
    """

    def _list_contact_sensors(self) -> Sequence[dict]:
        return super()._list_sensors(DeviceModels.CONTACT_SENSOR)

    def list(self) -> Sequence[ContactSensor]:
        """Lists all contact sensors available to a Wyze account.

        :rtype: Sequence[ContactSensor]
        """
        return [ContactSensor(**device) for device in self._list_contact_sensors()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[ContactSensor]:
        """Retrieves details of a contact sensor.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Optional[ContactSensor]
        """
        contact_sensor = self._get_sensor(device_mac, self._list_contact_sensors())
        if contact_sensor is not None:
            return ContactSensor(**contact_sensor)
        return None


class MotionSensorsClient(SensorsClient):
    """A Client that services Wyze Sense motion sensors.
    """

    def _list_motion_sensors(self) -> Sequence[dict]:
        return super()._list_sensors(DeviceModels.MOTION_SENSOR)

    def list(self) -> Sequence[MotionSensor]:
        """Lists all motion sensors available to a Wyze account.

        :rtype: Sequence[MotionSensor]
        """
        return [MotionSensor(**device) for device in self._list_motion_sensors()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[MotionSensor]:
        """Retrieves details of a motion sensor.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Optional[MotionSensor]
        """
        motion_sensor = self._get_sensor(device_mac, self._list_motion_sensors())
        if motion_sensor is not None:
            return MotionSensor(**motion_sensor)
        return None
