"""Classes for constructing Wyze-specific data strtucture"""

from .base import (AbstractWirelessNetworkedDevice, ClimateMixin, ContactMixin,  # noqa
                   Device, DeviceModels, DeviceProp, DeviceProps,
                   LockableMixin, MotionMixin, PropDef, SwitchableMixin, VoltageMixin)
from .bulbs import Bulb, MeshBulb, BulbProps  # noqa
from .cameras import Camera, CameraProps  # noqa
from .locks import (Lock, LockGateway, LockEventType, LockProps, LockRecord, LockRecordDetail)  # noqa
from .plugs import Plug, OutdoorPlug, PlugProps  # noqa
from .scales import Scale, ScaleRecord, UserGoalWeight, ScaleProps  # noqa
from .sensors import Sensor, ContactSensor, MotionSensor, SensorProps  # noqa
from .thermostats import Thermostat, ThermostatFanMode, ThermostatProps, ThermostatScenarioType, ThermostatSystemMode  # noqa
from .vacuums import Vacuum, VacuumMap, VacuumMapNavigationPoint, VacuumMapPoint, VacuumMapRoom, VacuumMode, VacuumProps, VacuumSuctionLevel  # noqa


class DeviceParser(object):
    import logging
    from typing import Optional, Union

    _logger = logging.getLogger(__name__)

    @classmethod
    def parse(cls, device: Union[dict, "Device"]) -> Optional["Device"]:
        if device is None:
            return None
        elif isinstance(device, Device):
            return device
        else:
            if "product_type" in device:
                type = device["product_type"]
                if type == Bulb.type:
                    return Bulb(**device)
                elif type == Camera.type:
                    return Camera(**device)
                elif type == ContactSensor.type:
                    return ContactSensor(**device)
                elif type == Lock.type:
                    return Lock(**device)
                elif type == LockGateway.type:
                    return LockGateway(**device)
                elif type == MeshBulb.type:
                    return MeshBulb(**device)
                elif type == MotionSensor.type:
                    return MotionSensor(**device)
                elif type == Plug.type:
                    return Plug(**device)
                elif type == OutdoorPlug.type:
                    return OutdoorPlug(**device)
                elif type == Scale.type or type in DeviceModels.SCALE:
                    return Scale(**device)
                elif type == Thermostat.type or type in DeviceModels.THERMOSTAT:
                    return Thermostat(**device)
                elif type == Vacuum.type or type in DeviceModels.VACUUM:
                    return Vacuum(**device)
                else:
                    cls._logger.warning(f"Unknown device detected and skipped ({device})")
                    return None
            else:
                cls._logger.warning(f"Unknown device detected and skipped ({device})")
                return None
