from datetime import datetime
from typing import Optional, Sequence, Union

from wyze_sdk.models.devices import DeviceModels, Vacuum, VacuumSuctionLevel
from wyze_sdk.models.devices.vacuums import VacuumSweepRecord
from wyze_sdk.service import VenusServiceClient, WyzeResponse
from wyze_sdk.api.base import BaseClient


class VacuumsClient(BaseClient):
    """A Client that services Wyze vacuums.

    Methods:
        list: Lists all vacuums available to a Wyze account
        info: Retrieves details of a vacuum
        clean: Starts cleaning
        pause: Pauses cleaning
        dock: Docks the vacuum
        get_sweep_records: Retrieves event history records for a vacuum
        set_suction_level: Sets the suction level of a vacuum
        sweep_rooms: Starts cleaning specific map rooms
    """

    def list(self, **kwargs) -> Sequence[Vacuum]:
        """Lists all vacuums available to a Wyze account.

        Returns:
            (Sequence[Vacuum])
        """
        return [Vacuum(**device) for device in self._list_vacuums()]

    def _list_vacuums(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.VACUUM]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Vacuum]:
        """Retrieves details of a vacuum.

        Args:
            device_mac (str): The device mac. e.g. 'JA_RO2_ABCDEF1234567890'

        Returns:
            (Optional[Vacuum])
        """
        vacuums = [_vacuum for _vacuum in self._list_vacuums()
                   if _vacuum['mac'] == device_mac]
        if len(vacuums) == 0:
            return None

        vacuum = vacuums[0]

        iot_prop = super()._venus_client().get_iot_prop(did=device_mac, keys=[prop_def.pid for prop_def in Vacuum.props().values()])
        if "data" in iot_prop.data and "props" in iot_prop.data["data"]:
            vacuum.update(iot_prop.data["data"]["props"])

        device_info = super()._venus_client().get_device_info(did=device_mac, keys=[prop_def.pid for prop_def in Vacuum.device_info_props().values()])
        if "data" in device_info.data and "settings" in device_info.data["data"]:
            vacuum.update(device_info.data["data"]["settings"])

        current_position = super()._venus_client().get_current_position(did=device_mac)
        if ("data" in current_position.data and current_position.data['data'] is not None):
            vacuum.update({"current_position": current_position.data["data"]})

        current_map = super()._venus_client().get_current_map(did=device_mac)
        if "data" in current_map.data and current_map.data['data'] is not None:
            vacuum.update({"current_map": current_map.data["data"]})

        return Vacuum(**vacuum)

    def clean(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Starts cleaning.

        Args:
            device_mac (str): The device mac. e.g. 'JA_RO2_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'JA_RO2'
        """
        response = self._set_vacuum_mode(device_mac, device_model, 0, 1)
        self._create_user_vacuum_event(event_id='WRV_CLEAN', event_type=1)
        return response

    def pause(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Pauses cleaning.

        Args:
            device_mac (str): The device mac. e.g. 'JA_RO2_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'JA_RO2'
        """
        response = self._set_vacuum_mode(device_mac, device_model, 0, 2)
        self._create_user_vacuum_event(event_id='WRV_PAUSE', event_type=1)
        return response

    def dock(self, *, device_mac: str, device_model: str, **kwargs) -> WyzeResponse:
        """Docks the vacuum.

        Args:
            device_mac (str): The device mac. e.g. 'JA_RO2_ABCDEF1234567890'
            device_model (str): The device model. e.g. 'JA_RO2'
        """
        response = self._set_vacuum_mode(device_mac, device_model, 3, 1)
        # yes, when canceling cleaning, the event is still WRV_CLEAN
        self._create_user_vacuum_event(event_id='WRV_CLEAN', event_type=1)
        return response

    def get_sweep_records(self, *, device_mac: str, limit: int = 20, since: datetime, **kwargs) -> Sequence[VacuumSweepRecord]:
        """Retrieves event history records for a vacuum.

        The results are queried and returned in reverse-chronological order.

        Args:
            device_mac (str): The device mac. e.g. 'JA_RO2_ABCDEF1234567890'
            since (datetime): The starting datetime of the query i.e., the most recent datetime for returned records
                This parameter is optional and defaults to None
            limit (int): The maximum number of records to return.
                Defaults to 20

        Returns:
            (Sequence[VacuumSweepRecord])
        """
        return [VacuumSweepRecord(**record) for record in super()._venus_client().get_sweep_records(did=device_mac, keys=[], limit=limit, since=since)["data"]["data"]]

    def set_suction_level(self, *, device_mac: str, device_model: str, suction_level: VacuumSuctionLevel, **kwargs) -> WyzeResponse:
        """Sets the suction level of a vacuum.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            device_model (str): The device model. e.g. 'WLPA19'
            suction_level (VacuumSuctionLevel): The new suction level. e.g. VacuumSuctionLevel.QUIET
        """
        response = self._set_vacuum_preference(device_mac, device_model, 1, suction_level.code)
        self._create_user_vacuum_event(event_id='WRV_SETTINGS_SUCTION', event_type=1)
        return response

    def _set_vacuum_mode(self, device_mac: str, device_model: str, type: int, value: int) -> WyzeResponse:
        return super()._venus_client().set_iot_action(
            did=device_mac, model=device_model, cmd='set_mode', params={
                'type': type, 'value': value})

    def sweep_rooms(self, *, device_mac: str, room_ids: Union[int, Sequence[int]]) -> WyzeResponse:
        """Starts cleaning specific map rooms.

        Args:
            device_mac (str): The device mac. e.g. 'JA_RO2_ABCDEF1234567890'
            room_ids (Union[int, Sequence[int]]): The room ids to clean. e.g. [11, 14]
        """
        return super()._venus_client().sweep_rooms(did=device_mac, rooms=room_ids)

    def _set_vacuum_preference(
            self,
            device_mac: str, device_model: str,
            control_type: int,
            value: int) -> WyzeResponse:
        return super()._venus_client().set_iot_action(
            did=device_mac,
            model=device_model,
            cmd='set_preference',
            params={
                'ctrltype': control_type, 'value': value
            }
        )

    def _create_user_vacuum_event(self, event_id: str, event_type: int) -> WyzeResponse:
        return super()._create_user_event(VenusServiceClient.WYZE_APP_ID, event_id, event_type)
