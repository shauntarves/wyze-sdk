from __future__ import annotations

import datetime
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.models import datetime_to_epoch

from .base import ExServiceClient, WyzeResponse


class VenusServiceClient(ExServiceClient):
    """
    Venus service client is the wrapper on the requests to https://wyze-venus-service-vn.wyzecam.com
    """
    WYZE_API_URL = "https://wyze-venus-service-vn.wyzecam.com"
    WYZE_APP_ID = "venp_4c30f812828de875"

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

    def sweep_rooms(self, *, did: str, rooms: Union[int, Sequence[int]], **kwargs) -> WyzeResponse:
        """
        The client command to sweep specific room(s). The rooms should
        be specified as an array of integers, as identified by the
        current map.

        Ref: com.wyze.sweeprobot.model.request.VenusSweepByRoomRequest
        """
        if isinstance(rooms, (list, Tuple)):
            kwargs.update({"rooms_id": rooms})
        else:
            kwargs.update({"rooms_id": [rooms]})
        kwargs.update({'did': did, 'type': 1, 'value': 1})
        return self.api_call('/plugin/venus/sweeping', http_verb="POST", json=kwargs)
