from datetime import datetime
from typing import Optional, Sequence, Tuple, Union

from wyze_sdk.models import datetime_to_epoch

from .base import ExServiceClient, WyzeResponse


class ScaleServiceClient(ExServiceClient):
    """
    Scale service client is the wrapper on the requests to https://wyze-scale-service.wyzecam.com
    """

    WYZE_API_URL = "https://wyze-scale-service.wyzecam.com"
    WYZE_APP_ID = "scap_41183d5d0bac498d"

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
        # create the time-based nonce
        nonce = self.request_verifier.clock.nonce()

        return super().api_call(
            api_method,
            http_verb=http_verb,
            params=params,
            json=json,
            headers=self._get_headers(request_specific_headers=request_specific_headers, nonce=nonce),
            nonce=nonce,
        )

    def get_device_setting(self, *, did: str, **kwargs) -> WyzeResponse:
        """
        Get the settings for the scale.

        See: com.wyze.ihealth.d.a.m
        """
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/scale/get_device_setting', http_verb="GET", params=kwargs)

    def get_device_member(self, *, did: str, **kwargs) -> WyzeResponse:
        """
        Get the users associated with the scale.

        See: com.wyze.ihealth.d.a.j
        """
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/scale/get_device_member', http_verb="GET", params=kwargs)

    def get_family_member(self, *, did: str, **kwargs) -> WyzeResponse:
        """
        Get the users associated with the scale.

        See: com.wyze.ihealth.d.a.o
        """
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/scale/get_family_member', http_verb="GET", params=kwargs)

    def get_user_preference(self, *, did: str, **kwargs) -> WyzeResponse:
        """
        Get the scale-related preferences for the current user.

        See: com.wyze.ihealth.d.a.p
        """
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/scale/get_user_preference', http_verb="GET", params=kwargs)

    def get_token(self, *, did: str, **kwargs) -> WyzeResponse:
        """
        Get binding token for the scale.

        See: com.wyze.ihealth.d.a.c
        """
        kwargs.update({'device_id': did})
        return self.api_call('/plugin/scale/get_token', http_verb="GET", params=kwargs)

    def get_user_device_relation(self, *, did: str, user_id: str, **kwargs) -> WyzeResponse:
        """
        Get the relationship of the users associated with the scale.

        See: com.wyze.ihealth.d.a.d
        """
        kwargs.update({'device_id': did, 'user_id': user_id})
        return self.api_call('/plugin/scale/get_user_device_relation', http_verb="GET", params=kwargs)

    def update_device_setting(self, *, did: str, model: str, firmware_ver: str, mac: str, unit: str, broadcast: int, **kwargs) -> WyzeResponse:
        """
        Update the settings of scale.

        See: com.wyze.ihealth.d.a.f
        """
        kwargs.update({'device_id': did, 'device_model': model, 'firmware_ver': firmware_ver, 'mac': mac, 'unit': unit, 'broadcast': broadcast})
        return self.api_call('/plugin/scale/update_device_setting', json=kwargs)

    def get_user_profile(self):
        """
        Get the scale-related data from the user's profile.

        See: com.wyze.ihealth.d.a.a and com.samsung.android.sdk.healthdata.HealthUserProfile
        """
        return self.api_call('/app/v2/platform/get_user_profile', http_verb="GET")

    def update_user_profile(self, *, logo_url: str, nickname: str, gender: str, birth_date: str, height: str, height_unit: str, body_type: str, occupation: str, **kwargs) -> WyzeResponse:
        """
        Set scale-related data to the user's profile.

        See: com.wyze.ihealth.d.a.l and com.samsung.android.sdk.healthdata.HealthUserProfile
        """
        kwargs.update({'logo_url': logo_url, 'nickname': nickname, 'gender': gender, 'birthDate': birth_date, 'height': height, 'height_unit': height_unit, 'body_type': body_type, 'occupation': occupation})
        return self.api_call('/app/v2/platform/update_user_profile', json=kwargs)

    def get_goal_weight(self, *, user_id: str, **kwargs) -> WyzeResponse:
        """
        Get the goal weight from the user's profile.

        See: com.wyze.ihealth.d.b.v
        """
        kwargs.update({'family_member_id': user_id})
        return self.api_call('/plugin/scale/get_goal_weight', http_verb="GET", params=kwargs)

    def get_heart_rate_record_list(self, *, user_id: Optional[str] = None, record_number: Optional[int] = 1, measure_ts: Optional[int] = None, **kwargs) -> WyzeResponse:
        """
        Get the heart rate records from the user's profile.

        See: com.wyze.ihealth.d.b.b
        """
        if user_id:
            kwargs.update({'family_member_id': user_id})
        kwargs.update({'record_number': str(record_number)})
        if measure_ts:
            kwargs.update({'measure_ts': str(measure_ts)})
        return self.api_call('/plugin/scale/get_heart_rate_record_list', http_verb="GET", params=kwargs)

    def get_latest_records(self, *, user_id: Optional[str] = None, **kwargs) -> WyzeResponse:
        """
        Get the latest records from the user's profile.

        See: com.wyze.ihealth.d.b.t
        """
        if user_id:
            kwargs.update({'family_member_id': user_id})
        return self.api_call('/plugin/scale/get_latest_record', http_verb="GET", params=kwargs)

    def get_records(self, *, user_id: Optional[str] = None, start_time: datetime, end_time: datetime, **kwargs) -> WyzeResponse:
        """
        Get a range of records from the user's profile.

        See: com.wyze.ihealth.d.b.i and com.samsung.android.sdk.healthdata.HealthConstants.SessionMeasurement
        """
        if user_id:
            kwargs.update({'family_member_id': user_id})
        kwargs.update({'start_time': str(0), 'end_time': str(datetime_to_epoch(end_time))})
        return self.api_call('/plugin/scale/get_record_range', http_verb="GET", params=kwargs)

    def delete_goal_weight(self, *, user_id: Optional[str] = None, **kwargs) -> WyzeResponse:
        """
        Removes the goal weight from the user's profile.

        See: com.wyze.ihealth.d.b.j
        """
        if user_id:
            kwargs.update({'family_member_id': user_id})
        return self.api_call('/plugin/scale/delete_goal_weight', http_verb="GET", params=kwargs)

    def add_heart_rate_record(self, *, did: str, user_id: str, measure_ts: int, heart_rate: int, **kwargs) -> WyzeResponse:
        """
        Add a heart rate record to the user's profile.

        See: com.wyze.ihealth.d.b.p
        """
        kwargs.update({'device_id': did, 'family_member_id': user_id, 'measure_ts': measure_ts, 'heart_rate': str(heart_rate)})
        return self.api_call('/plugin/scale/get_latest_record', json=kwargs)

    def add_weight_record(self, *, did: str, mac: str, user_id: str, measure_ts: int, measure_type: int = 1, weight: float, **kwargs) -> WyzeResponse:
        """
        Add a weight-only record to the user's profile.

        See: com.wyze.ihealth.d.b.k
        """
        kwargs.update({'device_id': did, 'mac': mac, 'family_member_id': user_id, 'measure_ts': measure_ts, 'measure_type': measure_type, 'weight': weight})
        return self.api_call('/plugin/scale/get_latest_record', json=kwargs)

    def delete_record(self, *, data_id=Union[int, Sequence[int]], **kwargs) -> WyzeResponse:
        """
        Delete health records from the user's profile.

        See: com.wyze.ihealth.d.b.u
        """
        if isinstance(data_id, (list, Tuple)):
            kwargs.update({"data_id_list": ",".join(data_id)})
        else:
            kwargs.update({"data_id_list": [data_id]})
        return self.api_call('/plugin/scale/delete_record', json=kwargs)
