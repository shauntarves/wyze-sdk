from datetime import datetime
from typing import Optional, Sequence, Union

from wyze_sdk.models.devices import DeviceModels, Scale, ScaleRecord
from wyze_sdk.service import WyzeResponse
from wyze_sdk.api.base import BaseClient


class ScalesClient(BaseClient):
    """A Client that services Wyze scales.

    Methods:
        list: Lists all scales available to a Wyze account
        info: Retrieves details of a scale
        get_records: Retrieves a user's scale event history record
        get_goal_weight: Retrieves a user's goal weight
        delete_goal_weight: Deletes a user's goal weight
        delete_record: Deletes a scale event history record
        add_weight_record: Creates a standard weight event history record for a user
        set_unit: Sets the weight/mass unit for the scale
    """

    def _list_scales(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.SCALE]

    def list(self, **kwargs) -> Sequence[Scale]:
        """Lists all scales available to a Wyze account.

        Returns:
            (Sequence[Scale])
        """
        return [Scale(**device) for device in self._list_scales()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Scale]:
        """Retrieves details of a scale.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'

        Returns:
            (Optional[Scale])
        """
        scales = [_scale for _scale in self._list_scales() if _scale['mac'] == device_mac]
        if len(scales) == 0:
            return None

        scale = scales[0]

        device_setting = super()._scale_client().get_device_setting(did=device_mac)
        if "data" in device_setting.data:
            scale.update(device_setting.data["data"])

        device_member = super()._scale_client().get_device_member(did=device_mac)
        if "data" in device_member.data and device_member.data['data'] is not None:
            scale.update({"device_members": device_member.data["data"]})

        family_member = super()._scale_client().get_family_member(did=device_mac)
        if "data" in family_member.data and family_member.data['data'] is not None:
            scale.update({"family_members": family_member.data["data"]})

        user_preference = super()._scale_client().get_user_preference(did=device_mac)
        if "data" in user_preference.data and user_preference.data['data'] is not None:
            scale.update({"user_preferences": user_preference.data["data"]})

        token = super()._scale_client().get_token(did=device_mac)
        if "data" in token.data and token.data['data'] is not None:
            scale.update(token.data["data"])

        # user_device_relation = super()._scale_client().get_user_device_relation(did=device_mac, user_id='d4e502568f8d453b0ffd014527706f40')
        # print(user_device_relation)
        # if "data" in user_preference.data and user_preference.data['data'] is not None:
        #     scale.update({"user_preferences": user_preference.data["data"]})

        # com.wyze.ihealth.d.e
        user_profile = super()._platform_client().get_user_profile(appid='nHtOAABMsnTbOmg74g3zBsFuHx4iVi5G')
        if "data" in user_profile.data and user_profile.data['data'] is not None:
            scale.update({"user_profile": user_profile.data["data"]})

        latest_records = super()._scale_client().get_latest_records()
        if "data" in latest_records.data and latest_records.data['data'] is not None:
            scale.update({"latest_records": latest_records.data["data"]})

        return Scale(**scale)

    def get_records(self, *, user_id: Optional[str] = None, start_time: datetime, end_time: Optional[datetime] = datetime.now(), **kwargs) -> Sequence[ScaleRecord]:
        """Retrieves a user's scale event history records.

        The results are queried and returned in reverse-chronological order

        Args:
            user_id (str): The user id. e.g. 'abcdef1234567890abcdef1234567890'
                Defaults to None, which assumes the current user.
            start_time (datetime): The ending datetime of the query i.e., the oldest allowed datetime for returned records
            end_time (datetime): The starting datetime of the query i.e., the most recent datetime for returned records
                This parameter is optional and defaults to None

        Returns:
            (Sequence[ScaleRecord])
        """
        return [ScaleRecord(**record) for record in super()._scale_client().get_records(user_id=user_id, start_time=start_time, end_time=end_time)["data"]]

    def get_goal_weight(self, *, user_id: str, **kwargs) -> WyzeResponse:
        """Retrieves a user's goal weight.

        Args:
            user_id (str): The user id. e.g. 'abcdef1234567890abcdef1234567890'
        """
        response = super()._scale_client().get_goal_weight(user_id=user_id)
        return response

    def delete_goal_weight(self, *, user_id: Optional[str] = None, **kwargs) -> WyzeResponse:
        """Deletes a user's goal weight, if one exists.

        Args:
            user_id (str): The user id. e.g. 'abcdef1234567890abcdef1234567890'
                Defaults to None, which assumes the current user.
        """
        response = super()._scale_client().delete_goal_weight(user_id=user_id)
        return response

    def delete_record(self, *, data_id=Union[int, Sequence[int]], **kwargs) -> WyzeResponse:
        """Deletes a scale event history record.

        Args:
            data_id (Union[int, Sequence[int]]): The data ids. e.g. '1234567890'
        """
        response = super()._scale_client().delete_record(data_id=data_id)
        return response

    def add_weight_record(self, *, device_mac: str, mac: str, user_id: str, measure_ts: datetime, measure_type: int = 1, weight: float, **kwargs) -> WyzeResponse:
        """Creates a standard weight event history record for a user.

        Args:
            device_mac (str): The device mac. e.g. 'JA.SC2.ABCDEF1234567890'
            mac (str): The device mac, without the leading product model identifier. e.g. 'ABCDEF1234567890'
            user_id (str): The user id. e.g. 'abcdef1234567890abcdef1234567890'
            measure_ts (datetime): The timestamp of the record.
            measure_type (int): The measurement type. e.g. 1
            weight (float): The new weight in kg. e.g. 117.3
        """
        response = super()._scale_client().add_weight_record(did=device_mac, mac=mac, user_id=user_id, measure_ts=measure_ts.timestamp(), measure_type=measure_type, weight=weight)
        return response

    def set_unit(
        self,
        *,
        device_mac: str,
        device_model: str,
        firmware_ver: str,
        mac: str,
        unit: str,
        broadcast: int,
        **kwargs,
    ) -> WyzeResponse:
        """Sets the weight/mass unit for the scale.

        Args:
            device_mac (str): The device mac. e.g. 'JA.SC2.ABCDEF1234567890'
            device_model (str): The device model. e.g. ''
            firmware_ver (str): The firmware version. e.g. ''
            mac (str): The device mac, without the leading product model identifier. e.g. 'ABCDEF1234567890'
            unit (str): The new unit. e.g. 'kg'
            broadcast (int): The broadcast. e.g. 1
        """
        response = self._set_scale_setting(device_mac, device_model, firmware_ver, mac, unit, broadcast)
        return response

    def _set_scale_setting(
        self,
        device_mac: str,
        device_model: str,
        firmware_ver: str,
        mac: str,
        unit: str,
        broadcast: int
    ) -> WyzeResponse:
        return super()._scale_client().update_device_setting(did=device_mac, model=device_model, firmware_ver=firmware_ver, mac=mac, unit=unit, broadcast=broadcast)
