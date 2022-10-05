from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Sequence, Set, Tuple, Union

from wyze_sdk.errors import WyzeObjectFormationError
from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime,
                             show_unknown_key_warning)
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice,
                                     DeviceProp, VoltageMixin)


class VacuumProps(object):
    """
    :meta private:
    """

    @classmethod
    def clean_level(cls) -> PropDef:
        return PropDef("cleanlevel", str)

    @classmethod
    def sweep_record_clean_time(cls) -> PropDef:
        return PropDef("clean_time", int)

    @classmethod
    def sweep_record_clean_size(cls) -> PropDef:
        return PropDef("clean_size", int)

    @classmethod
    def mode(cls) -> PropDef:
        return PropDef("mode", int)

    @classmethod
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
        self._id = id if id else int(self._extract_attribute('roomId_', others))
        self._name = name if name else self._extract_attribute('roomName_', others)
        if not clean_state:
            clean_state = self._extract_attribute('cleanState_', others)
            if clean_state:
                clean_state = int(clean_state)
        self._clean_state = clean_state
        if not room_clean:
            room_clean = self._extract_attribute('roomClean_', others)
            if room_clean:
                room_clean = int(room_clean)
        self._room_clean = room_clean
        if not name_position:
            name_position = self._extract_attribute('roomNamePost_', others)
            if name_position:
                name_position = VacuumMapPoint(**name_position)
        self._name_position = name_position
        show_unknown_key_warning(self, others)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def clean_state(self) -> Optional[int]:
        return self._clean_state

    @property
    def room_clean(self) -> Optional[int]:
        return self._room_clean

    @property
    def name_position(self) -> Optional[VacuumMapPoint]:
        return self._name_position


