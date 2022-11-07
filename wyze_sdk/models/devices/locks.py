from __future__ import annotations

from datetime import datetime, time
from enum import Enum
from typing import Optional, Sequence, Set, Tuple, Union

from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime,
                             show_unknown_key_warning, str_to_time)

from .base import (AbstractWirelessNetworkedDevice, ContactMixin, Device,
                   DeviceModels, DeviceProp, LockableMixin, VoltageMixin)


# door_open_status and notice in device_params appear to be unused
# notifications are controlled by a different API
# see: https://wyze-lock-service-broker.wyzecam.com/app/v2/lock
class LockProps(object):
    """
    :meta private:
    """

    @classmethod
    def locker_lock_state(cls) -> PropDef:
        return PropDef("hardlock", int, acceptable_values=range(-1, 6))

    @classmethod
    def locker_open_close_state(cls) -> PropDef:
        return PropDef("door", int, acceptable_values=[1, 2])

    @classmethod
    def lock_state(cls) -> PropDef:
        return PropDef("switch_state", bool, int)

    @classmethod
    def open_close_state(cls) -> PropDef:
        return PropDef("open_close_state", bool, int)

    @classmethod
    def onoff_line(cls) -> PropDef:
        return PropDef("onoff_line", bool, int)

    @classmethod
    def voltage(cls) -> PropDef:
        return PropDef("power", int)

    @classmethod
    def ajar_alarm(cls) -> PropDef:
        return PropDef("ajar_alarm", int, acceptable_values=[1, 2])

    @classmethod
    def trash_mode(cls) -> PropDef:
        return PropDef("trash_mode", int, acceptable_values=[1, 2])

    @classmethod
    def auto_unlock(cls) -> PropDef:
        return PropDef("auto_unlock", int, acceptable_values=[1, 2])

    @classmethod
    def door_sensor(cls) -> PropDef:
        return PropDef("door_sensor", int, acceptable_values=[1, 2])

    @classmethod
    def auto_lock_time(cls) -> PropDef:
        return PropDef("auto_lock_time", int, acceptable_values=range(0, 7))

    @classmethod
    def left_open_time(cls) -> PropDef:
        return PropDef("left_open_time", int, acceptable_values=range(0, 7))

    @classmethod
    def open_volume(cls) -> PropDef:
        return PropDef("open_volume", int, acceptable_values=range(0, 100))

    @classmethod
    def keypad_enable_status(cls) -> PropDef:
        return PropDef("keypad_enable_status", int, acceptable_values=[1, 2])


class LockStatusType(Enum):
    """
    See: com.yunding.ford.widget.LockStatusWidget
    """

    OFFLINE = ('Offline', -1)
    CONNECTING = ('Connecting', 0)
    LOCKED = ('Locked', 1)
    LOCKING = ('Locking', 2)
    UNLOCKED = ('Unlocked', 3)
    UNLOCKING = ('Unlocking', 4)
    UNCALIBRATED = ('Uncalibrated', 5)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockStatusType"]:
        for type in list(LockStatusType):
            if code == type.code:
                return type


class LockEventType(Enum):
    """
    See: ford_lock_history_event_id
    """

    UNLOCKED = ('Unlocked', 2203)
    OPENED = ('Opened', 2214)
    CLOSED = ('Closed', 2215)
    LOCKED = ('Locked', 2216)
    OPEN_TOO_LONG = ('Open too long', 2218)
    JAMMED = ('Jammed', 2221)
    TOTALLY_JAMMED = ('Totally jammed', 2222)
    SWUNG_OPEN = ('Swung open', 2223)
    KEPT_OPEN = ('Kept open longer than 24 hours', 2224)
    TRASH_MODE = ('Trash mode', 2225)
    AUTO_CALIBRATED = ('Auto-calibrated', 2226)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockEventType"]:
        for type in list(LockEventType):
            if code == type.code:
                return type


class LockEventSource(Enum):
    """
    See: ford_lock_history_source
    """

    LOCAL = ('App', 1)
    KEYPAD = ('Keypad', [2, 102])
    FINGERPRINT = ('Fingerprint', 3)
    INSIDE_BUTTON = ('Inside button', 4)
    MANUAL = ('Manual', 5)
    INSIDE_HOLDER = ('Inside holder', 6)
    NFC = ('NFC', 7)
    AUTO = ('Auto', 8)
    REMOTE = ('Remote', 9)

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockEventSource"]:
        for mode in list(LockEventSource):
            if code in mode.codes:
                return mode


