from datetime import datetime
from enum import Enum
import logging
from typing import Any, Optional, Sequence, Set, Tuple, Union

from wyze_sdk.errors import WyzeObjectFormationError
from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime, show_unknown_key_warning)
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice, DeviceProp, VoltageMixin)


class VacuumProps(object):

    @classmethod
    @property
    def clean_level(cls) -> PropDef:
        return PropDef("cleanlevel", str)

    @classmethod
    @property
    def sweep_record_clean_time(cls) -> PropDef:
        return PropDef("clean_time", int)

    @classmethod
    @property
    def sweep_record_clean_size(cls) -> PropDef:
        return PropDef("clean_size", int)

    @classmethod
    @property
    def mode(cls) -> PropDef:
        return PropDef("mode", int)

    @classmethod
    @property
    def battery(cls) -> PropDef:
        return PropDef("battary", int)  # typo required


class VacuumMode(Enum):

    BREAK_POINT = ('break point', [11, 33, 39])
    IDLE = ('idle', [0, 14, 29, 35, 40])
    PAUSE = ('pause', [4, 9, 27, 31, 37])
    SWEEPING = ('sweeping', [1, 7, 25, 30, 36])
    ON_WAY_CHARGE = ('on way charge', 5)
    FULL_FINISH_SWEEPING_ON_WAY_CHARGE = ('full finish sweeping on way charge', [10, 12, 26, 32, 38])

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self) -> str:
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["VacuumMode"]:
        for mode in list(VacuumMode):
            if code in mode.codes:
                return mode


class VacuumSuctionLevel(Enum):

    QUIET = ('Quiet', 1)
    STANDARD = ('Standard', 2)
    STRONG = ('Strong', 3)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self) -> str:
        return self.description

    @classmethod
    def parse(cls, code: Union[str, int]) -> Optional["VacuumSuctionLevel"]:
        if isinstance(code, str):
            try:
                code = int(code)
            except TypeError:
                return None
        for item in list(VacuumSuctionLevel):
            if code == item.code:
                return item


class VacuumMapPoint(JsonObject):

    @property
    def attributes(self) -> Set[str]:
        return {
            "x",
            "y",
            "phi",
        }

    def __init__(
        self,
        *,
        x: float = None,
        y: float = None,
        phi: Optional[float] = None,
        **others: dict
    ):
        self.x = x if x else float(self._extract_attribute('x_', others))
        self.y = y if y else float(self._extract_attribute('y_', others))
        try:
            self.phi = phi if phi is not None else float(self._extract_attribute('phi_', others))
        except TypeError:
            pass
        show_unknown_key_warning(self, others)


class VacuumMapNavigationPoint(JsonObject):

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "status",
            "point_type",
            "coordinates",
        }

    def __init__(
        self,
        *,
        id: int = None,
        status: int = None,
        point_type: int = None,
        coordinates: VacuumMapPoint = None,
        **others: dict
    ):
        self._id = id if id else int(self._extract_attribute('pointId_', others))
        self._status = status if status else int(self._extract_attribute('status_', others))
        self._point_type = point_type if point_type else int(self._extract_attribute('pointType_', others))
        self._coordinates = coordinates if coordinates else VacuumMapPoint(**others)
        show_unknown_key_warning(self, others)

    @property
    def id(self) -> int:
        return self._id

    @property
    def status(self) -> int:
        return self._status

    @property
    def point_type(self) -> int:
        return self._point_type

    @property
    def coordinates(self) -> VacuumMapPoint:
        return self._coordinates


class VacuumMapRoom(JsonObject):

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "name",
            "clean_state",
            "room_clean",
            "name_position",
        }

    def __init__(
        self,
        *,
        id: str = None,
        name: str = None,
        clean_state: int = None,
        room_clean: int = None,
        name_position: VacuumMapPoint = None,
        **others: dict
    ):
        self._id = id if id else int(self._extract_attribute('id', others))
        self._name = name if name else self._extract_attribute('name', others)
        self._clean_state = clean_state if clean_state else int(self._extract_attribute('clean_state', others))
        self._room_clean = room_clean if room_clean else int(self._extract_attribute('room_clean', others))
        self._name_position = name_position if name_position else VacuumMapPoint(**self._extract_attribute('roomNamePost_', others))
        show_unknown_key_warning(self, others)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def clean_state(self) -> int:
        return self._clean_state

    @property
    def room_clean(self) -> int:
        return self._room_clean

    @property
    def name_position(self) -> VacuumMapPoint:
        return self._name_position