class VacuumMap(JsonObject):
    """
    The protobuf definition for a vacuum map.
    """

    @classmethod
    def _robot_map_proto(cls) -> dict:
        return {
            # Java type int
            #  0 == REAL_TIME
            #  1 == POINT
            #  2 == AREA
            #  3 == MEMORY
            '1': {'type': 'int', 'name': 'mapType_'},
            # Mapped from MapExtInfo to VenusMapExtraTimeBean
            '2': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'taskBeginDate_'},
                '2': {'type': 'int', 'name': 'mapUploadDate_'}
            }, 'name': 'mapExtInfo_'},
            # Mapped from MapHeadInfo to VenusMapHeadBean
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
            # Mapped from MapDataInfo to VenusMapContentBean
            '4': {'type': 'message', 'message_typedef': {
                '1': {'type': 'bytes', 'name': 'mapData_'}
            }, 'name': 'mapData_'},
            # Mapped from List<AllMapInfo> to List<VenusMapIdAndNameBean>
            '5': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'mapHeadId_'},
                '2': {'type': 'bytes', 'name': 'mapName_'}
            }, 'name': ''},  # mapInfo_
            # Mapped from DeviceHistoryPoseInfo to VenusDeviceHistoryPoseBean
            '6': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'poseId_'},
                # Mapped from DeviceCoverPointDataInfo to VenusDeviceCoverPointBean
                '2': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': 'update_'},
                    '2': {'type': 'float', 'name': 'x_'},
                    '3': {'type': 'float', 'name': 'y_'}
                }, 'name': 'points_'},
                '3': {'type': 'int', 'name': 'pathType_'}
            }, 'name': 'historyPose_'},
            # Mapped from DevicePoseDataInfo to VenusChargingPilePositionBean
            '7': {'type': 'message', 'message_typedef': {
                '1': {'type': 'float', 'name': 'x_'},
                '2': {'type': 'float', 'name': 'y_'},
                '3': {'type': 'float', 'name': 'phi_'}
            }, 'name': 'chargeStation_'},
            # Mapped from DeviceCurrentPoseInfo to VenusDeviceCurrentPositionBean
            # currentPose_ only present when unit is active
            '8': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'poseId_'},
                '2': {'type': 'int', 'name': 'update_'},
                '3': {'type': 'float', 'name': 'x_'},
                '4': {'type': 'float', 'name': 'y_'},
                '5': {'type': 'float', 'name': 'phi_'}
            }, 'name': 'currentPose_'},
            #  Mapped from List<DeviceAreaDataInfo> to List<VenusDeviceAreaBean>
            '9': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'status_'},
                '2': {'type': 'int', 'name': 'type_'},
                '3': {'type': 'int', 'name': 'areaIndex_'},
                # Mapped from List<DevicePointInfo> to List<VenusDeviceAreaBean.RoomPoint>
                '4': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'float', 'name': 'x_'},
                    '2': {'type': 'float', 'name': 'y_'}
                }, 'name': 'points_'},
            }, 'name': 'virtualWalls_'},
            #  Mapped from List<DeviceAreaDataInfo> to List<VenusDeviceAreaBean>
            '10': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'status_'},
                '2': {'type': 'int', 'name': 'type_'},
                '3': {'type': 'int', 'name': 'areaIndex_'},
                # Mapped from List<DevicePointInfo> to List<VenusDeviceAreaBean.RoomPoint>
                '4': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'float', 'name': 'x_'},
                    '2': {'type': 'float', 'name': 'y_'}
                }, 'name': 'points_'},
            }, 'name': 'areasInfo_'},
            # Mapped from List<DeviceNavigationPointDataInfo> to List<VenusDeviceNavigationPointBean>
            # navigationPoints_ only present when unit is active
            '11': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'pointId_'},
                '2': {'type': 'int', 'name': 'status_'},
                '3': {'type': 'int', 'name': 'pointType_'},
                '4': {'type': 'float', 'name': 'x_'},
                '5': {'type': 'float', 'name': 'y_'},
                '6': {'type': 'float', 'name': 'phi_'}
            }, 'name': 'navigationPoints_'},
            # Mapped from List<RoomDataInfo> to List<VenusRoomSweepBean>
            '12': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'roomId_'},
                '2': {'type': 'bytes', 'name': 'roomName_'},
                '3': {'type': 'int', 'name': 'roomTypeId_'},
                '4': {'type': 'int', 'name': 'meterialId_'},
                '5': {'type': 'int', 'name': 'cleanState_'},
                '6': {'type': 'int', 'name': 'roomClean_'},
                '7': {'type': 'int', 'name': 'roomCleanIndex_'},
                # Mapped from List<DevicePointInfo> to List<VenusDeviceAreaBean.RoomPoint>
                '8': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'float', 'name': 'x_'},
                    '2': {'type': 'float', 'name': 'y_'}
                }, 'name': 'roomNamePost_'},
                # Mapped from CleanPerferenceDataInfo to VenusCleanPreferenceBean
                '9': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': 'cleanMode_'},
                    '2': {'type': 'int', 'name': 'waterLevel_'},
                    '3': {'type': 'int', 'name': 'windPower_'},
                    '4': {'type': 'int', 'name': 'twiceClean_'},
                }, 'name': 'cleanPerfer_'}
            }, 'name': ''},  # roomDataInfo_
            # Mapped from DeviceRoomMatrix to VenusRoomMatrixBean
            '13': {'type': 'message', 'message_typedef': {
                '1': {'type': 'bytes', 'name': 'matrix_'}
            }, 'name': 'roomMatrix_'},
            # Mapped from List<DeviceRoomChainDataInfo> to List<VenusRoomChainBean>
            '14': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'roomId_'},
                # Mapped from List<DeviceChainPointDataInfo> to List<VenusRoomChainBean.RoomChainPoint>
                '2': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': 'x_'},
                    '2': {'type': 'int', 'name': 'y_'},
                    '3': {'type': 'int', 'name': 'value_'}
                }, 'name': 'points_'}
            }, 'name': 'roomChain_'},
            # Mapped from List<ObjectDataInfo> to List<VenusObjectIdentifyBean>
            '15': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'objectId_'},
                '2': {'type': 'int', 'name': 'objectTypeId_'},
                '3': {'type': 'bytes', 'name': 'objectName_'},
                '4': {'type': 'int', 'name': 'confirm_'},
                '5': {'type': 'float', 'name': 'x_'},
                '6': {'type': 'float', 'name': 'y_'},
                '7': {'type': 'bytes', 'name': 'url_'},
            }, 'name': 'objects_'},
            # Mapped from List<FurnitureDataInfo> to List<VenusFurnitureBean>
            '16': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'id_'},
                '2': {'type': 'int', 'name': 'typeId_'},
                # Mapped from List<DevicePointInfo> to List<VenusDeviceAreaBean.RoomPoint>
                '3': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'float', 'name': 'x_'},
                    '2': {'type': 'float', 'name': 'y_'}
                }, 'name': 'points_'},
                '4': {'type': 'bytes', 'name': 'url_'},
                '5': {'type': 'int', 'name': 'status_'},
            }, 'name': 'furnitureInfo_'},
            # Mapped from List<HouseInfo> to List<VenusHouseBean>
            '17': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'id_'},
                '2': {'type': 'bytes', 'name': 'name_'},
                '3': {'type': 'int', 'name': 'curMapCount_'},
                '4': {'type': 'int', 'name': 'maxMapSize_'},
                # Mapped from List<AllMapInfo> to List<VenusMapIdAndNameBean>
                '5': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': 'mapHeadId_'},
                    '2': {'type': 'bytes', 'name': 'mapName_'}
                }, 'name': 'maps_'},
            }, 'name': 'houseInfos_'},
            #  Mapped from List<DeviceAreaDataInfo> to List<VenusDeviceAreaBean>
            '18': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': 'status_'},
                '2': {'type': 'int', 'name': 'type_'},
                '3': {'type': 'int', 'name': 'areaIndex_'},
                # Mapped from List<DevicePointInfo> to List<VenusDeviceAreaBean.RoomPoint>
                '4': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'float', 'name': 'x_'},
                    '2': {'type': 'float', 'name': 'y_'}
                }, 'name': 'points_'},
            }, 'name': 'backupAreas_'},
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
        if 'historyPose_' in map_data and 'points' in map_data['historyPose_']:
            return [VacuumMapNavigationPoint(**points) for points in map_data['historyPose_']['points']]
        if '6' in map_data and '2' in map_data['6']:
            return [VacuumMapNavigationPoint(**points) for points in map_data['6']['2']]

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
                self._logger.info(f"key: {key}")
                self._logger.info(f"  type: {value.__class__}")
                if isinstance(value, (list, dict)):
                    self._logger.info(f"  count: {len(value)}")

            return map
        except (binascii.Error, zlib.error) as e:
            raise WyzeObjectFormationError(f"encountered an error parsing map blob {e}")