class LockVolumeLevel(Enum):
    """
    See: ford_lock_setting_volume
    """

    OFF = ('Off', 0)
    NORMAL = ('Normal', 50)
    HIGH = ('High', 100)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockVolumeLevel"]:
        for level in list(LockVolumeLevel):
            if code == level.code:
                return level


class LockLeftOpenTime(Enum):
    """
    See: ford_open_alarm_time
    """

    IMMEDIATE = ('At once', 1)
    MIN_1 = ('1 min', 2)
    MIN_5 = ('5 min', 3)
    MIN_10 = ('10 min', 4)
    MIN_30 = ('30 min', 5)
    MIN_60 = ('60 min', 6)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockLeftOpenTime"]:
        for item in list(LockLeftOpenTime):
            if code == item.code:
                return item


class LockKeyType(Enum):
    """
    See: com.yunding.ydbleapi.bean.KeyInfo.type
    """

    BLUETOOTH = ('Bluetooth', 1)
    ACCESS_CODE = ('Access Code', 2)
    FINGERPRINT = ('Fingerprint', 3)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockKeyType"]:
        for type in list(LockKeyType):
            if code == type.code:
                return type


class LockKeyState(Enum):
    """
    See: com.yunding.ydbleapi.bean.LockPasswordInfo.pwd_state
    """

    INIT = ('Init', 1)
    IN_USE = ('In use', 2)
    WILL_USE = ('Will use', 3)
    OUT_OF_PERMISSION = ('Out of permission', 4)
    FROZENED = ('Frozen', 5)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockKeyState"]:
        for state in list(LockKeyState):
            if code == state.code:
                return state


class LockKeyOperation(Enum):
    """
    See: com.yunding.ydbleapi.bean.LockPasswordInfo.operation
    """

    ADD = ('Add', 1)
    DELETE = ('Delete', 2)
    UPDATE = ('Update', 3)
    FROZEN = ('Freeze', 4)
    UNFROZEN = ('Unfreeze', 5)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockKeyOperation"]:
        for operation in list(LockKeyOperation):
            if code == operation.code:
                return operation


class LockKeyOperationStage(Enum):
    """
    See: com.yunding.ydbleapi.bean.LockPasswordInfo.operation_stage
    """

    GOING = ('Pending', 1)
    INVALID = ('Failure', 2)
    SUCCESS = ('Success', 3)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockKeyOperationStage"]:
        for stage in list(LockKeyOperationStage):
            if code == stage.code:
                return stage


class LockKeyPermissionType(Enum):
    """
    See: com.yunding.ydbleapi.bean.YDPermission.status
    """

    ALWAYS = ('Always', 1)
    DURATION = ('Temporary', 2)
    ONCE = ('One-Time', 3)
    RECURRING = ('Recurring', 4)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockKeyPermissionType"]:
        for type in list(LockKeyPermissionType):
            if code == type.code:
                return type

    def to_json(self):
        return self.code


