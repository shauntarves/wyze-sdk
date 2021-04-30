from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Set, Tuple, Union

from wyze_sdk.models import (JsonObject, epoch_to_datetime,
                             show_unknown_key_warning)


class EventAlarmType(Enum):
    """
    See: com.HLApi.Obj.EventItem
    """

    MOTION = ("Motion", [1, 6, 7, 13])
    SOUND = ("Sound", 2)
    OTHER = ("Other", 3)
    SMOKE = ("Smoke", 4)
    CO = ("Carbon Monoxide", 5)
    TRIGGERED = ("Triggered", 8)  # this applies for contact/motion sensors only
    DOORBELL_RANG = ("Doorbell rang", 10)
    SCENE = ("Scene action", 11)
    FACE = ("Face appeared", 12)

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["EventAlarmType"]:
        for mode in list(EventAlarmType):
            if code in mode.codes:
                return mode


class AiEventType(Enum):
    """
    See: com.wyze.platformkit.config.AiConfig
         com.wyze.event.faceai.WyzeCloudEventFaceAI
    """

    NOTHING = ("Nothing", 000000)
    PERSON = ("Person", 101)
    FACE = ("Face", 101001)
    VEHICLE = ("Vehicle", 102)
    PET = ("Pet", 103)
    PACKAGE = ("Package", 104)
    CRYING = ("Baby Crying", 800001)
    BARKING = ("Dog Barking", 800002)
    MEOWING = ("Cat Meowing", 800003)
    CAR = ("Car", [])
    SCHOOL_BUS = ("School Bus", [])
    DELIVERY_TRUCK = ("Delivery Truck", [])
    DOG = ("Dog", [])
    CAT = ("Cat", [])

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["AiEventType"]:
        for mode in list(AiEventType):
            if code in mode.codes:
                return mode


class EventFileType(Enum):
    """
    See: com.wyze.event.utils.WyzeEventPlayerHelper
    """

    IMAGE = ("Image", 1)
    VIDEO = ("Video", 2)

    def __init__(self, description: str, codes: Union[int, Sequence[int]]):
        self.description = description
        if isinstance(codes, (list, Tuple)):
            self.codes = codes
        else:
            self.codes = [codes]

    def describe(self):
        return self.description

    @classmethod
    def parse(cls, code: int) -> Optional["EventFileType"]:
        for mode in list(EventFileType):
            if code in mode.codes:
                return mode


class EventFile(JsonObject):
    """
    A file (photo, video) associated with a Wyze event.

    See: com.wyze.platformkit.model.WpkEventData
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "file_id",
            "type",
            "status",
            "url",
        }

    def __init__(
        self,
        *,
        file_id: str = None,
        type: int = None,
        status: int = None,
        url: str = None,
        **others: dict
    ):
        self.id = file_id if file_id else self._extract_attribute('file_id', others)
        self.type = type if type is not None else self._extract_attribute('type', others)
        self.status = status if status else self._extract_attribute('status', others)  # not used
        self.url = url if url else self._extract_attribute('url', others)
        show_unknown_key_warning(self, others)

    @property
    def type(self) -> EventFileType:
        return self._type

    @type.setter
    def type(self, value: int = None):
        self._type = EventFileType.parse(value)


class Event(JsonObject):
    """
    A Wyze event.

    See: com.wyze.platformkit.model.WpkEventData
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "device_mac",
            "device_model",
            "event_id",
            "event_ts",
            "event_category",
            "event_params",
            "event_value",
            "file_list",
            "tag_list",
            "read_state",
        }

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        device_mac: str = None,
        event_id: int = None,
        event_ts: datetime = None,
        event_category: int = None,
        event_params: dict = None,
        event_value: str = None,
        file_list: Sequence[dict] = None,
        tag_list: Sequence[int] = None,
        read_state: int = None,
        **others: dict
    ):
        self.id = event_id if event_id else self._extract_attribute('event_id', others)
        self.mac = device_mac if device_mac else self._extract_attribute('device_mac', others)
        self.time = event_ts if event_ts else epoch_to_datetime(self._extract_attribute('event_ts', others), ms=True)
        self.category = event_category if event_category else self._extract_attribute('event_category', others)
        self.parameters = event_params if event_params else self._extract_attribute('event_params', others)
        self.alarm_type = event_value if event_value else self._extract_attribute('event_value', others)
        self.files = file_list if file_list is not None else self._extract_attribute('file_list', others)
        self.tags = tag_list if tag_list is not None else self._extract_attribute('tag_list', others)
        self.is_read = (read_state if read_state is not None else self._extract_attribute('read_state', others)) == 1
        show_unknown_key_warning(self, others)

    @property
    def alarm_type(self) -> Sequence[EventFile]:
        return self._alarm_type

    @alarm_type.setter
    def alarm_type(self, value: Union[int, str]):
        if isinstance(value, int):
            self._alarm_type = EventAlarmType.parse(value)
        else:
            try:
                self._alarm_type = EventAlarmType.parse(int(value))
            except ValueError:
                self._logger.debug(f"could not cast value {value} into expected type {EventAlarmType.__class__}")

    @property
    def tags(self) -> Sequence[AiEventType]:
        return self._tags

    @tags.setter
    def tags(self, value: Sequence[int] = []):
        self._tags = [AiEventType.parse(tag) for tag in value]

    @property
    def files(self) -> Sequence[EventFile]:
        return self._files

    @files.setter
    def files(self, value: Sequence[dict] = []):
        self._files = [EventFile(**file) for file in value]