class VacuumMapSummary(JsonObject):
    """
    A vacuum map summary.
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "current_map",
            "img_url",
            "latest_area_point_list",
            "map_id",
            "room_info_list",
            "user_map_name",
        }

    def __init__(
        self,
        *,
        current_map: bool = False,
        img_url: str = None,
        map_id: int = None,
        user_map_name: str = None,
        **others: dict
    ):
        self._current_map = current_map if current_map else self._extract_attribute('current_map', others)
        self._img_url = img_url if img_url else self._extract_attribute('img_url', others)
        self._map_id = map_id if map_id else self._extract_attribute('map_id', others)
        self._user_map_name = user_map_name if user_map_name else self._extract_attribute('user_map_name', others)
        self._room_info_list = None
        self._latest_area_point_list = None
        latest_area_point_list = self._extract_attribute('latest_area_point_list', others)
        if latest_area_point_list:
            if not isinstance(latest_area_point_list, (list, Tuple)):
                latest_area_point_list = [latest_area_point_list]
            self._latest_area_point_list = [VacuumMapPoint(x=point['point_x'], y=point['point_y']) for point in latest_area_point_list]
        room_info_list = self._extract_attribute('room_info_list', others)
        if room_info_list:
            if not isinstance(room_info_list, (list, Tuple)):
                room_info_list = [room_info_list]
            self._room_info_list = [VacuumMapRoom(id=room['room_id'], name=room['room_name']) for room in room_info_list]
        show_unknown_key_warning(self, others)

    @property
    def is_current(self) -> bool:
        return False if self._current_map is None else self._current_map

    @property
    def img_url(self) -> str:
        return self._img_url

    @property
    def id(self) -> int:
        return self._map_id

    @property
    def name(self) -> int:
        return self._user_map_name

    @property
    def rooms(self) -> Optional[Sequence[VacuumMapRoom]]:
        return None if not self._room_info_list else self._room_info_list

    @property
    def latest_points(self) -> Optional[Sequence[VacuumMapPoint]]:
        return None if not self._latest_area_point_list else self._latest_area_point_list


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
            value = DeviceProp(definition=VacuumProps.sweep_record_clean_time(), value=value)
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
            value = DeviceProp(definition=VacuumProps.sweep_record_clean_size(), value=value)
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


class VacuumSupplyProps(object):
    """
    :meta private:
    """

    @classmethod
    def filter(cls) -> PropDef:
        return PropDef("filter", int)

    @classmethod
    def sweep_record_clean_time(cls) -> PropDef:
        return PropDef("clean_time", int)

    @classmethod
    def sweep_record_clean_size(cls) -> PropDef:
        return PropDef("clean_size", int)


class VacuumSupplyType(Enum):

    MAIN_BRUSH = ('Main brush', 300)
    SIDE_BRUSH = ('Side brush', 200)
    FILTER = ('Filter', 150)
    # DISHCLOTH = ('Dishcloth', 0) // not used

    def __init__(self, description: str, max_hours: int):
        self.description = description
        self.max_hours = max_hours

    def describe(self) -> str:
        return self.description


class VacuumSupplyLevel(object):
    """
    The usage information for vacuum supplies.
    """

    attributes = {
        "type",
        "usage",
        "remaining",
    }

    def __init__(
        self,
        *,
        type: VacuumSupplyType = None,
        usage: Optional[int] = None,
    ):
        self._type = type
        self._usage = usage

    @property
    def type(self) -> VacuumSupplyType:
        return self._type

    @property
    def usage(self) -> str:
        return self._usage

    @property
    def remaining(self) -> str:
        return self.type.max_hours - self.usage


class VacuumSupplies(JsonObject):
    """
    Vacuum supply levels.
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "filter",
            "main_brush",
            "side_brush",
            # "dishcloth" // not used
        }

    def __init__(
        self,
        *,
        filter: int = None,
        main_brush: int = None,
        side_brush: int = None,
        **others: dict
    ):
        self._filter = VacuumSupplyLevel(
            type=VacuumSupplyType.FILTER,
            usage=filter if filter is not None else self._extract_attribute(Vacuum.props().get('filter').pid, others)
        )
        self._main_brush = VacuumSupplyLevel(
            type=VacuumSupplyType.MAIN_BRUSH,
            usage=main_brush if main_brush is not None else self._extract_attribute(Vacuum.props().get('main_brush').pid, others)
        )
        self._side_brush = VacuumSupplyLevel(
            type=VacuumSupplyType.SIDE_BRUSH,
            usage=side_brush if side_brush is not None else self._extract_attribute(Vacuum.props().get('side_brush').pid, others)
        )

    @property
    def filter(self) -> VacuumSupplyLevel:
        """
        The supply levels of the filter.
        """
        return self._filter

    @property
    def main_brush(self) -> VacuumSupplyLevel:
        """
        The supply levels of the main brush.
        """
        return self._main_brush

    @property
    def side_brush(self) -> VacuumSupplyLevel:
        """
        The supply levels of the side brush.
        """
        return self._side_brush


