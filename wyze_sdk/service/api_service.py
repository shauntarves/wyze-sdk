import logging

from datetime import datetime, timedelta
from time import strftime, gmtime
from typing import Any, Dict, Optional, Sequence, Tuple, Union
from wyze_sdk.models.events import EventAlarmType
from wyze_sdk.signature import RequestVerifier

from wyze_sdk.errors import WyzeRequestError
from wyze_sdk.models import datetime_to_epoch
from wyze_sdk.models.devices import DeviceProp

from .base import BaseServiceClient, WyzeResponse


class ApiServiceClient(BaseServiceClient):
    """
    Wyze api client is the wrapper on the requests to https://api.wyzecam.com
    """

    SC = "a626948714654991afd3c0dbd7cdb901"
    WYZE_API_URL = "https://api.wyzecam.com/"
    WYZE_APP_NAME = "com.hualai"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
        app_name: str = WYZE_APP_NAME,
        sc: str = SC,
    ):
        super().__init__(token=token, base_url=base_url, app_name=app_name, request_verifier=RequestVerifier(signing_secret=None))
        self.app_ver = self.app_name + '___' + self.app_version
        self.sc = sc

    def _get_headers(
        self,
        *,
        request_specific_headers: Optional[dict]
    ) -> Dict[str, str]:
        return super()._get_headers(headers=None, has_json=True, request_specific_headers=request_specific_headers)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        json: dict = {},
        headers: dict = None,
    ) -> WyzeResponse:
        json['access_token'] = self.token
        json['app_name'] = self.app_name
        json['app_ver'] = self.app_ver
        json['app_version'] = self.app_version
        json['phone_id'] = self.phone_id
        json['phone_system_type'] = str(self.phone_type)
        json['sc'] = self.sc
        json['ts'] = self.request_verifier.clock.nonce()

        headers = self._get_headers(
            request_specific_headers={
                'Connection': 'keep-alive',
            }
        )

        return super().api_call(api_method, http_verb=http_verb, data=None, params=None, json=json, headers=headers, auth=None)

    def refresh_token(self, *, refresh_token: str, **kwargs) -> WyzeResponse:
        SV_REFRESH_TOKEN = 'd91914dd28b7492ab9dd17f7707d35a3'

        kwargs.update({"refresh_token": refresh_token, "sv": SV_REFRESH_TOKEN})
        return self.api_call('/app/user/refresh_token', json=kwargs)

    def set_device_property(self, *, mac: str, model: str, pid: str, value: Any, **kwargs) -> WyzeResponse:
        SV_SET_DEVICE_PROPERTY = '44b6d5640c4d4978baba65c8ab9a6d6e'

        kwargs.update({"device_mac": mac, "device_model": model, "pid": pid, "pvalue": str(value), "sv": SV_SET_DEVICE_PROPERTY})
        return self.api_call('/app/v2/device/set_property', json=kwargs)

    def get_device_list_property_list(self, *, device_ids: Sequence[str], target_pids: Sequence[str], **kwargs) -> WyzeResponse:
        SV_GET_DEVICE_LIST_PROPERTY_LIST = 'be9e90755d3445d0a4a583c8314972b6'

        kwargs.update({"device_list": device_ids, "target_pid_list": target_pids, "sv": SV_GET_DEVICE_LIST_PROPERTY_LIST})
        return self.api_call('/app/v2/device_list/get_property_list', json=kwargs)

    def get_device_property_list(self, *, mac: str, model: str, target_pids: Sequence[str] = [], **kwargs) -> WyzeResponse:
        SV_GET_DEVICE_PROPERTY_LIST = '1df2807c63254e16a06213323fe8dec8'

        kwargs.update({"device_mac": mac, "device_model": model, "sv": SV_GET_DEVICE_PROPERTY_LIST})
        if target_pids is not None:
            kwargs.update({"target_pid_list": target_pids})

        return self.api_call('/app/v2/device/get_property_list', json=kwargs)

    def get_v1_device_info(self, *, mac: str, **kwargs) -> WyzeResponse:
        SV_GET_DEVICE_INFO = '90fea740c4c045f9a3084c17cee71d46'

        kwargs.update({"device_mac": mac, "sv": SV_GET_DEVICE_INFO})
        return self.api_call('/app/device/get_device_info', json=kwargs)

    def get_device_info(self, *, mac: str, model: str, **kwargs) -> WyzeResponse:
        SV_GET_DEVICE_INFO = '81d1abc794ba45a39fdd21233d621e84'

        kwargs.update({"device_mac": mac, "device_model": model, "sv": SV_GET_DEVICE_INFO})
        return self.api_call('/app/v2/device/get_device_Info', json=kwargs)

    def get_object_list(self, **kwargs) -> WyzeResponse:
        SV_GET_DEVICE_LIST = 'c417b62d72ee44bf933054bdca183e77'

        kwargs.update({"sv": SV_GET_DEVICE_LIST})
        return self.api_call(
            '/app/v2/home_page/get_object_list', json=kwargs)

    def get_device_timer(self, *, mac: str, action_type: int, **kwargs) -> WyzeResponse:
        """
        "data": {
            "action_value": "1",
            "delay_time": 10800,
            "plan_execute_ts": 1618169169544
        },
        """
        SV_GET_DEVICE_TIMER = 'ddd49252f61944dc9c46d1a770a5980f'

        kwargs.update({"device_mac": mac, "action_type": action_type, "sv": SV_GET_DEVICE_TIMER})
        return self.api_call('/app/v2/device/timer/get', json=kwargs)

    def set_device_timer(self, *, mac: str, delay_time: int, action_value: int, **kwargs) -> WyzeResponse:
        """
        action_value: 0=off, 1=on

        See: com.HLApi.CloudAPI.CloudProtocol.deviceTimerSet
        """
        SV_SET_DEVICE_TIMER = 'b4810ce03e7747669fdc4644e554fd23'

        kwargs.update({
            "device_mac": mac,
            "action_type": 1,
            "action_value": action_value,
            "delay_time": delay_time,
            "plan_execute_ts": datetime_to_epoch(datetime.now() + timedelta(seconds=delay_time)),
            "sv": SV_SET_DEVICE_TIMER
        })
        return self.api_call('/app/v2/device/timer/set', json=kwargs)

    def get_device_group_timer(self, *, id: int, action_type: int, **kwargs) -> WyzeResponse:
        """
        "data": {
            "action_value": "1",
            "delay_time": 10800,
            "plan_execute_ts": 1618169169544
        },
        """
        SV_GET_DEVICE_GROUP_TIMER = 'bf55bbf1db0e4fa18cc7a13022de33a3'

        kwargs.update({"group_id": str(id), "action_type": action_type, "sv": SV_GET_DEVICE_GROUP_TIMER})
        return self.api_call('/app/v2/device_group/timer/get', json=kwargs)

    def cancel_device_timer(self, *, mac: str, action_type: int, **kwargs) -> WyzeResponse:
        SV_CANCEL_DEVICE_TIMER = '3f97925c690740f4aff91da765087db5'

        kwargs.update({"device_mac": mac, "action_type": action_type, "sv": SV_CANCEL_DEVICE_TIMER})
        return self.api_call('/app/v2/device/timer/cancel', json=kwargs)

    def get_smoke_event_list(self, *, device_ids: Sequence[str] = [], begin: Optional[datetime] = None, end: Optional[datetime] = None, limit: Optional[int] = 20, order_by: Optional[int] = 2, **kwargs) -> WyzeResponse:
        return self.get_event_list(device_ids=device_ids, event_values=EventAlarmType.SMOKE, begin=begin, end=end, limit=limit, order_by=order_by)

    def get_sound_event_list(self, *, device_ids: Sequence[str] = [], begin: Optional[datetime] = None, end: Optional[datetime] = None, limit: Optional[int] = 20, order_by: Optional[int] = 2, **kwargs) -> WyzeResponse:
        return self.get_event_list(device_ids=device_ids, event_values=EventAlarmType.SOUND, begin=begin, end=end, limit=limit, order_by=order_by)

    def get_co_event_list(self, *, device_ids: Sequence[str] = [], begin: Optional[datetime] = None, end: Optional[datetime] = None, limit: Optional[int] = 20, order_by: Optional[int] = 2, **kwargs) -> WyzeResponse:
        return self.get_event_list(device_ids=device_ids, event_values=EventAlarmType.CO, begin=begin, end=end, limit=limit, order_by=order_by)

    def get_motion_event_list(self, *, device_ids: Sequence[str] = [], begin: Optional[datetime] = None, end: Optional[datetime] = None, limit: Optional[int] = 20, order_by: Optional[int] = 2, **kwargs) -> WyzeResponse:
        return self.get_event_list(device_ids=device_ids, event_values=EventAlarmType.MOTION, begin=begin, end=end, limit=limit, order_by=order_by)

    def get_event_list(self, *, device_ids: Sequence[str] = [], event_values: Union[EventAlarmType, Sequence[EventAlarmType]] = [], event_tags: Sequence[str] = [], event_type: str = "1", begin: Optional[datetime] = None, end: Optional[datetime] = None, limit: int = 20, order_by: int = 2, **kwargs) -> WyzeResponse:
        SV_GET_EVENT_LIST = 'bdcb412e230049c0be0916e75022d3f3'

        if limit < 1 or limit > 20:
            raise WyzeRequestError(f"limit {limit} must be between 1 and 20")
        if order_by not in [1, 2]:
            raise WyzeRequestError(f"order_by {order_by} must be one of {[1, 2]}")
        if begin is None:
            begin = datetime.now() - timedelta(days=1)
        if end is None:
            end = datetime.now()
        if isinstance(event_values, (list, Tuple)):
            kwargs.update({
                "event_value_list": [code for alarm_type in event_values for code in alarm_type.codes]
            })
        else:
            kwargs.update({"event_value_list": [code for code in event_values.codes]})
        kwargs.update({
            "device_mac_list": device_ids,
            'begin_time': datetime_to_epoch(begin),
            "event_tag_list": event_tags,
            "event_type": event_type,
            'end_time': datetime_to_epoch(end),
            'order_by': order_by,
            'count': limit,
            "sv": SV_GET_EVENT_LIST,
        })
        return self.api_call('/app/v2/device/get_event_list', json=kwargs)

    def set_read_state_list(self, *, events: dict[str, Sequence[str]], read_state: bool = True, **kwargs) -> WyzeResponse:
        SV_SET_READ_STATE_LIST = '1e9a7d77786f4751b490277dc3cfa7b5'

        kwargs.update({
            "event_list": [{
                "device_mac": mac,
                "event_id_list": [event.id for event in events],
                "event_type": 1
            } for mac, events in events],
            "read_state": 1 if read_state else 0,
            "sv": SV_SET_READ_STATE_LIST,
        })
        return self.api_call('/app/v2/device_event/set_read_state_list', json=kwargs)

    def run_action(self, *, mac: str, action_key: str, action_params: Optional[dict] = {}, custom_string: Optional[str] = None, provider_key: str, **kwargs) -> WyzeResponse:
        SV_RUN_ACTION = '011a6b42d80a4f32b4cc24bb721c9c96'

        kwargs.update({
            "instance_id": mac,
            "action_key": action_key,
            "provider_key": provider_key,
            "sv": SV_RUN_ACTION
        })
        kwargs.update({"action_params": action_params})
        if custom_string is not None:
            kwargs.update({"custom_string": custom_string})
        return self.api_call('/app/v2/auto/run_action', json=kwargs)

    def run_action_list(self, *, actions: Union[dict[str, dict[str, DeviceProp]], Sequence[dict[str, dict[str, DeviceProp]]]], custom_string: Optional[str] = None, **kwargs) -> WyzeResponse:
        SV_RUN_ACTION_LIST = '5e02224ae0c64d328154737602d28833'

        kwargs.update({
            "action_list": [],
            "sv": SV_RUN_ACTION_LIST
        })
        if not isinstance(actions, (list, Tuple)):
            actions = [actions]
        for action in actions:
            kwargs["action_list"].append({
                "action_key": action["key"],
                "action_params": {
                    "list": [
                        {
                            "mac": action["device_mac"],
                            "plist": [
                                {
                                    "pid": action["prop"].definition.pid,
                                    "pvalue": str(action["prop"].api_value),
                                }
                            ]
                        }
                    ]
                },
                "instance_id": action["device_mac"],
                "provider_key": action["provider_key"],
            })
        if custom_string is not None:
            kwargs.update({"custom_string": custom_string})
        return self.api_call('/app/v2/auto/run_action_list', json=kwargs)