class LockRecordDetail(JsonObject):
    """
    A lock record's details.

    See: com.yunding.ford.entity.FamilyRecord.Detail
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "avatar",
            "email",
            "left_open_time",
            "receiver_name",
            "role",
            "sender_name",
            "source",
            "source_name",
            "sourceid",
            "time",
            "audio_played",
        }

    def __init__(
        self,
        *,
        id: int = None,
        avatar: str = None,
        email: str = None,
        left_open_time: Optional[Union[int, LockLeftOpenTime]] = None,
        receiver_name: str = None,
        role: str = None,
        sender_name: str = None,
        source: Optional[Union[int, LockEventSource]] = None,
        source_name: str = None,
        sourceid: int = None,
        time: datetime = None,
        audio_played: int = None,
        **others: dict
    ):
        self.id = id if id else self._extract_attribute('id', others)
        self.avatar = avatar if avatar else self._extract_attribute('avatar', others)
        self.email = email if email else self._extract_attribute('email', others)
        if isinstance(left_open_time, LockLeftOpenTime):
            self.left_open_time = left_open_time
        else:
            self.left_open_time = LockLeftOpenTime.parse(left_open_time if left_open_time is not None else self._extract_attribute('left_open_time', others))
        self.receiver_name = receiver_name if receiver_name else self._extract_attribute('receiver_name', others)
        self.role = role if role else self._extract_attribute('role', others)
        self.sender_name = sender_name if sender_name else self._extract_attribute('sender_name', others)
        if isinstance(source, LockEventSource):
            self.source = source
        else:
            self.source = LockEventSource.parse(source if source is not None else self._extract_attribute('source', others))
        self.source_name = source_name if source_name else self._extract_attribute('source_name', others)
        self.sourceid = sourceid if sourceid else self._extract_attribute('sourceid', others)
        self.time = time if time else epoch_to_datetime(self._extract_attribute('time', others), ms=True)
        self.audio_played = audio_played if audio_played else self._extract_attribute('audio_played', others)
        show_unknown_key_warning(self, others)


class LockKeyPermission(JsonObject):
    """
    A lock key permission.

    See: com.yunding.ydbleapi.bean.YDPermission
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "type",
            "begin",
            "end",
        }

    def __init__(
        self,
        *,
        type: Optional[LockKeyPermissionType] = None,
        begin: Optional[Union[int, datetime]] = None,
        end: Optional[Union[int, datetime]] = None,
        **others: dict
    ):
        self.type = type if type is not None else LockKeyPermissionType.parse(self._extract_attribute('status', others))
        if isinstance(begin, datetime):
            self.begin = begin
        else:
            self.begin = epoch_to_datetime(begin if begin is not None else self._extract_attribute('begin', others), ms=True)
        if isinstance(end, datetime):
            self.end = end
        else:
            self.end = epoch_to_datetime(end if end is not None else self._extract_attribute('end', others), ms=True)
        show_unknown_key_warning(self, others)

    def to_json(self):
        to_return = {'status': self.type.to_json()}
        if self.type == LockKeyPermissionType.DURATION or self.type == LockKeyPermissionType.ONCE:
            if self.begin is not None:
                to_return['begin'] = int(self.begin.replace(microsecond=0).timestamp())
            if self.end is not None:
                to_return['end'] = int(self.end.replace(microsecond=0).timestamp())
        if self.type == LockKeyPermissionType.RECURRING:
            to_return['begin'] = 0
            to_return['end'] = 0
        return to_return


class LockKeyPeriodicity(JsonObject):
    """
    A lock key periodicity describing recurring access rules.

    See: com.yunding.ydbleapi.bean.PeriodicityInfo
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "type",
            "interval",
            "begin",
            "end",
            "valid_days",
        }

    def __init__(
        self,
        *,
        begin: Union[str, int, time] = None,
        end: Union[str, int, time] = None,
        valid_days: Union[int, Sequence[int]] = None,
        **others: dict
    ):
        self.type = 2
        self.interval = 1
        if isinstance(begin, time):
            self.begin = begin
        else:
            self.begin = str_to_time(begin if begin is not None else self._extract_attribute('begin', others))
        if isinstance(end, time):
            self.end = end
        else:
            self.end = str_to_time(end if end is not None else self._extract_attribute('end', others))
        if not isinstance(valid_days, (list, Tuple)):
            valid_days = [valid_days]
        self.valid_days = valid_days

        show_unknown_key_warning(self, others)

    def to_json(self):
        return {
            'type': self.type,
            'interval': self.interval,
            'begin': self.begin.replace(second=0, microsecond=0).strftime('%H%M%S'),
            'end': self.end.replace(second=0, microsecond=0).strftime('%H%M%S'),
            'valid_days': self.valid_days,
        }


class LockRecord(JsonObject):
    """
    A lock record.

    See: com.yunding.ford.entity.FamilyRecord
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "type",
            "detail",
            "priority",
            "processed",
            "time",
            "user_id",
            "uuid",
        }

    def __init__(
        self,
        *,
        type: Optional[Union[int, LockEventType]] = None,
        details: Optional[Union[dict, LockRecordDetail]] = None,
        priority: int = None,
        processed: int = None,
        time: datetime = None,
        user_id: str = None,
        uuid: str = None,
        **others: dict
    ):
        self.type = type if type is not None else self._extract_attribute('eventid', others)
        if isinstance(details, LockRecordDetail):
            self.details = details
        else:
            self.details = LockRecordDetail(**(details if details is not None else self._extract_attribute('detail', others)))
        self.priority = priority if priority is not None else self._extract_attribute('priority', others)
        self.processed = processed if processed is not None else self._extract_attribute('processed', others)
        if isinstance(time, datetime):
            self.time = time
        else:
            self.time = epoch_to_datetime(time if time is not None else self._extract_attribute('time', others), ms=True)
        self.user_id = user_id if user_id else self._extract_attribute('master', others)
        self.uuid = uuid if uuid else self._extract_attribute('uuid', others)
        show_unknown_key_warning(self, others)

    @property
    def type(self) -> LockEventType:
        return self._type

    @type.setter
    def type(self, value: Union[int, LockEventType]):
        if isinstance(value, int):
            value = LockEventType.parse(value)
        self._type = value


