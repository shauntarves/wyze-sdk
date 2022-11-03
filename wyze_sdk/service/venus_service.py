from __future__ import annotations

import datetime
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.models import datetime_to_epoch
from wyze_sdk.models.devices.vacuums import VacuumDeviceControlRequestType, VacuumDeviceControlRequestValue

from .base import ExServiceClient, WyzeResponse


class VenusServiceClient(ExServiceClient):
    """
    Venus service client is the wrapper on the requests to https://wyze-venus-service-vn.wyzecam.com
    """
    WYZE_API_URL = "https://wyze-venus-service-vn.wyzecam.com"
    WYZE_APP_ID = "venp_4c30f812828de875"
    WYZE_VENUS_PLUGIN_VERSION = "2.35.1"
    WYZE_VACUUM_FIRMWARE_VERSION = "1.6.113"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
        app_id: str = WYZE_APP_ID,
    ):
        super().__init__(token=token, base_url=base_url, app_id=app_id)

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        params: dict = None,
        json: dict = None,
        request_specific_headers: Optional[dict] = None,
    ) -> WyzeResponse:
        nonce = self.request_verifier.clock.nonce()

        return super().api_call(
            api_method,
            http_verb=http_verb,
            params=params,
            json=json,
            headers=self._get_headers(request_specific_headers=request_specific_headers, nonce=nonce),
            nonce=nonce,
        )

    def control(self, *, did: str, type: VacuumDeviceControlRequestType, value: VacuumDeviceControlRequestValue, rooms: Union[int, Sequence[int]] = None, **kwargs) -> WyzeResponse:
        """
        The client command to issue commands to the device.

        The rooms should be specified as an array of integers, as identified by the
        current map.

        Actions defined in the app are:

        FOR ALL:
        type: VacuumDeviceControlRequestType.RETURN_TO_CHARGING:
            value: VacuumDeviceControlRequestValue.START (Recharge Start)
            value: VacuumDeviceControlRequestValue.STOP
                mode 5: Recharge Stop Manual Recharge
                mode 10,32,1103,1203,1303,1403: Recharge Stop Finish Recharge
                mode 11,33,1104,1204,1304,1404 AND charge_state 0: Recharge Stop Break Recharge
                mode 11,33,1104,1204,1304,1404 AND charge_state 1: Recharge Stop Break Charging

        FOR VACUUM (i12 == 0):
        type: VacuumDeviceControlRequestType.GLOBAL_SWEEPING:
            if no rooms selected:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
            if rooms selected:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
        type: VacuumDeviceControlRequestType.AREA_CLEAN:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
        FOR MOP (i12 == 2):
        type: VacuumDeviceControlRequestType.GLOBAL_SWEEPING:
            if no rooms selected:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
            if rooms selected:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
        type: VacuumDeviceControlRequestType.AREA_CLEAN:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
        FOR HURRICANE (i12 == 1):
        type: VacuumDeviceControlRequestType.GLOBAL_SWEEPING:
            if no rooms selected:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
            if rooms selected:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE
        type: VacuumDeviceControlRequestType.AREA_CLEAN:
            value: VacuumDeviceControlRequestValue.START (resume)
            value: VacuumDeviceControlRequestValue.PAUSE
            value: VacuumDeviceControlRequestValue.FALSE_PAUSE

        Ref: com.wyze.sweeprobot.common.entity.model.request.VenusDeviceControlRequest
        Ref: k(int i10, int i11, int i12)
        """
        kwargs.update({
            'type': type.code,
            'value': value.code,
            'vacuumMopMode': 0,
        })
        if rooms is not None:
            if not isinstance(rooms, (list, Tuple)):
                rooms = [rooms]
            kwargs.update({"rooms_id": rooms})
        return self.api_call(f'/plugin/venus/{did}/control', http_verb="POST", json=kwargs)

    def get_maps(self, *, did: str, **kwargs) -> WyzeResponse:
        kwargs.update({'did': did})
        return self.api_call('/plugin/venus/memory_map/list', http_verb="GET", params=kwargs)

    def get_current_position(self, *, did: str, **kwargs) -> WyzeResponse:
        kwargs.update({'did': did})
        return self.api_call('/plugin/venus/memory_map/current_position', http_verb="GET", params=kwargs)

    def get_current_map(self, *, did: str, **kwargs) -> WyzeResponse:
        kwargs.update({'did': did})
        return self.api_call('/plugin/venus/memory_map/current_map', http_verb="GET", params=kwargs)

    def set_current_map(self, *, did: str, map_id: int, **kwargs) -> WyzeResponse:
        kwargs.update({'device_id': did, 'map_id': map_id})
        return self.api_call('/plugin/venus/memory_map/current_map', http_verb="POST", json=kwargs)

    def get_sweep_records(self, *, did: str, keys: Union[str, Sequence[str]], limit: int = 20, since: datetime, **kwargs) -> WyzeResponse:
        # if isinstance(keys, (list, Tuple)):
        #     kwargs.update({"keys": ",".join(keys)})
        # else:
        #     kwargs.update({"keys": keys})
        kwargs.update({
            'did': did,
            "purpose": "history_map",
            "count": limit,
            "last_time": datetime_to_epoch(since)
        })
        return self.api_call('/plugin/venus/sweep_record/query_data', http_verb="GET", params=kwargs)

    def get_iot_prop(self, *, did: str, keys: Union[str, Sequence[str]], **kwargs) -> WyzeResponse:
        if isinstance(keys, (list, Tuple)):
            kwargs.update({"keys": ",".join(keys)})
        else:
            kwargs.update({"keys": keys})
        kwargs.update({'did': did})
        return self.api_call('/plugin/venus/get_iot_prop', http_verb="GET", params=kwargs)

    def get_device_info(self, *, did: str, keys: Union[str, Sequence[str]], **kwargs) -> WyzeResponse:
        if isinstance(keys, (list, Tuple)):
            kwargs.update({"keys": ",".join(keys)})
        else:
            kwargs.update({"keys": keys})
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/venus/device_info', http_verb="GET", params=kwargs)

    def get_status(self, *, did: str, **kwargs) -> WyzeResponse:
        return self.api_call(f'/plugin/venus/{did}/status', http_verb="GET", params=kwargs)

    def set_iot_action(self, *, did: str, model: str, cmd: str, params: Union[dict, Sequence[dict]], is_sub_device: bool = False, **kwargs) -> WyzeResponse:
        if isinstance(params, (list, Tuple)):
            kwargs.update({"params": params})
        else:
            kwargs.update({"params": [params]})
        kwargs.update({
            'cmd': cmd,
            'did': did,
            'model': model,
            'is_sub_device': 1 if is_sub_device else 0,
        })
        return self.api_call('/plugin/venus/set_iot_action', http_verb="POST", json=kwargs)

    def _create_event(self, *, did: str, type: VacuumDeviceControlRequestType, value: VacuumDeviceControlRequestValue, args: Union[str, Sequence[str]] = None, **kwargs) -> WyzeResponse:
        kwargs.update({
            'uuid': '88DBF3344D20B5597DB7C8F0AFBB4030',
            'deviceId': did,
            'createTime': str(self.request_verifier.clock.nonce()),
            'mcuSysVersion': self.WYZE_VACUUM_FIRMWARE_VERSION,
            'appVersion': self.app_version,
            'pluginVersion': self.WYZE_VENUS_PLUGIN_VERSION,
            'phoneId': self.phone_id,
            'phoneOsVersion': '16.0',
            'eventKey': type.description,
            'eventType': value.code,
        })
        if args is not None:
            if not isinstance(args, (list, Tuple)):
                args = [args]
            for index, item in enumerate(args):
                kwargs.update({
                    f'arg{index + 1}': item
                })
        kwargs.update({
            "arg11": "ios",
            "arg12": "iPhone 13 mini",
        })
        return self.api_call('/plugin/venus/event_tracking', http_verb="POST", json=kwargs)
