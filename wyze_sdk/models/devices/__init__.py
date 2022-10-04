"""Classes for constructing Wyze-specific data strtucture"""
from __future__ import annotations

from .base import (AbstractNetworkedDevice, AbstractWirelessNetworkedDevice,  # noqa
                   ClimateMixin, ContactMixin, Device, DeviceModels,
                   DeviceProp, DeviceProps, LockableMixin, MotionMixin,
                   PropDef, SwitchableMixin, VoltageMixin)
from .lights import LightProps, Light  # noqa
from .bulbs import BulbProps, Bulb, MeshBulb, WhiteBulb  # noqa
from .cameras import BaseStation, Camera, CameraProps  # noqa
from .locks import (Lock, LockEventType, LockGateway, LockProps,  # noqa
                    LockRecord, LockRecordDetail)
from .plugs import OutdoorPlug, Plug, PlugProps  # noqa
from .scales import Scale, ScaleProps, ScaleRecord, UserGoalWeight  # noqa
from .sensors import ContactSensor, MotionSensor, Sensor, SensorProps  # noqa
from .thermostats import (Thermostat, ThermostatFanMode,  # noqa
                          ThermostatProps, ThermostatScenarioType,
                          ThermostatSystemMode)
from .vacuums import (Vacuum, VacuumMap, VacuumMapNavigationPoint,  # noqa
                      VacuumMapPoint, VacuumMapRoom, VacuumMode, VacuumProps,
                      VacuumSuctionLevel)


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
                if type == BaseStation.type:
                    return BaseStation(**device)
                elif type == Bulb.type:
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
                elif type == OutdoorPlug.type:
                    return OutdoorPlug(**device)
                elif type == Plug.type:
                    return Plug(**device)
                elif type == Scale.type or type in DeviceModels.SCALE:
                    return Scale(**device)
                elif type == Thermostat.type or type in DeviceModels.THERMOSTAT:
                    return Thermostat(**device)
                elif type == Vacuum.type or type in DeviceModels.VACUUM:
                    return Vacuum(**device)
                else:
                    cls._logger.warning(f"Unknown device type detected ({device})")
                    return Device(**device)
            else:
                cls._logger.warning(f"Unknown device detected and skipped ({device})")
                return None