class LockKey(JsonObject):
    """
    A lock key. This can be either:
        * a Bluetooth connection
        * a password (hash of a numeric code)
        * a fingerprint
    BLE Actions:
        * freeze   (1)
            * permission_state = 5
            * operation = 4
        * unfreeze (2)
            * permission_state = 2
            * operation = 5
        * update   (3)
            * operation = 3
            * (set permission)
    Password Actions:
        * freeze   (1)
            * pwd_state = 5
            * operation = 4
            * operation_stage = 3
        * unfreeze (2)
            * pwd_state = 2
            * operation = 5
            * operation_stage = 3
        * update   (3)
            * operation = 3
            * operation_stage = 3
            * (set permission)
    Fingerprint Actions:
        * freeze   (1)
            * fp_state = 5
            * operation = 4
            * operation_stage = 3
        * unfreeze (2)
            * fp_state = 2
            * operation = 5
            * operation_stage = 3
        * update   (3)
            * operation = 3
            * operation_stage = 3
            * (set permission)

    See: com.yunding.ydbleapi.bean.KeyInfo
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "type",
            "time",
            "name",
            "description",
            "is_default",
            "notify",
            "userid",
            "username",
            "permission",
            "periodicity",
            "operation",
            "operation_stage",
            "permission_state",  # used with Bluetooth key
            "pwd_state",  # used with password key
        }

    def __init__(
        self,
        *,
        id: int = None,
        type: LockKeyType = None,
        time: datetime = None,
        name: str = None,
        description: str = None,
        is_default: Union[int, bool] = None,
        notify: Union[int, bool] = False,
        userid: str = None,
        username: str = None,
        permission: Union[dict, LockKeyPermission] = None,
        periodicity: Optional[Union[dict, LockKeyPeriodicity]] = None,
        operation: Union[int, LockKeyOperation] = None,
        operation_stage: Union[int, LockKeyOperationStage] = None,
        permission_state: Optional[Union[int, LockKeyState]] = None,
        pwd_state: Optional[Union[int, LockKeyState]] = None,
        **others: dict
    ):
        self.id = id if id is not None else self._extract_attribute('id', others)
        self.type = type
        if isinstance(time, datetime):
            self.time = time
        else:
            self.time = epoch_to_datetime(time if time is not None else self._extract_attribute('time', others), ms=True)
        self.name = name if name is not None else self._extract_attribute('name', others)
        self.description = description if description is not None else self._extract_attribute('description', others)
        self.is_default = is_default if is_default is not None else self._extract_attribute('is_default', others)
        self.notify = notify if notify is not None else self._extract_attribute('notify', others)
        self.userid = userid if userid else self._extract_attribute('userid', others)
        self.username = username if username else self._extract_attribute('username', others)
        if isinstance(permission, LockKeyPermission):
            self.permission = permission
        else:
            self.permission = LockKeyPermission(**permission) if permission is not None else LockKeyPermission(**self._extract_attribute('permission', others))
        if isinstance(periodicity, LockKeyPeriodicity):
            self.periodicity = periodicity
        else:
            periodicity = periodicity if periodicity is not None else self._extract_attribute('period_info', others)
            self.periodicity = LockKeyPeriodicity(**periodicity) if periodicity is not None else None
        if not isinstance(operation, LockKeyOperation):
            self.operation = LockKeyOperation.parse(operation if operation is not None else self._extract_attribute('operation', others))
        self.operation = operation
        if not isinstance(operation_stage, LockKeyOperationStage):
            self.operation_stage = LockKeyOperationStage.parse(operation_stage if operation_stage is not None else self._extract_attribute('operation_stage', others))
        self.operation_stage = operation_stage
        if not isinstance(permission_state, LockKeyState):
            self.permission_state = LockKeyState.parse(permission_state if permission_state is not None else self._extract_attribute('permission_state', others))
        self.permission_state = permission_state
        if not isinstance(pwd_state, LockKeyState):
            self.pwd_state = LockKeyState.parse(pwd_state if pwd_state is not None else self._extract_attribute('pwd_state', others))
        self.pwd_state = pwd_state
        show_unknown_key_warning(self, others)

    @property
    def is_default(self) -> bool:
        return self._is_default

    @is_default.setter
    def is_default(self, value: Union[int, bool]):
        if isinstance(value, int):
            value = True if value == 1 else False
        self._is_default = value

    @property
    def notify(self) -> bool:
        return self._notify

    @notify.setter
    def notify(self, value: Union[int, bool]):
        if isinstance(value, int):
            value = True if value == 1 else False
        self._notify = value


class LockKeypad(VoltageMixin, Device):

    type = "LockKeypad"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "uuid",
            "power",
            "is_enabled",
            "onoff_time",
            "power_refreshtime",
        })

    def __init__(
        self,
        is_enabled: bool = False,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.uuid = super()._extract_attribute("uuid", others)
        self.voltage = self._extract_property(prop_def=LockProps.voltage(), others=others)
        self.is_enabled = is_enabled
        self._is_online = self._extract_property(prop_def=LockProps.onoff_line(), others=others)
        show_unknown_key_warning(self, others)


class Lock(LockableMixin, ContactMixin, VoltageMixin, Device):

    type = "Lock"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "open_close_state",
            "open_close_ts",
            "switch_state",
            "switch_state_ts",
            "parent",
            "door_sensor",  # Auto-Lock -> Door Position
            "auto_lock_time",  # Auto-Lock -> Auto-Lock/Timing
            "trash_mode",  # Auto-Lock -> Trash Mode
            "auto_unlock",  # Auto-Unlock -> Auto-Unlock
            "keypad",
            "ajar_alarm",  # Alarm Settings -> Door Jam Alarm
            "left_open_time",  # Alarm Settings -> Left Open Alarm
            "door_open_status",
            "open_volume",
            "record_count",
        })

    @classmethod
    def parse_uuid(cls, mac: str) -> str:
        for model in DeviceModels.LOCK:
            if model in mac:
                return Lock.remove_model_prefix(mac, model + '.')

    def __init__(
        self,
        parent: Optional[str] = None,
        door_sensor: Union[int, bool] = None,
        auto_lock_time: Union[int, bool, LockLeftOpenTime] = None,
        trash_mode: Union[int, bool] = None,
        auto_unlock: Union[int, bool] = None,
        keypad: Optional[LockKeypad] = None,
        ajar_alarm: Union[int, bool] = None,
        left_open_time: Union[int, bool, LockLeftOpenTime] = None,
        open_volume: Union[int, LockVolumeLevel] = None,
        record_count: Optional[int] = None,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        if self.mac is not None:
            self._uuid = Lock.parse_uuid(self.mac)
        self.lock_state = self._extract_lock_state(others)
        self.open_close_state = self._extract_open_close_state(others)
        self.voltage = self._extract_property(prop_def=LockProps.voltage(), others=others)
        self._parent = parent if parent is not None else super()._extract_attribute("parent", others)
        if ajar_alarm is None:
            ajar_alarm = self._extract_attribute(name=LockProps.ajar_alarm().pid, others=others)
        self.ajar_alarm = True if ajar_alarm is True or ajar_alarm == 1 else False
        if isinstance(left_open_time, LockLeftOpenTime):
            self.left_open_time = left_open_time
        else:
            if left_open_time is None:
                left_open_time = self._extract_attribute(name=LockProps.left_open_time().pid, others=others)
            if left_open_time is False or isinstance(left_open_time, int) and left_open_time == 0:
                self.left_open_time = False
            else:
                self.left_open_time = LockLeftOpenTime.parse(left_open_time)
        if door_sensor is None:
            door_sensor = self._extract_attribute(name=LockProps.door_sensor().pid, others=others)
        self.door_sensor = True if door_sensor is True or door_sensor == 1 else False
        if isinstance(auto_lock_time, LockLeftOpenTime):
            self.auto_lock_time = auto_lock_time
        else:
            if auto_lock_time is None:
                auto_lock_time = self._extract_attribute(name=LockProps.auto_lock_time().pid, others=others)
            if auto_lock_time is False or isinstance(auto_lock_time, int) and auto_lock_time == 0:
                self.auto_lock_time = False
            else:
                self.auto_lock_time = LockLeftOpenTime.parse(auto_lock_time)
        if trash_mode is None:
            trash_mode = self._extract_attribute(name=LockProps.trash_mode().pid, others=others)
        self.trash_mode = True if trash_mode is True or trash_mode == 1 else False
        if auto_unlock is None:
            auto_unlock = self._extract_attribute(name=LockProps.auto_unlock().pid, others=others)
        self.auto_unlock = True if auto_unlock is True or auto_unlock == 1 else False
        if keypad is None:
            keypad = super()._extract_attribute("keypad", others)
            if keypad is not None:
                keypad_enable_status = super()._extract_attribute("keypad_enable_status", others)
                keypad = LockKeypad(**keypad, is_enabled=True if keypad_enable_status == 1 else False)
        self.keypad = keypad
        if isinstance(open_volume, LockVolumeLevel):
            self.open_volume = open_volume
        else:
            if open_volume is None:
                open_volume = self._extract_attribute(name=LockProps.open_volume().pid, others=others)
            self.open_volume = LockVolumeLevel.parse(open_volume)
        self._record_count = record_count if record_count is not None else super()._extract_attribute("record_count", others)
        show_unknown_key_warning(self, others)

    def _extract_lock_state(self, others: Union[dict, Sequence[dict]]) -> DeviceProp:
        if "device_params" in others and "locker_status" in others["device_params"]:
            self.logger.debug("found non-empty locker_status")
            prop_def = LockProps.locker_lock_state()
            value = super()._extract_property(prop_def=prop_def, others=others["device_params"]["locker_status"])
            ts = super()._extract_attribute(name=prop_def.pid + "_refreshtime", others=others["device_params"]["locker_status"])
            self.logger.debug(f"returning new DeviceProp with value {value.value}")
            return DeviceProp(definition=prop_def, ts=ts, value=value.value)
        # if switch_state == 1, device is UNlocked so we have to flip the bit
        prop = super()._extract_property(prop_def=LockProps.lock_state(), others=others)
        return DeviceProp(definition=prop.definition, ts=prop.ts, value=not prop.value)

    def _extract_open_close_state(self, others: Union[dict, Sequence[dict]]) -> DeviceProp:
        if "device_params" in others and "locker_status" in others["device_params"]:
            self.logger.debug("found non-empty locker_status")
            prop_def = LockProps.locker_open_close_state()
            value = super()._extract_property(prop_def=prop_def, others=others["device_params"]["locker_status"])
            ts = super()._extract_attribute(name=prop_def.pid + "_refreshtime", others=others["device_params"]["locker_status"])
            self.logger.debug(f"returning new DeviceProp with {value}")
            # door: 1 = open, 2 = closed, 255 = some unknown value
            return DeviceProp(definition=prop_def, ts=ts, value=value == 1)
        # open_close_state: 1 = closed 0 = open
        prop = super()._extract_property(prop_def=LockProps.open_close_state(), others=others)
        return DeviceProp(definition=prop.definition, ts=prop.ts, value=not prop.value)

    @property
    def parent(self) -> str:
        return self._parent

    @property
    def record_count(self) -> int:
        return self._record_count

    @property
    def is_locked(self) -> bool:
        # this is janky...a lock needs to store a lock status
        if super().lock_state is None:
            return False
        if isinstance(super().lock_state.definition.type, bool):
            return super().lock_state
            # return True if super().lock_state.value == 1 else True
        return super().lock_state.value == LockStatusType.LOCKED.code


class LockGateway(AbstractWirelessNetworkedDevice):

    type = "GateWay"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "uuid",
            "locks",
        })

    @classmethod
    def parse_uuid(cls, mac: str) -> str:
        for model in DeviceModels.LOCK_GATEWAY:
            if model in mac:
                return LockGateway.remove_model_prefix(mac, model + '.')

    def __init__(
        self,
        *,
        rssi: Optional[int] = None,
        ssid: Optional[str] = None,
        locks: Optional[Sequence[dict]] = None,
        **others: dict,
    ):
        if rssi is None or ssid is None:
            connection = super()._extract_attribute('connection', others)
            if connection is not None:
                rssi = super()._extract_attribute('wifi_signal', connection)
                ssid = super()._extract_attribute('ssid', connection)
        super().__init__(type=self.type, **others)
        if self.mac is not None:
            self._uuid = LockGateway.parse_uuid(self.mac)
        self.locks = locks if locks is not None else super()._extract_attribute('locks', others)
        show_unknown_key_warning(self, others)

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def locks(self) -> Sequence[Lock]:
        return self._locks

    @locks.setter
    def locks(self, value: Sequence[dict]):
        if value is not None:
            self._locks = [Lock(**lock) for lock in value]
