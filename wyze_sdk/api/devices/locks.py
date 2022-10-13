from abc import ABCMeta
from datetime import datetime, timedelta
import re
from typing import Optional, Sequence

from wyze_sdk.api.base import BaseClient
from wyze_sdk.errors import WyzeRequestError
from wyze_sdk.models.devices import DeviceModels, Lock, LockGateway
from wyze_sdk.models.devices.locks import LockKey, LockKeyPeriodicity, LockKeyPermission, LockKeyPermissionType, LockKeyType, LockRecord
from wyze_sdk.service import FordServiceClient, WyzeResponse
from wyze_sdk.signature import CBCEncryptor, MD5Hasher

# The relationship between locks and gateways is a bit complicated.
# Gateways can supposedly service multiple locks, with each lock
# being paired with exactly one gateway. The gateway is accessible
# from the Wyze app, but it really only exists there to modify WiFi
# network information in the event that it changes.
#
# Keypads are paired 1:1 with locks, with the lock entity storing
# the relationship key.


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
        """Lists all lock gateways available to a Wyze account.

        :rtype: Sequence[LockGateway]
        """
        gateways = [LockGateway(**device) for device in self._list_lock_gateways()]
        return gateways

    def info(self, device_mac: str, **kwargs) -> Optional[LockGateway]:
        """Retrieves details of a lock gateway.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Optional[LockGateway]
        """
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
    """

    def list(self, **kwargs) -> Sequence[Lock]:
        """Lists all locks available to a Wyze account.

        :rtype: Sequence[Lock]
        """
        return [Lock(**device) for device in self._list_locks()]

    def _control_lock(self, device_mac: str, action: str, **kwargs) -> WyzeResponse:
        uuid = Lock.parse_uuid(mac=device_mac)
        return self._ford_client().remote_control_lock(uuid=uuid, action=action)

    def lock(self, device_mac: str, **kwargs) -> WyzeResponse:
        """Locks a lock.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: WyzeResponse
        """
        return self._control_lock(device_mac=device_mac, action="remoteLock")

    def unlock(self, device_mac: str, **kwargs) -> WyzeResponse:
        """Unlocks a lock.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: WyzeResponse
        """
        return self._control_lock(device_mac=device_mac, action="remoteUnlock")

    def get_records(self, *, device_mac: str, limit: int = 20, since: datetime, until: Optional[datetime] = None, offset: int = 0, **kwargs) -> Sequence[LockRecord]:
        """Retrieves event history records for a lock.

        .. note:: The results are queried and returned in reverse-chronological order.

        Args:
        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param datetime since: The starting datetime of the query i.e., the most recent datetime for returned records
        :param datetime until: The ending datetime of the query i.e., the oldest allowed datetime for returned records. This parameter is optional and defaults to ``None``
        :param int limit: The maximum number of records to return. Defaults to ``20``
        :param int offset: The number of records to skip when querying. Defaults to ``0``

        :rtype: Sequence[LockRecord]
        """
        return [LockRecord(**record) for record in super()._ford_client().get_family_records(uuid=Lock.parse_uuid(mac=device_mac), begin=since, end=until, limit=limit, offset=offset)["family_record"]]

    def get_keys(self, *, device_mac: str, **kwargs) -> Sequence[LockKey]:
        """Retrieves keys for a lock.

        Args:
        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Sequence[LockKey]
        """
        uuid = Lock.parse_uuid(mac=device_mac)
        return [LockKey(type=LockKeyType.ACCESS_CODE, **password) for password in super()._ford_client().get_passwords(uuid=uuid)["passwords"]]

    def info(self, *, device_mac: str, **kwargs) -> Optional[Lock]:
        """Retrieves details of a lock.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``

        :rtype: Optional[Lock]
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

    def _validate_access_code(self, access_code: str):
        if access_code is None or access_code.strip() == '':
            raise WyzeRequestError("access code must be a numeric code between 4 and 8 digits long")
        if re.match('\d{4,8}$', access_code) is None:
            raise WyzeRequestError(f"{access_code} is not a valid access code")

    def _encrypt_access_code(self, access_code: str) -> str:
        secret = self._ford_client().get_crypt_secret()["secret"]
        return CBCEncryptor(self._ford_client().WYZE_FORD_IV_HEX).encrypt(MD5Hasher().hash(secret), access_code).hex()

    def create_access_code(self, device_mac: str, access_code: str, name: Optional[str], permission: Optional[LockKeyPermission] = None, periodicity: Optional[LockKeyPeriodicity] = None, **kwargs) -> WyzeResponse:
        """Creates a guest access code on a lock.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param str access_code: The new access code. e.g. ``1234``
        :param str name: The name for the guest access code.
        :param LockKeyPermission permission: The access permission rules for the guest access code.
        :param Optional[LockKeyPeriodicity] periodicity: The recurrance rules for a recurring guest access code.

        :rtype: WyzeResponse

        :raises WyzeRequestError: if the new access code is not valid
        """
        self._validate_access_code(access_code=access_code)
        if permission.type == LockKeyPermissionType.RECURRING and periodicity is None:
            raise WyzeRequestError("periodicity must be provided when setting recurring permission")
        if permission.type == LockKeyPermissionType.ONCE:
            if permission.begin is None:
                permission.begin = datetime.now()
            if permission.end is None:
                permission.end = permission.begin + timedelta(days=30)
        if permission is None:
            permission = LockKeyPermission(type=LockKeyPermissionType.ALWAYS)

        uuid = Lock.parse_uuid(mac=device_mac)
        return self._ford_client().add_password(uuid=uuid, password=self._encrypt_access_code(access_code=access_code), name=name, permission=permission, periodicity=periodicity, userid=self._user_id)

    def delete_access_code(self, device_mac: str, access_code_id: int, **kwargs) -> WyzeResponse:
        """Deletes an access code from a lock.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param int access_code_id: The id of the access code to delete.

        :rtype: WyzeResponse
        """
        uuid = Lock.parse_uuid(mac=device_mac)
        return self._ford_client().delete_password(uuid=uuid, password_id=str(access_code_id))

    def update_access_code(self, device_mac: str, access_code_id: int, access_code: Optional[str] = None, name: Optional[str] = None, permission: LockKeyPermission = None, periodicity: Optional[LockKeyPeriodicity] = None, **kwargs) -> WyzeResponse:
        """Updates an existing access code on a lock.

        :param str device_mac: The device mac. e.g. ``ABCDEF1234567890``
        :param int access_code_id: The id of the access code to reset.
        :param Optional[str] access_code: The new access code. e.g. ``1234``
        :param Optional[str] name: The new name for the guest access code.
        :param LockKeyPermission permission: The access permission rules for the guest access code.
        :param Optional[LockKeyPeriodicity] periodicity: The recurrance rules for a recurring guest access code.

        :rtype: WyzeResponse

        :raises WyzeRequestError: if the new access code is not valid
        """
        self._validate_access_code(access_code=access_code)
        if permission is None:
            raise WyzeRequestError("permission must be provided")
        if permission.type == LockKeyPermissionType.RECURRING and periodicity is None:
            raise WyzeRequestError("periodicity must be provided when setting recurring permission")

        uuid = Lock.parse_uuid(mac=device_mac)
        return self._ford_client().update_password(uuid=uuid, password_id=str(access_code_id), password=self._encrypt_access_code(access_code=access_code), name=name, permission=permission, periodicity=periodicity)

    @property
    def gateways(self) -> LockGatewaysClient:
        """Returns a lock gateway client.

        :rtype: LockGatewaysClient
        """
        return LockGatewaysClient(token=self._token, base_url=self._base_url, logger=self._logger)