class AwayModeGenerator(object):

    cursor_time = None
    remain_time = None
    _logger = logging.getLogger(__name__)

    @property
    def value(self) -> Sequence[str]:
        _values = []

        local_am_start = datetime(1970, 1, 1, 6, 0, 0)
        local_am_end = datetime(1970, 1, 1, 9, 0, 0)
        local_pm_start = datetime(1970, 1, 1, 18, 0, 0)
        local_pm_end = datetime(1970, 1, 1, 23, 0, 0)

        self._calculate_away_mode(_values, local_am_start, local_am_end)
        self._remove_unreasonable_data(_values, local_am_end)
        self._calculate_away_mode(_values, local_pm_start, local_pm_end)
        self._remove_unreasonable_data(_values, local_pm_end)

        value = []
        i2 = 1
        for _value in _values:
            value.append(f"{strftime('%H%M', gmtime(_value))}{i2}")
            i2 ^= 1  # adds the on/off bit

        print(f"value returning={value}")
        return value

    def _calculate_away_mode(self, arrayList: list, local_start: datetime, local_end: datetime) -> Sequence[str]:
        """
        See: com.hualai.wlpp1.u2.b
        """
        gmt_start_time = local_start.timestamp()
        gmt_end_time = local_end.timestamp()
        self.remain_time = gmt_end_time - gmt_start_time
        self.cursor_time = gmt_start_time
        z = False
        while (True):
            if z:
                arrayList.append(self._randomize(3600, 60, gmt_end_time))
                z = not z
            elif (self.remain_time <= 900):
                return arrayList
            else:
                arrayList.append(self._randomize(3600, 60, gmt_end_time))
                z = not z

    def _remove_unreasonable_data(self, arrayList: list[float], local_end: datetime):
        if arrayList is not None and len(arrayList) >= 2:
            last_data = arrayList[len(arrayList) - 1] + self._local_timezone_in_seconds
            self._logger.debug(f"remove_unreasonable_data last_data={last_data} local_end={local_end}")
            if last_data > local_end.timestamp():
                self._logger.debug(f"remove_unreasonable_data item {arrayList[len(arrayList) + -1]}")
                del arrayList[len(arrayList) + -1]
                del arrayList[len(arrayList) + -1]

    @property
    def _local_timezone_in_seconds(self) -> int:
        return (datetime.now() - datetime.utcnow()).total_seconds()

    def _randomize(self, seconds_per_hour: float, seconds_per_minute: float, end_time: float) -> int:
        import random
        self._logger.debug(f"_randomize remain_time={self.remain_time}")
        self._logger.debug(f"_randomize cursor_time={self.cursor_time}")
        minutes_remaining = 60.0 if self.remain_time - seconds_per_hour >= 0 else (self.remain_time % seconds_per_hour) / seconds_per_minute
        self._logger.debug(f"_randomize minutes_remaining={minutes_remaining}")
        random = self.cursor_time + (
            ((random.random() * (minutes_remaining - 5)) + 5.0) * seconds_per_minute
        )
        self.cursor_time = random
        self.remain_time = end_time - (random + seconds_per_minute)
        return self.cursor_time
