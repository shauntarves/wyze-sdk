from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Set, Tuple, Union

from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime, show_unknown_key_warning)

from .base import (AbstractWirelessNetworkedDevice, ContactMixin, Device, DeviceModels, LockableMixin)


class LockProps(object):

    @classmethod
    @property
    def lock_state(cls) -> PropDef:
        return PropDef("switch_state", bool, str)

    @classmethod
    @property
    def open_close_state(cls) -> PropDef:
        return PropDef("open_close_state", bool, str)


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

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockEventType"]:
        for mode in list(LockEventType):
            if code in mode.codes:
                return mode


class LockEventSource(Enum):
    """
    See: ford_lock_history_source
    """

    LOCAL = ('Local', 1)
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


class LockLeftOpenTime(Enum):
    """
    See: ford_open_alarm_time
    """

    MIN_1 = ('1 min', 2)
    MIN_5 = ('5 min', 3)
    MIN_10 = ('10 min', 4)
    MIN_30 = ('30 min', 5)
    MIN_60 = ('60 min', 6)

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["LockLeftOpenTime"]:
        for mode in list(LockLeftOpenTime):
            if code in mode.codes:
                return mode


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
        show_unknown_key_warning(self, others)


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
        elif details is not None:
            LockRecordDetail(**details)
        else:
            self.details = LockRecordDetail(**self._extract_attribute('detail', others))
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


class Lock(LockableMixin, ContactMixin, Device):

    type = "Lock"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "open_close_state",
            "open_close_ts",
            "switch_state",
            "switch_state_ts",
            "parent",
            "record_count",
        })

    @classmethod
    def parse_uuid(cls, mac: str) -> str:
        for model in DeviceModels.LOCK:
            if model in mac:
                return mac.removeprefix(model + '.')

    def __init__(
        self,
        parent: Optional[str] = None,
        record_count: Optional[int] = None,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        if self.mac is not None:
            self._uuid = Lock.parse_uuid(self.mac)
        self.lock_state = super()._extract_property(LockProps.lock_state, others)
        self.open_close_state = super()._extract_property(LockProps.open_close_state, others)
        self._parent = parent if parent is not None else super()._extract_attribute("parent", others)
        self._record_count = record_count if record_count is not None else super()._extract_attribute("record_count", others)
        show_unknown_key_warning(self, others)

    @property
    def parent(self) -> str:
        return self._parent

    @property
    def record_count(self) -> int:
        return self._record_count


class LockGateway(AbstractWirelessNetworkedDevice):

    type = "gateway"

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
                return mac.removeprefix(model + '.')

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
            for model in DeviceModels.LOCK_GATEWAY:
                self._uuid = self.mac.removeprefix(model + '.')
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
        self._locks = [Lock(**lock) for lock in value]
