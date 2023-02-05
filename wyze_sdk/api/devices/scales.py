from datetime import datetime, timedelta
from typing import Optional, Sequence, Union

from wyze_sdk.api.base import BaseClient
from wyze_sdk.errors import WyzeFeatureNotSupportedError, WyzeRequestError
from wyze_sdk.models.devices import DeviceModels, Scale, ScaleRecord, UserGoalWeight
from wyze_sdk.service import WyzeResponse


class ScalesClient(BaseClient):
    """A Client that services Wyze scales.
    """

    def _list_scales(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.SCALE]

    def list(self, **kwargs) -> Sequence[Scale]:
        """Lists all scales available to a Wyze account.

        :rtype: Sequence[Scale]
        """
        return [Scale(**device) for device in self._list_scales()]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Scale]:
        """Retrieves details of a scale.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Optional[Scale]

        :raises WyzeFeatureNotSupportedError: If the scale model isn't supported
        """
        scales = [_scale for _scale in self._list_scales() if _scale['mac'] == device_mac]
        if len(scales) == 0:
            return None

        scale = scales[0]

        device_setting = super()._scale_client(scale['product_model']).get_device_setting(did=device_mac)
        if "data" in device_setting.data:
            scale.update(device_setting.data["data"])

        device_member = super()._scale_client(scale['product_model']).get_device_member(did=device_mac)
        if "data" in device_member.data and device_member.data['data'] is not None:
            scale.update({"device_members": device_member.data["data"]})

        family_member = super()._scale_client(scale['product_model']).get_family_member(did=device_mac)
        if "data" in family_member.data and family_member.data['data'] is not None:
            scale.update({"family_members": family_member.data["data"]})

        user_preference = super()._scale_client(scale['product_model']).get_user_preference(did=device_mac)
        if "data" in user_preference.data and user_preference.data['data'] is not None:
            scale.update({"user_preferences": user_preference.data["data"]})

        if self._user_id is not None:
            user_device_relation = super()._scale_client(scale['product_model']).get_user_device_relation(did=device_mac, user_id=self._user_id)
            if "data" in user_device_relation.data and user_device_relation.data['data'] is not None:
                scale.update({"device_relation": user_device_relation.data["data"]})

            user_goal_weight = super()._scale_client().get_goal_weight(user_id=self._user_id)
            if "data" in user_goal_weight.data and user_goal_weight.data['data'] is not None:
                scale.update({"goal_weight": user_goal_weight.data["data"]})

        if scale['product_model'] in DeviceModels.SCALE_S:

            # // this returns the same data as above
            # device_info = super()._scale_client(scale['product_model']).get_device_info(did=device_mac)
            # if "data" in device_info.data:
            #     scale.update(device_info.data["data"])

            now = datetime.now()
            latest_records = super()._scale_client(scale['product_model']).get_records(user_id=self._user_id, start_time=now-timedelta(days=5), end_time=now)
            if "data" in latest_records.data and latest_records.data['data'] is not None:
                scale.update({"latest_records": latest_records.data["data"]})
        elif scale['product_model'] in DeviceModels.SCALE_X:
            raise WyzeFeatureNotSupportedError('Scale Series X')
        else:
            token = super()._scale_client().get_token(did=device_mac)
            if "data" in token.data and token.data['data'] is not None:
                scale.update(token.data["data"])

            # com.wyze.ihealth.d.e
            user_profile = super()._platform_client().get_user_profile(appid='nHtOAABMsnTbOmg74g3zBsFuHx4iVi5G')
            if "data" in user_profile.data and user_profile.data['data'] is not None:
                scale.update({"user_profile": user_profile.data["data"]})

            latest_records = super()._scale_client().get_latest_records()
            if "data" in latest_records.data and latest_records.data['data'] is not None:
                scale.update({"latest_records": latest_records.data["data"]})

        return Scale(**scale)

    def get_records(self, *, device_model: Optional[str] = DeviceModels.SCALE_[0], user_id: Optional[str] = None, start_time: datetime, end_time: Optional[datetime] = datetime.now(), **kwargs) -> Sequence[ScaleRecord]:
        """Retrieves a user's scale event history records.

        .. note:: The results are queried and returned in reverse-chronological order

        :param str user_id: The user id. e.g. ``abcdef1234567890abcdef1234567890``. Defaults to ``None``, which assumes the current user.
        :param datetime start_time: The ending datetime of the query i.e., the oldest allowed datetime for returned records
        :param datetime end_time: The starting datetime of the query i.e., the most recent datetime for returned records. This parameter is optional and defaults to ``None``

        :rtype: Sequence[ScaleRecord]
        """
        return [ScaleRecord(**record) for record in super()._scale_client(device_model=device_model).get_records(user_id=user_id if user_id is not None else self._user_id, start_time=start_time, end_time=end_time)["data"]]

    def get_goal_weight(self, *, device_model: Optional[str] = DeviceModels.SCALE_[0], user_id: Optional[str] = None, **kwargs) -> UserGoalWeight:
        """Retrieves a user's goal weight.

        :param str user_id: The user id. e.g. ``abcdef1234567890abcdef1234567890``

        :rtype: WyzeResponse
        """
        response = super()._scale_client(device_model=device_model).get_goal_weight(user_id=user_id if user_id is not None else self._user_id)
        return None if response["data"] is None else UserGoalWeight(**response["data"])

    def delete_goal_weight(self, *, user_id: Optional[str] = None, **kwargs) -> WyzeResponse:
        """Deletes a user's goal weight, if one exists.

        :param str user_id: The user id. e.g. ``abcdef1234567890abcdef1234567890``. Defaults to ``None``, which assumes the current user.

        :rtype: WyzeResponse
        """
        response = super()._scale_client().delete_goal_weight(user_id=user_id)
        return response

    def delete_record(self, *, data_id=Union[int, Sequence[int]], **kwargs) -> WyzeResponse:
        """Deletes a scale event history record.

        :param data_id: The data ids. e.g. ``1234567890``
        :type data_id: Union[int, Sequence[int]]

        :rtype: WyzeResponse
        """
        response = super()._scale_client().delete_record(data_id=data_id)
        return response

    def add_weight_record(self, *, device_mac: str, mac: str, user_id: str, measure_ts: datetime, measure_type: int = 1, weight: float, **kwargs) -> WyzeResponse:
        """Creates a standard weight event history record for a user.

        :param str device_mac: The device mac. e.g. ``JA.SC2.ABCDEF1234567890``
        :param str mac: The device mac, without the leading product model identifier. e.g. ``ABCDEF1234567890``
        :param str user_id: The user id. e.g. ``abcdef1234567890abcdef1234567890``
        :param datetime measure_ts: The timestamp of the record.
        :param int measure_type: The measurement type. e.g. ``1``
        :param float weight: The new weight in kg. e.g. ``117.3``

        :rtype: WyzeResponse
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
        :param str device_mac: The device mac. e.g. ``JA.SC2.ABCDEF1234567890``
        :param str mac: The device mac, without the leading product model identifier. e.g. ``ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``JA.SC2``
        :param str firmware_ver: The firmware version. e.g. ''
        :param str unit: The new unit. e.g. ``kg``
        :param int broadcast: The broadcast. e.g. ``1``

        :raises WyzeRequestError: if the new unit is not ``kg`` or ``lb``

        :rtype: WyzeResponse
        """

        if unit not in ['kg', 'lb']:
            raise WyzeRequestError(f"{unit} must be one of {['kg', 'lb']}")

        response = self._set_scale_setting(device_mac, device_model, unit, firmware_ver, mac, broadcast)
        return response

    def _set_scale_setting(
        self,
        device_mac: str,
        device_model: str,
        unit: str,
        firmware_ver: str,
        mac: str,
        broadcast: int
    ) -> WyzeResponse:
        return super()._scale_client().update_device_setting(did=device_mac, model=device_model, firmware_ver=firmware_ver, mac=mac, unit=unit, broadcast=broadcast)
