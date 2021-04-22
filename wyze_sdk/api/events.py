from itertools import groupby
from typing import Sequence, Tuple, Union

from wyze_sdk.models.events import (Event)
from wyze_sdk.api.base import BaseClient, WyzeResponse


class EventsClient(BaseClient):
    """A Client that manages Wyze events.

    Methods:
        list: Lists & filters events
        mark_read: Marks events as read
        mark_unread: Marks events as unread
    """

    def list(self, **kwargs) -> Sequence[Event]:
        """Lists & filters events.

        Args:
            device_ids (Sequence[str]): The device mac(s) for filtering events. e.g. ['ABCDEF1234567890', 'ABCDEF1234567891']
            event_values (Union[EventAlarmType, Sequence[EventAlarmType]]): The alarm types to incude. e.g. [EventAlarmType.MOTION, EventAlarmType.SOUND]
            begin: (datetime): The start of the event filter date/time range.
              Defaults to 24 hours before now
            end: (datetime): The end of the event filter date/time range.
              Defaults to now
            limit: (int): The number of event records to return.
              Defaults to, and cannot exceed, 20
            order_by: (int): The order ([1] chronological or [2] reverse-chronological) of the record query.
              Defaults to 2 (reverse chronological)

        Returns:
            (Sequence[Event])
        """
        return [Event(**event) for event in super()._api_client().get_event_list(**kwargs).data["data"]["event_list"]]

    def mark_read(self, *, events: Union[Event, Sequence[Event]], **kwargs) -> WyzeResponse:
        """Marks events as read.

        Args:
            events (Union[Event, Sequence[Event]]): The events to mark read.
        """
        if not isinstance(events, (list, Tuple)):
            events = [events]

        return super()._api_client().set_read_state_list(
            events=groupby(events, key=lambda event: event.mac), read_state=True)

    def mark_unread(self, *, events: Union[Event, Sequence[Event]], **kwargs) -> WyzeResponse:
        """Marks events as unread.

        Args:
            events (Union[Event, Sequence[Event]]): The events to mark unread.
        """
        if not isinstance(events, (list, Tuple)):
            events = [events]

        return super()._api_client().set_read_state_list(
            events=groupby(events, key=lambda event: event.mac), read_state=False)
