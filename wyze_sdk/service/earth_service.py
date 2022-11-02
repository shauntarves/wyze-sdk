from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union

from .base import ExServiceClient, WyzeResponse


class EarthServiceClient(ExServiceClient):
    """
    Earth service client is the wrapper on the requests to https://wyze-earth-service.wyzecam.com
    """
    WYZE_API_URL = "https://wyze-earth-service.wyzecam.com"
    WYZE_APP_ID = "earp_9b66f89647d35e43"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = WYZE_API_URL,
    ):
        super().__init__(token=token, base_url=base_url)

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

    def get_device_info(self, *, did: Union[str, Sequence[str]], parent_did: str = None, model: str = None, keys: Union[str, Sequence[str]], **kwargs) -> WyzeResponse:
        if isinstance(keys, (list, Tuple)):
            kwargs.update({"keys": ",".join(keys)})
        else:
            kwargs.update({"keys": keys})
        if isinstance(did, (list, Tuple)):
            kwargs.update({
                "device_id": ",".join(did),
                'parent_device_id': parent_did,
                'model': model,
            })
            return self.api_call('/plugin/earth/device_info/batch', http_verb="GET", params=kwargs)
        kwargs.update({"device_id": did})
        return self.api_call('/plugin/earth/device_info', http_verb="GET", params=kwargs)

    def get_iot_prop(self, *, did: Union[str, Sequence[str]], parent_did: str = None, model: str = None, keys: Union[str, Sequence[str]], **kwargs) -> WyzeResponse:
        if isinstance(keys, (list, Tuple)):
            kwargs.update({"keys": ",".join(keys)})
        else:
            kwargs.update({"keys": keys})
        if isinstance(did, (list, Tuple)):
            kwargs.update({
                "did": ",".join(did),
                'parent_did': parent_did,
                'model': model,
            })
            return self.api_call('/plugin/earth/get_iot_prop/batch', http_verb="GET", params=kwargs)
        kwargs.update({"did": did})
        return self.api_call('/plugin/earth/get_iot_prop', http_verb="GET", params=kwargs)

    def get_sub_device(self, *, did: str, **kwargs) -> WyzeResponse:
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/earth/get_sub_device', http_verb="GET", params=kwargs)

    def set_iot_prop(self, *, did: str, model: str, key: str, value: str, is_sub_device: bool = False, **kwargs) -> WyzeResponse:
        # This method is only used for updating the schedule and the resetting the filter(s) - basically
        # anything that doesn't need to talk to the physical unit
        kwargs.update({
            'did': did,
            'model': model,
            'props': {key: value},
            'is_sub_device': 1 if is_sub_device else 0,
        })
        return self.api_call('/plugin/earth/set_iot_prop', http_verb="POST", json=kwargs)

    def set_iot_prop_by_topic(self, *, did: str, model: str, props: dict[str, str], is_sub_device: bool = False, **kwargs) -> WyzeResponse:
        kwargs.update({
            'did': did,
            'model': model,
            'props': props,
            'is_sub_device': 1 if is_sub_device else 0,
        })
        return self.api_call('/plugin/earth/set_iot_prop_by_topic', http_verb="POST", json=kwargs)
