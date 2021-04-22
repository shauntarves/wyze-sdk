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