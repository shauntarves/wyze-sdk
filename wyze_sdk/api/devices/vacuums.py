from datetime import datetime
from typing import Optional, Sequence, Union

from wyze_sdk.api.base import BaseClient
from wyze_sdk.errors import WyzeRequestError
from wyze_sdk.models.devices import DeviceModels, Vacuum, VacuumSuctionLevel
from wyze_sdk.models.devices.vacuums import VacuumDeviceControlRequestType, VacuumDeviceControlRequestValue, VacuumMapSummary, VacuumMode, VacuumStatus, VacuumSweepRecord, VenusDotArg1Message, VenusDotArg2Message, VenusDotArg3Message
from wyze_sdk.service import VenusServiceClient, WyzeResponse


class VacuumsClient(BaseClient):
    """A Client that services Wyze Robot Vacuums.
    """

    def list(self, **kwargs) -> Sequence[Vacuum]:
        """Lists all vacuums available to a Wyze account.

        :rtype: Sequence[Vacuum]
        """
        return [Vacuum(**device) for device in self._list_vacuums()]

    def _list_vacuums(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.VACUUM]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Vacuum]:
        """Retrieves details of a vacuum.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``

        :rtype: Optional[Vacuum]
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

        status = super()._venus_client().get_status(did=device_mac)
        if "data" in status.data:
            if "eventFlag" in status.data["data"]:
                vacuum.update(**status.data["data"]["eventFlag"])
            if "heartBeat" in status.data["data"]:
                vacuum.update(**status.data["data"]["heartBeat"])

        current_position = super()._venus_client().get_current_position(did=device_mac)
        if ("data" in current_position.data and current_position.data['data'] is not None):
            vacuum.update({"current_position": current_position.data["data"]})

        current_map = super()._venus_client().get_current_map(did=device_mac)
        if "data" in current_map.data and current_map.data['data'] is not None:
            vacuum.update({"current_map": current_map.data["data"]})

        return Vacuum(**vacuum)

    def clean(self, *, device_mac: str, **kwargs) -> WyzeResponse:
        """Starts a new cleaning action or resumes a paused cleaning.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``JA_RO2`` DEPRECATED

        :rtype: WyzeResponse
        """
        device = self.info(device_mac=device_mac)

        event_args = [VenusDotArg1Message.Vacuum, VenusDotArg2Message.Whole]

        if device.status == VacuumStatus.PAUSED or device.mode == VacuumMode.PAUSED:
            event_args.append(VenusDotArg3Message.Resume)
        else:
            event_args.append(VenusDotArg3Message.Start)

        response = super()._venus_client().control(
            did=device_mac,
            type=VacuumDeviceControlRequestType.GLOBAL_SWEEPING,
            value=VacuumDeviceControlRequestValue.START,
        )
        super()._venus_client()._create_event(
            did=device_mac,
            type=VacuumDeviceControlRequestType.GLOBAL_SWEEPING,
            value=VacuumDeviceControlRequestValue.START,
            args=event_args
        )
        return response

    def pause(self, *, device_mac: str, **kwargs) -> WyzeResponse:
        """Pauses the vacuum's current cleaning action.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``JA_RO2`` DEPRECATED

        :rtype: WyzeResponse

        :raises WyzeRequestError: If the device is already idle.
        """
        device = self.info(device_mac=device_mac)

        if device.status == VacuumStatus.DOCKED or device.status == VacuumStatus.PAUSED or device.status == VacuumStatus.STANDBY:
            raise WyzeRequestError("Device is already idle.")

        response = super()._venus_client().control(
            did=device_mac,
            type=VacuumDeviceControlRequestType.GLOBAL_SWEEPING,
            value=VacuumDeviceControlRequestValue.PAUSE,
        )
        super()._venus_client()._create_event(
            did=device_mac,
            type=VacuumDeviceControlRequestType.GLOBAL_SWEEPING,
            value=VacuumDeviceControlRequestValue.PAUSE,
            args=[VenusDotArg1Message.Vacuum, VenusDotArg2Message.Whole, VenusDotArg3Message.Pause]
        )
        return response

    def dock(self, *, device_mac: str, **kwargs) -> WyzeResponse:
        """Docks the vacuum.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``JA_RO2`` DEPRECATED

        :rtype: WyzeResponse

        :raises WyzeRequestError: If the device is already docked
        """
        device = self.info(device_mac=device_mac)

        if device.status == VacuumStatus.DOCKED:
            raise WyzeRequestError("Device is already docked.")

        response = super()._venus_client().control(
            did=device_mac,
            type=VacuumDeviceControlRequestType.RETURN_TO_CHARGING,
            value=VacuumDeviceControlRequestValue.START,
        )
        super()._venus_client()._create_event(
            did=device_mac,
            type=VacuumDeviceControlRequestType.RETURN_TO_CHARGING,
            value=VacuumDeviceControlRequestValue.START,
            args=[VenusDotArg3Message.Start, VenusDotArg2Message.ManualRecharge]
        )
        return response

    def stop(self, *, device_mac: str, **kwargs) -> WyzeResponse:
        """Stops the vacuum on its way to the charging dock.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``

        :rtype: WyzeResponse

        :raises WyzeRequestError: If the device is not in a stoppable state
        """
        device = self.info(device_mac=device_mac)

        event_type = VacuumDeviceControlRequestType.RETURN_TO_CHARGING
        event_value = VacuumDeviceControlRequestValue.STOP
        event_args = None

        if device.mode == VacuumMode.RETURNING_TO_CHARGE:
            event_args = [event_value.description, VenusDotArg2Message.ManualRecharge]
        elif device.mode == VacuumMode.FINISHED_RETURNING_TO_CHARGE:
            event_args = [event_value.description, VenusDotArg2Message.FinishRecharge]
        else:
            raise WyzeRequestError(f"Device cannot be stopped when in {device.mode}. Docking or canceling may be possible.")

        response = super()._venus_client().control(
            did=device_mac,
            type=event_type,
            value=event_value,
        )
        super()._venus_client()._create_event(
            did=device_mac,
            type=event_type,
            value=event_value,
            args=event_args
        )
        return response

    def cancel(self, *, device_mac: str, **kwargs) -> WyzeResponse:
        """Prevents the vacuum from resuming an unfinished cleaning action after charging.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``

        :rtype: WyzeResponse

        :raises WyzeRequestError: If the device is not in a cancelable state
        """
        device = self.info(device_mac=device_mac)

        if device.mode != VacuumMode.DOCKED_NOT_COMPLETE:
            message = f"Device cleaning cannot be canceled when in {device.mode}."
            if device.mode == VacuumMode.IDLE:
                message = "Device does not have an in-progress cleaning action that can be canceled."
            if device.status != VacuumStatus.DOCKED:
                message = message + " Docking may be possible."
            raise WyzeRequestError(message)

        response = super()._venus_client().control(
            did=device_mac,
            type=VacuumDeviceControlRequestType.RETURN_TO_CHARGING,
            value=VacuumDeviceControlRequestValue.STOP,
        )
        super()._venus_client()._create_event(
            did=device_mac,
            type=VacuumDeviceControlRequestType.RETURN_TO_CHARGING,
            value=VacuumDeviceControlRequestValue.STOP,
            args=[VacuumDeviceControlRequestValue.STOP.description, VenusDotArg2Message.BreakCharging if device.is_charging else VenusDotArg2Message.BreakRecharge]
        )
        return response

    def get_sweep_records(self, *, device_mac: str, limit: int = 20, since: datetime, **kwargs) -> Sequence[VacuumSweepRecord]:
        """Retrieves event history records for a vacuum.

        The results are queried and returned in reverse-chronological order.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
        :param int limit: The maximum number of records to return. Defaults to ``20``
        :param datetime since: The starting datetime of the query i.e., the most recent datetime for returned records. This parameter is optional and defaults to ``None``

        :rtype: Sequence[VacuumSweepRecord]
        """
        return [VacuumSweepRecord(**record) for record in super()._venus_client().get_sweep_records(did=device_mac, keys=[], limit=limit, since=since)["data"]["data"]]

    def get_maps(self, *, device_mac: str, **kwargs) -> Sequence[VacuumMapSummary]:
        """Retrieves defined maps for a vacuum.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``

        :rtype: Sequence[VacuumMapSummary]
        """
        return [VacuumMapSummary(**map) for map in super()._venus_client().get_maps(did=device_mac)["data"]]

    def set_current_map(self, *, device_mac: str, map_id: int, **kwargs) -> WyzeResponse:
        """Sets the current map of a vacuum.

        Args:
            :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
            :param int map_id: The new current map id. e.g. ``12345678``

        :rtype: WyzeResponse
        """

        return super()._venus_client().set_current_map(
            did=device_mac, map_id=map_id)

    def set_suction_level(self, *, device_mac: str, device_model: str, suction_level: VacuumSuctionLevel, **kwargs) -> WyzeResponse:
        """Sets the suction level of a vacuum.

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
        :param str device_model: The device model. e.g. ``JA_RO2``
        :param VacuumSuctionLevel suction_level: The new suction level. e.g. ``VacuumSuctionLevel.QUIET``

        :rtype: WyzeResponse
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

        :param str device_mac: The device mac. e.g. ``JA_RO2_ABCDEF1234567890``
        :param room_ids: The room ids to clean. e.g. ``[11, 14]``
        :type room_ids: Union[int, Sequence[int]]

        :rtype: WyzeResponse
        """
        return super()._venus_client().control(
            did=device_mac,
            type=VacuumDeviceControlRequestType.GLOBAL_SWEEPING,
            value=VacuumDeviceControlRequestValue.START,
            rooms=room_ids
        )

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
