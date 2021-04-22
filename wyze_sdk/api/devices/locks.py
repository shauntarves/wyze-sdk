from abc import ABCMeta
from datetime import datetime
from typing import Optional, Sequence

from wyze_sdk.models.devices import DeviceModels, Lock, LockGateway
from wyze_sdk.models.devices.locks import LockRecord
from wyze_sdk.service import FordServiceClient, WyzeResponse
from wyze_sdk.api.base import BaseClient


class BaseLockClient(BaseClient, metaclass=ABCMeta):

    def _ford_client(self) -> FordServiceClient:
        return BaseClient._service_client(FordServiceClient, token=self._token, base_url=self._base_url)

    def _get_lock_devices(self, **kwargs) -> WyzeResponse:
        return self._ford_client().get_user_device().data

    def _list_locks(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.LOCK]

    def _list_lock_gateways(self, **kwargs) -> Sequence[dict]:
        return [device for device in super()._list_devices(
        ) if device["product_model"] in DeviceModels.LOCK_GATEWAY]


class LockGatewaysClient(BaseLockClient):

    def list(self, **kwargs) -> Sequence[LockGateway]:
        gateways = [LockGateway(**device) for device in self._list_lock_gateways()]
        return gateways

    def info(self, device_mac: str, **kwargs) -> Optional[LockGateway]:
        gateways = [_gateway for _gateway in self._list_lock_gateways() if _gateway['mac'] == device_mac]
        if len(gateways) == 0:
            return None

        gateway = gateways[0]

        uuid = LockGateway.parse_uuid(gateway['mac'])

        device_info = self._ford_client().get_gateway_info(uuid=uuid)
        gateway.update({"device_params": {**gateway["device_params"], **device_info["device"]} if "device_params" in gateway else device_info["device"]})

        locks = gateway["locks"] if "locks" in gateway else []

        response = self._get_lock_devices()
        if response is not None and "devices" in response:
            for device in response["devices"]:
                if device["model"] == "XNLL901":
                    if "states" in response:
                        for state in response["states"]:
                            if state["uuid"] == device["uuid"]:
                                device.update(state)
                    locks.append(device)

        gateway.update({"locks": locks})

        return LockGateway(**gateway)


class LocksClient(BaseLockClient):
    """A Client that services Wyze locks.

    Methods:
        list: Lists all locks available to a Wyze account
        info: Retrieves details of a lock
        lock: Locks a lock
        unlock: Unlocks a lock
        get_records: Retrieves event history records for a lock
    """

    def list(self, **kwargs) -> Sequence[Lock]:
        """Lists all locks available to a Wyze account.

        Returns:
            (Sequence[Lock])
        """
        return [Lock(**device) for device in self._list_locks()]

    def _control_lock(self, device_mac: str, action: str, **kwargs) -> WyzeResponse:
        uuid = Lock.parse_uuid(mac=device_mac)
        return self._ford_client().remote_control_lock(uuid=uuid, action=action)

    def lock(self, device_mac: str, **kwargs) -> WyzeResponse:
        """Locks a lock.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
        """
        return self._control_lock(device_mac=device_mac, action="remoteLock")

    def unlock(self, device_mac: str, **kwargs) -> WyzeResponse:
        """Unlocks a lock.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
        """
        return self._control_lock(device_mac=device_mac, action="remoteUnlock")

    def get_records(self, *, device_mac: str, limit: int = 20, since: datetime, until: Optional[datetime] = None, offset: int = 0, **kwargs) -> Sequence[LockRecord]:
        """Retrieves event history records for a lock.

        The results are queried and returned in reverse-chronological order.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'
            since (datetime): The starting datetime of the query i.e., the most recent datetime for returned records
            until (datetime): The ending datetime of the query i.e., the oldest allowed datetime for returned records
                This parameter is optional and defaults to None
            limit (int): The maximum number of records to return.
                Defaults to 20
            offset (int): The number of records to skip when querying.
                Defaults to 0

        Returns:
            (Sequence[LockRecord])
        """
        return [LockRecord(**record) for record in super()._ford_client().get_family_record(uuid=Lock.parse_uuid(mac=device_mac), begin=since, end=until, limit=limit, offset=offset)["family_record"]]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Lock]:
        """Retrieves details of a lock.

        Args:
            device_mac (str): The device mac. e.g. 'ABCDEF1234567890'

        Returns:
            (Optional[Lock])
        """
        locks = [_lock for _lock in self._list_locks() if _lock['mac'] == device_mac]
        if len(locks) == 0:
            return None

        lock = locks[0]

        uuid = Lock.parse_uuid(lock['mac'])

        device_info = self._ford_client().get_lock_info(uuid=uuid)
        if "device" in device_info.data and device_info.data['device'] is not None:
            lock.update({"device_params": {**lock["device_params"], **device_info.data["device"]} if "device_params" in lock else device_info.data["device"]})
            if "parent" in device_info.data["device"]:
                response = self._get_lock_devices()
                if response is not None and "devices" in response:
                    for device in response["devices"]:
                        if device["model"] == "DC-CW01" and device_info.data["device"]["parent"] == device["uuid"]:
                            lock.update({"parent": device})

        lock.update({"secret": self._ford_client().get_crypt_secret()["secret"]})

        lock.update({"record_count": self._ford_client().get_family_record_count(uuid=uuid, begin=datetime(1970, 1, 1, 0, 0, 0))["cnt"]})

        return Lock(**lock)

    @property
    def gateways(self) -> LockGatewaysClient:
        return LockGatewaysClient(token=self._token, base_url=self._base_url, logger=self._logger)