class Vacuum(VoltageMixin, AbstractWirelessNetworkedDevice):

    type = "Vacuum"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "rooms",
            "current_position",
            "current_map",
            "supplies",
        }).union(Vacuum.props().keys()).union(Vacuum.device_info_props().keys())

    @classmethod
    def props(cls) -> dict[str, PropDef]:
        return {
            "iot_state": PropDef("iot_state", str),
            "battery": VacuumProps.battery(),
            "mode": VacuumProps.mode(),
            "charge_state": PropDef("chargeState", int),
            "clean_size": PropDef("cleanSize", int),
            "clean_time": PropDef("cleanTime", int),
            "fault_type": PropDef("fault_type", str),
            "fault_code": PropDef("fault_code", int),
            "current_map_id": PropDef("current_mapid", int),
            "count": PropDef("count", int),
            "clean_level": VacuumProps.clean_level(),
            "notice_save_map": PropDef("notice_save_map", bool),
            "memory_map_update_time": PropDef("memory_map_update_time", int),
            "filter": PropDef("filter", int),
            "side_brush": PropDef("side_brush", int),
            "main_brush": PropDef("main_brush", int),
            # "dishcloth": PropDef("dishcloth", int), // unused
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
        self.voltage = super()._extract_property(VacuumProps.battery(), others)
        self.mode = super()._extract_attribute('mode' if "mode" in others else VacuumProps.mode().pid, others)
        self.clean_level = super()._extract_attribute('clean_level' if "clean_level" in others else VacuumProps.clean_level().pid, others)
        self._supplies = VacuumSupplies(**others)
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
    def supplies(self) -> VacuumSupplies:
        return self._supplies

    @property
    def mode(self) -> VacuumMode:
        return self._mode

    @mode.setter
    def mode(self, value: Union[int, DeviceProp]):
        if value is None:
            return
        if isinstance(value, int):
            value = DeviceProp(definition=VacuumProps.mode(), value=value)
        self._mode = VacuumMode.parse(code=value.value)

    @property
    def clean_level(self) -> VacuumSuctionLevel:
        return self._clean_level

    @clean_level.setter
    def clean_level(self, value: Union[str, int, DeviceProp]):
        if value is None:
            return
        if isinstance(value, (str, int)):
            value = DeviceProp(definition=VacuumProps.clean_level(), value=value)
        self._clean_level = VacuumSuctionLevel.parse(code=value.value)
