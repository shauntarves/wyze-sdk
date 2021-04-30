from itertools import groupby
from typing import Sequence, Tuple, Union

from wyze_sdk.api.base import BaseClient, WyzeResponse
from wyze_sdk.models.events import Event


class EventsClient(BaseClient):
    """A Client that manages Wyze events.
    """

    def list(self, **kwargs) -> Sequence[Event]:
        """Lists & filters events.

        :param device_ids: The device mac(s) for filtering events. e.g. ``['ABCDEF1234567890', 'ABCDEF1234567891']``
        :type device_ids: Sequence[str]
        :param event_values: The alarm types to incude. e.g. ``[EventAlarmType.MOTION, EventAlarmType.SOUND]``
        :type event_values: Union[EventAlarmType, Sequence[EventAlarmType]]
        :param datetime begin: The start of the event filter date/time range. Defaults to 24 hours before now
        :param datetime end: The end of the event filter date/time range. Defaults to now
        :param int limit: The number of event records to return. Defaults to, and cannot exceed, 20
        :param int order_by: The order ([``1``] chronological or [``2``] reverse-chronological) of the record query. Defaults to ``2`` (reverse chronological)

        :rtype: Sequence[Event]
        """
        return [Event(**event) for event in super()._api_client().get_event_list(**kwargs).data["data"]["event_list"]]

    def mark_read(self, *, events: Union[Event, Sequence[Event]], **kwargs) -> WyzeResponse:
        """Marks events as read.

        :param events: The events to mark read.
        :type events: Union[Event, Sequence[Event]]

        :rtype: WyzeResponse
        """
        if not isinstance(events, (list, Tuple)):
            events = [events]

        return super()._api_client().set_read_state_list(
            events=groupby(events, key=lambda event: event.mac), read_state=True)

    def mark_unread(self, *, events: Union[Event, Sequence[Event]], **kwargs) -> WyzeResponse:
        """Marks events as unread.

        :param events: The events to mark unread.
        :type events: Union[Event, Sequence[Event]]

        :rtype: WyzeResponse
        """
        if not isinstance(events, (list, Tuple)):
            events = [events]

        return super()._api_client().set_read_state_list(
            events=groupby(events, key=lambda event: event.mac), read_state=False)