class VacuumMap(JsonObject):
    """
    The protobuf definition for a vacuum map.
    """

    @classmethod
    def _robot_map_proto(cls) -> dict:
        return {
            '1': {'type': 'int', 'name': 'mapType_'},
            '2': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'taskBeginDate_'},
                '2': {'type': 'int', 'name': 'mapUploadDate_'}
            }, 'name': 'mapExtInfo_'},
            '3': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'mapHeadId_'},
                '2': {'type': 'int', 'name': 'sizeX_'},
                '3': {'type': 'int', 'name': 'sizeY_'},
                '4': {'type': 'float', 'name': 'minX_'},
                '5': {'type': 'float', 'name': 'minY_'},
                '6': {'type': 'float', 'name': 'maxX_'},
                '7': {'type': 'float', 'name': 'maxY_'},
                '8': {'type': 'float', 'name': 'resolution_'}
            }, 'name': 'mapHeadInfo_'},
            '4': {'type': 'message', 'message_typedef': {
                '1': {'type': 'bytes', 'name': 'mapData_'}
            }, 'name': 'mapData_'},
            '5': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'mapHeadId_'},
                '2': {'type': 'bytes', 'name': 'mapName_'}
            }, 'name': 'mapInfo_'},
            '6': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'poseId_'},
                '2': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': 'update_'},
                    '2': {'type': 'float', 'name': 'x_'},
                    '3': {'type': 'float', 'name': 'y_'}
                }, 'name': ''}
            }, 'name': ''},
            '7': {'type': 'message', 'message_typedef': {
                '1': {'type': 'float', 'name': 'x_'},
                '2': {'type': 'float', 'name': 'y_'},
                '3': {'type': 'float', 'name': 'phi_'}
            }, 'name': 'chargeStation_'},
            '8': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'poseId_'},
                '2': {'type': 'int', 'name': 'update_'},
                '3': {'type': 'float', 'name': 'x_'},
                '4': {'type': 'float', 'name': 'y_'},
                '5': {'type': 'float', 'name': 'phi_'}
            }, 'name': 'currentPose_'},
            #  9: virtualWalls
            # 10: areasInfo
            '11': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'pointId_'},
                '2': {'type': 'int', 'name': 'status_'},
                '3': {'type': 'int', 'name': 'pointType_'},
                '4': {'type': 'float', 'name': 'x_'},
                '5': {'type': 'float', 'name': 'y_'},
                '6': {'type': 'float', 'name': 'phi_'}
            }, 'name': ''},  # navigationPoints_
            '12': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'id'},  # roomId_
                '2': {'type': 'bytes', 'name': 'name'},  # roomName_
                # '3': {'type': 'bytes', 'name': 'roomTypeId_'},
                # '4': {'type': 'bytes', 'name': 'meterialId_'},
                '5': {'type': 'int', 'name': 'clean_state'},  # cleanState_
                '6': {'type': 'int', 'name': 'room_clean'},  # roomClean_
                # '7': {'type': 'int', 'name': 'roomCleanIndex_'},
                '8': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'float', 'name': 'x_'},
                    '2': {'type': 'float', 'name': 'y_'}
                }, 'name': 'roomNamePost_'}
            }, 'name': ''},  # error when using roomDataInfo_
            '13': {'type': 'message', 'message_typedef': {
                '1': {'type': 'bytes', 'name': 'matrix_'}
            }, 'name': 'roomMatrix_'},
            '14': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'room'},
                '2': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': 'x_'},
                    '2': {'type': 'int', 'name': 'y_'},
                    '3': {'type': 'int', 'name': 'value_'}
                }, 'name': ''}  # error when using points_
            }, 'name': ''}  # error when using roomChain_
            # 15: objects
            # 16: furnitureInfo
            # 17: houseInfos
            # 18: backupAreas
        }

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "name",
            "created",
            "updated",
        }

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        id: int = None,
        name: str = None,
        created: datetime = None,
        updated: datetime = None,
        blob: dict = None,
        **others: dict,
    ):
        self._id = id if id else self._extract_attribute('mapId', others)
        self._name = name if name else self._extract_attribute('mapName', others)
        self._created = created if created else epoch_to_datetime(self._extract_attribute('createTime', others), ms=True)
        self._updated = updated if updated else epoch_to_datetime(self._extract_attribute('updateTime', others), ms=True)
        self._blob = blob if blob else self._extract_attribute('map', others)
        show_unknown_key_warning(self, others)

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def updated(self) -> datetime:
        return self._updated

    @property
    def charge_station(self) -> Optional[VacuumMapPoint]:
        map_data = self.parse_blob(blob=self._blob)
        if 'chargeStation_' in map_data:
            return VacuumMapPoint(**map_data['chargeStation_'])
        if '7' in map_data:
            return VacuumMapPoint(**map_data['7'])

    @property
    def rooms(self) -> Optional[Sequence[VacuumMapRoom]]:
        map_data = self.parse_blob(blob=self._blob)
        if 'roomDataInfo_' in map_data:
            return [VacuumMapRoom(**room) for room in map_data['roomDataInfo_']]
        if '12' in map_data:
            return [VacuumMapRoom(**room) for room in map_data['12']]

    @property
    def navigation_points(self) -> Optional[Sequence[VacuumMapNavigationPoint]]:
        map_data = self.parse_blob(blob=self._blob)
        if 'historyPose_' in map_data:
            print(map_data['historyPose_'])
            return [VacuumMapNavigationPoint(**points) for points in map_data['historyPose_']['points']]
        if '6' in map_data:
            print(map_data['6'])
            return [VacuumMapNavigationPoint(**points) for points in map_data['6']['points']]

    def parse_blob(self, blob: str) -> dict:
        if blob is None:
            return {}

        import base64
        import binascii
        import json
        import zlib

        import blackboxprotobuf

        try:
            compressed = base64.b64decode(blob)
            if compressed is None:
                raise WyzeObjectFormationError('could not decode map blob')

            decompressed = zlib.decompress(compressed)

            # add the protobuf definition to the known types
            blackboxprotobuf.known_messages['robot_map'] = VacuumMap._robot_map_proto()

            # for some reason we have to re-encode and then re-decode the bytes
            map, typedef = blackboxprotobuf.protobuf_to_json(base64.b64decode(base64.b64encode(decompressed)), 'robot_map')

            map = json.loads(map)
            for key, value in map.items():
                self._logger.debug(f"key: {key}")
                self._logger.debug(f"  type: {value.__class__}")
                if isinstance(value, (list, dict)):
                    self._logger.debug(f"  count: {len(value)}")

            return map
        except (binascii.Error, zlib.error) as e:
            raise WyzeObjectFormationError(f"encountered an error parsing map blob {e}")


