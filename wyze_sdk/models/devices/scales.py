from datetime import datetime
from typing import (Optional, Sequence, Set, Union)

from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime, show_unknown_key_warning)
from wyze_sdk.models.devices import (AbstractWirelessNetworkedDevice, DeviceProp)


class ScaleProps(object):

    @classmethod
    @property
    def unit(cls) -> PropDef:
        return PropDef('unit', str, acceptable_values=['kg', 'lb'])


class ScaleRecord(JsonObject):
    """
    A scale record.

    See: com.wyze.ihealth.bean.GsonHs2sResults.DataBean
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "age",
            "bmi",
            "bmr",
            "body_fat",
            "body_type",
            "body_vfr",
            "body_water",
            "bone_mineral",
            "device_id",
            "family_member_id",
            "gender",
            "height",
            "impedance",
            "mac",
            "measure_ts",
            "measure_type",
            "metabolic_age",
            "muscle",
            "occupation",
            "protein",
            "timezone",
            "user_id",
            "weight",
        }

    def __init__(
        self,
        *,
        id: str = None,
        age: int = None,
        bmi: float = None,
        bmr: float = None,
        body_fat: float = None,
        body_type: int = None,
        body_vfr: float = None,
        body_water: float = None,
        bone_mineral: float = None,
        device_id: str = None,
        family_member_id: str = None,
        gender: int = None,
        height: float = None,
        impedance: Sequence[int] = None,
        mac: str = None,
        measure_ts: int = None,
        measure_type: int = None,
        metabolic_age: int = None,
        muscle: float = None,
        occupation: int = None,
        protein: float = None,
        timezone: str = None,
        user_id: int = None,
        weight: float = None,
        **others: dict
    ):
        self.id = id if id else str(self._extract_attribute('data_id', others))
        self.age = age if age else self._extract_attribute('age', others)
        self.bmi = bmi if bmi else self._extract_attribute('bmi', others)
        self.bmr = bmr if bmr else self._extract_attribute('bmr', others)
        self.body_fat = body_fat if body_fat else self._extract_attribute('body_fat', others)
        self.body_type = body_type if body_type else self._extract_attribute('body_type', others)
        self.body_vfr = body_vfr if body_vfr else self._extract_attribute('body_vfr', others)
        self.body_water = body_water if body_water else self._extract_attribute('body_water', others)
        self.bone_mineral = bone_mineral if bone_mineral else self._extract_attribute('bone_mineral', others)
        self.device_id = device_id if device_id else self._extract_attribute('device_id', others)
        self.family_member_id = family_member_id if family_member_id else self._extract_attribute('family_member_id', others)
        self.gender = gender if gender else self._extract_attribute('gender', others)
        self.height = height if height else self._extract_attribute('height', others)
        self.impedance = impedance if impedance else [
            self._extract_attribute('impedance1', others),
            self._extract_attribute('impedance2', others),
            self._extract_attribute('impedance3', others),
            self._extract_attribute('impedance4', others),
        ]
        self.mac = mac if mac else self._extract_attribute('mac', others)
        self.measure_ts = measure_ts if measure_ts else self._extract_attribute('measure_ts', others)
        self.measure_type = measure_type if measure_type else self._extract_attribute('measure_type', others)
        self.metabolic_age = metabolic_age if metabolic_age else self._extract_attribute('metabolic_age', others)
        self.muscle = muscle if muscle else self._extract_attribute('muscle', others)
        self.occupation = occupation if occupation else self._extract_attribute('occupation', others)
        self.protein = protein if protein else self._extract_attribute('protein', others)
        self.timezone = timezone if timezone else self._extract_attribute('timezone', others)
        self.user_id = user_id if user_id else self._extract_attribute('user_id', others)
        self.weight = weight if weight else self._extract_attribute('weight', others)
        show_unknown_key_warning(self, others)


class UserGoalWeight(JsonObject):
    """
    A user goal weight record.

    See: com.wyze.ihealth.bean.GsonUserGoalWeight
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "created",
            "current_weight",
            "family_member_id",
            "goal_weight",
            "updated",
            "user_id",
        }

    def __init__(
        self,
        *,
        id: str = None,
        created: datetime = None,
        current_weight: float = None,
        goal_weight: float = None,
        family_member_id: str = None,
        updated: datetime = None,
        user_id: int = None,
        **others: dict
    ):
        self.id = id if id else str(self._extract_attribute('id', others))
        self.created = created if created else epoch_to_datetime(self._extract_attribute('create_time', others), ms=True)
        self.current_weight = current_weight if current_weight else self._extract_attribute('current_weight', others)
        self.family_member_id = family_member_id if family_member_id else self._extract_attribute('family_member_id', others)
        self.goal_weight = goal_weight if goal_weight else self._extract_attribute('goal_weight', others)
        self.updated = updated if updated else epoch_to_datetime(self._extract_attribute('update_time', others), ms=True)
        self.user_id = user_id if user_id else self._extract_attribute('user_id', others)
        show_unknown_key_warning(self, others)


class Scale(AbstractWirelessNetworkedDevice):

    type = "Scale"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "unit",
            "broadcast",
            "device_members",
            "goal_weight",
            "latest_records",
        })

    def __init__(
        self,
        unit: Optional[str] = None,
        goal_weight: Optional[UserGoalWeight] = None,
        latest_records: Optional[Sequence[ScaleRecord]] = None,
        **others: dict,
    ):
        super().__init__(type=self.type, **others)
        self.unit = unit if unit else super()._extract_property(ScaleProps.unit, others)
        self._broadcast = super()._extract_attribute('broadcast', others)
        self.goal_weight = goal_weight
        latest_records = latest_records if latest_records is not None else super()._extract_attribute('latest_records', others)
        if latest_records is not None:
            self._latest_records = [latest_record if isinstance(latest_record, ScaleRecord) else ScaleRecord(**latest_record) for latest_record in latest_records]
        self._device_members = super()._extract_attribute('device_members', others)
        show_unknown_key_warning(self, others)

    @property
    def unit(self) -> str:
        return None if self._unit is None else self._unit.value

    @unit.setter
    def unit(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=ScaleProps.unit, value=value)
        self._unit = value

    @property
    def broadcast(self) -> bool:
        return self._broadcast

    @property
    def device_members(self) -> Sequence[dict]:
        return self._device_members

    @property
    def goal_weight(self) -> UserGoalWeight:
        return self._goal_weight

    @goal_weight.setter
    def goal_weight(self, value: Union[dict, UserGoalWeight]):
        if isinstance(value, dict):
            value = UserGoalWeight(**value)
        self._goal_weight = value

    @property
    def latest_records(self) -> Sequence[ScaleRecord]:
        return self._latest_records