class VacuumSweepRecord(JsonObject):
    """
    A vacuum sweep record.
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "created",
            "started",
            "clean_type",
            "clean_time",
            "clean_size",
            "model",
            "map_img_big_url",
            "map_img_small_url",
        }

    def __init__(
        self,
        *,
        created: datetime = None,
        started: datetime = None,
        clean_type: int = None,
        clean_time: int = None,
        clean_size: int = None,
        model: str = None,
        **others: dict
    ):
        self._created = created if created else epoch_to_datetime(self._extract_attribute('create_time', others), ms=True)
        self._started = started if started else epoch_to_datetime(self._extract_attribute('timeBegin', others))
        self._clean_type = clean_type if clean_type else self._extract_attribute('cleanType', others)
        self.clean_time = clean_time if clean_time is not None else self._extract_attribute('cleanTime', others)
        self.clean_size = clean_size if clean_size is not None else self._extract_attribute('cleanSize', others)
        self._model = model if model else self._extract_attribute('model', others)
        self._map_img_big_url = self._extract_attribute('map_img_big_url', others)
        self._map_img_small_url = self._extract_attribute('map_img_small_url', others)
        show_unknown_key_warning(self, others)

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def started(self) -> datetime:
        return self._started

    @property
    def clean_time(self) -> int:
        """
        The cleaning time of this sweep record (in minutes).
        """
        return None if self._clean_time is None else self._clean_time.value

    @clean_time.setter
    def clean_time(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=VacuumProps.sweep_record_clean_time, value=value)
        self._clean_time = value

    @property
    def clean_size(self) -> int:
        """
        The area cleaned during this sweep record (in sq.ft.).

        What comes from the API is some number related to m^2, but it's been multiplied
        by 100, presumably to send across an integer that can be parsed to a single
        significant digit?
        """
        return None if self._clean_size is None else int((self._clean_size.value / 100) * 10.76391)

    @clean_size.setter
    def clean_size(self, value: Union[int, DeviceProp]):
        if isinstance(value, int):
            value = DeviceProp(definition=VacuumProps.sweep_record_clean_size, value=value)
        self._clean_size = value

    @property
    def model(self) -> str:
        return self._model

    @property
    def map_img_big_url(self) -> str:
        return self._map_img_big_url

    @property
    def map_img_small_url(self) -> str:
        return self._map_img_small_url


class Vacuum(VoltageMixin, AbstractWirelessNetworkedDevice):

    type = "Vacuum"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "rooms",
            "current_position",
            "current_map",
        }).union(Vacuum.props().keys()).union(Vacuum.device_info_props().keys())

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {
            "iot_state": PropDef("iot_state", str),
            "battery": VacuumProps.battery,
            "mode": VacuumProps.mode,
            "charge_state": PropDef("chargeState", int),
            "clean_size": PropDef("cleanSize", int),
            "clean_time": PropDef("cleanTime", int),
            "fault_type": PropDef("fault_type", str),
            "fault_code": PropDef("fault_code", int),
            "current_map_id": PropDef("current_mapid", int),
            "count": PropDef("count", int),
            "clean_level": VacuumProps.clean_level,
            "notice_save_map": PropDef("notice_save_map", bool),
            "memory_map_update_time": PropDef("memory_map_update_time", int),
        }

    @classmethod
    def device_info_props(cls) -> dict[str, PropDef]:
        return {
            "mac": PropDef("mac", str),
            "ip": PropDef("ipaddr", str),
            "device_type": PropDef("device_type", str),
            "mcu_sys_version": PropDef("mcu_sys_version", str),
        }

    def __init__(
        self,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.voltage = super()._extract_property(VacuumProps.battery, others)
        self.mode = super()._extract_attribute('mode' if "mode" in others else VacuumProps.mode.pid, others)
        self.clean_level = super()._extract_attribute('clean_level' if "clean_level" in others else VacuumProps.clean_level.pid, others)
        self._current_map = VacuumMap(**super()._extract_attribute('current_map', others)) if "current_map" in others else None
        self.current_position = super()._extract_attribute('current_position', others)
        show_unknown_key_warning(self, others)

    @property
    def rooms(self) -> Sequence[VacuumMapRoom]:
        if self.current_map is not None:
            return self.current_map.rooms

    @property
    def current_position(self) -> VacuumMapPoint:
        return self._current_position

    @current_position.setter
    def current_position(self, value: Optional[Any] = None):
        if isinstance(value, (list, Tuple)):
            self._current_position = VacuumMapPoint(**value[0])
        elif isinstance(value, dict):
            self._current_position = VacuumMapPoint(**value)
        else:
            self._current_position = None

    @property
    def current_map(self) -> VacuumMap:
        return self._current_map

    @property
    def mode(self) -> VacuumMode:
        return self._mode

    @mode.setter
    def mode(self, value: Union[int, DeviceProp]):
        if value is None:
            return
        if isinstance(value, int):
            value = DeviceProp(definition=VacuumProps.mode, value=value)
        self._mode = VacuumMode.parse(code=value.value)

    @property
    def clean_level(self) -> VacuumSuctionLevel:
        return self._clean_level

    @clean_level.setter
    def clean_level(self, value: Union[str, int, DeviceProp]):
        if value is None:
            return
        if isinstance(value, (str, int)):
            value = DeviceProp(definition=VacuumProps.clean_level, value=value)
        self._clean_level = VacuumSuctionLevel.parse(code=value.value)
