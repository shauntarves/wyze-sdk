from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence, Set, Union

from wyze_sdk.models import (JsonObject, PropDef, epoch_to_datetime,
                             show_unknown_key_warning)
from wyze_sdk.models.devices import AbstractWirelessNetworkedDevice, DeviceProp


class ScaleProps(object):
    """
    :meta private:
    """

    @classmethod
    def unit(cls) -> PropDef:
        return PropDef('unit', str, acceptable_values=['kg', 'lb'])

    @classmethod
    def _convert_kg_to_lb(cls, value: float) -> float:
        return round(value * 2.20462262185, 2)


class ScaleSegmentMeasurement(JsonObject):
    """
    Segment body composition from a scale with hand electrodes, such as the
    Scale Ultra BodyScan. This includes fat and muscle mass in kilograms for
    each arm and leg and for the trunk/torso. The trunk and limb fat values
    approximately add up to the record's total body fat mass.

    See: com.wyze.pluto.model.ICAFElectrode
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "left_arm_fat_kg",
            "left_arm_muscle_kg",
            "left_leg_fat_kg",
            "left_leg_muscle_kg",
            "right_arm_fat_kg",
            "right_arm_muscle_kg",
            "right_leg_fat_kg",
            "right_leg_muscle_kg",
            "trunk_fat_kg",
            "trunk_muscle_kg",
        }

    def __init__(
        self,
        *,
        left_arm_fat_kg: float = None,
        left_arm_muscle_kg: float = None,
        left_leg_fat_kg: float = None,
        left_leg_muscle_kg: float = None,
        right_arm_fat_kg: float = None,
        right_arm_muscle_kg: float = None,
        right_leg_fat_kg: float = None,
        right_leg_muscle_kg: float = None,
        trunk_fat_kg: float = None,
        trunk_muscle_kg: float = None,
        **others: dict
    ):
        # The API calls the trunk all_body and leaves "fat" out of the fat
        # values' names, e.g. left_arm_kg.
        self.left_arm_fat_kg = left_arm_fat_kg if left_arm_fat_kg else self._extract_attribute('left_arm_kg', others)
        self.left_arm_muscle_kg = left_arm_muscle_kg if left_arm_muscle_kg else self._extract_attribute('left_arm_muscle_kg', others)
        self.left_leg_fat_kg = left_leg_fat_kg if left_leg_fat_kg else self._extract_attribute('left_leg_kg', others)
        self.left_leg_muscle_kg = left_leg_muscle_kg if left_leg_muscle_kg else self._extract_attribute('left_leg_muscle_kg', others)
        self.right_arm_fat_kg = right_arm_fat_kg if right_arm_fat_kg else self._extract_attribute('right_arm_kg', others)
        self.right_arm_muscle_kg = right_arm_muscle_kg if right_arm_muscle_kg else self._extract_attribute('right_arm_muscle_kg', others)
        self.right_leg_fat_kg = right_leg_fat_kg if right_leg_fat_kg else self._extract_attribute('right_leg_kg', others)
        self.right_leg_muscle_kg = right_leg_muscle_kg if right_leg_muscle_kg else self._extract_attribute('right_leg_muscle_kg', others)
        self.trunk_fat_kg = trunk_fat_kg if trunk_fat_kg else self._extract_attribute('all_body_kg', others)
        self.trunk_muscle_kg = trunk_muscle_kg if trunk_muscle_kg else self._extract_attribute('all_body_muscle_kg', others)
        show_unknown_key_warning(self, others)


class ScaleRecord(JsonObject):
    """
    A scale record.

    ``impedance`` holds the raw impedance readings: ten on eight-electrode
    scales such as the Scale Ultra BodyScan, and four on other scales. When
    no impedance was measured, readings are usually 0 but can be ``None``.
    The body composition calculated from them is in the other fields, such
    as ``body_fat``, ``muscle`` and ``body_segments``.

    See: com.wyze.ihealth.bean.GsonHs2sResults.DataBean and, for scales on the
    Pluto service, com.wyze.pluto.db.duomain.WplWeight
    """

    @property
    def attributes(self) -> Set[str]:
        return {
            "id",
            "age",
            "bmi",
            "bmr",
            "body_fat",
            "body_score",
            "body_segments",
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
            "muscle_protection_index",
            "occupation",
            "protein",
            "skeletal_muscle",
            "subcutaneous_fat",
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
        body_score: int = None,
        body_segments: Union[dict, ScaleSegmentMeasurement] = None,
        body_type: int = None,
        body_vfr: float = None,
        body_water: float = None,
        bone_mineral: float = None,
        device_id: str = None,
        family_member_id: str = None,
        gender: int = None,
        height: float = None,
        impedance: Sequence[float] = None,
        mac: str = None,
        measure_ts: int = None,
        measure_type: int = None,
        metabolic_age: int = None,
        muscle: float = None,
        muscle_protection_index: float = None,
        occupation: int = None,
        protein: float = None,
        skeletal_muscle: float = None,
        subcutaneous_fat: float = None,
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
        self.body_score = body_score if body_score else self._extract_attribute('body_score', others)
        self.body_segments = body_segments if body_segments else self._extract_attribute('measurement_data', others)
        if isinstance(self.body_segments, dict):
            self.body_segments = ScaleSegmentMeasurement(**self.body_segments)
        self.body_type = body_type if body_type else self._extract_attribute('body_type', others)
        self.body_vfr = body_vfr if body_vfr else self._extract_attribute('body_vfr', others)
        self.body_water = body_water if body_water else self._extract_attribute('body_water', others)
        self.bone_mineral = bone_mineral if bone_mineral else self._extract_attribute('bone_mineral', others)
        self.device_id = device_id if device_id else self._extract_attribute('device_id', others)
        self.family_member_id = family_member_id if family_member_id else self._extract_attribute('family_member_id', others)
        self.gender = gender if gender else self._extract_attribute('gender', others)
        self.height = height if height else self._extract_attribute('height', others)
        # Eight-electrode scales send all ten readings as an impedances list
        # instead of impedance1 to impedance4.
        self.impedance = impedance if impedance else [
            self._extract_attribute('impedance1', others),
            self._extract_attribute('impedance2', others),
            self._extract_attribute('impedance3', others),
            self._extract_attribute('impedance4', others),
        ]
        impedances = self._extract_attribute('impedances', others)
        if impedances and not impedance:
            self.impedance = impedances
        self.mac = mac if mac else self._extract_attribute('mac', others)
        self.measure_ts = measure_ts if measure_ts else self._extract_attribute('measure_ts', others)
        self.measure_type = measure_type if measure_type else self._extract_attribute('measure_type', others)
        self.metabolic_age = metabolic_age if metabolic_age else self._extract_attribute('metabolic_age', others)
        self.muscle = muscle if muscle else self._extract_attribute('muscle', others)
        self.muscle_protection_index = muscle_protection_index if muscle_protection_index else self._extract_attribute('muscle_protection_index', others)
        self.occupation = occupation if occupation else self._extract_attribute('occupation', others)
        self.protein = protein if protein else self._extract_attribute('protein', others)
        self.skeletal_muscle = skeletal_muscle if skeletal_muscle else self._extract_attribute('skeletal_muscle', others)
        self.subcutaneous_fat = subcutaneous_fat if subcutaneous_fat else self._extract_attribute('subcutaneous_fat', others)
        self.timezone = timezone if timezone else self._extract_attribute('timezone', others)
        self.user_id = user_id if user_id else self._extract_attribute('user_id', others)
        self._weight = weight if weight else self._extract_attribute('weight', others)
        show_unknown_key_warning(self, others)

    @property
    def weight(self, unit: str = 'lb'):
        if self._weight is None:
            return None
        if unit == 'lb':
            return ScaleProps._convert_kg_to_lb(self._weight)
        return self._weight


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
        self._current_weight = current_weight if current_weight else self._extract_attribute('current_weight', others)
        self.family_member_id = family_member_id if family_member_id else self._extract_attribute('family_member_id', others)
        self._goal_weight = goal_weight if goal_weight else self._extract_attribute('goal_weight', others)
        self.updated = updated if updated else epoch_to_datetime(self._extract_attribute('update_time', others), ms=True)
        self.user_id = user_id if user_id else self._extract_attribute('user_id', others)
        show_unknown_key_warning(self, others)

    @property
    def goal_weight(self, unit: str = 'lb'):
        if self._goal_weight is None:
            return None
        if unit == 'lb':
            return ScaleProps._convert_kg_to_lb(self._goal_weight)
        return self._goal_weight

    @property
    def current_weight(self, unit: str = 'lb'):
        if self._current_weight is None:
            return None
        if unit == 'lb':
            return ScaleProps._convert_kg_to_lb(self._current_weight)
        return self._current_weight


class Scale(AbstractWirelessNetworkedDevice):

    type = "WyzeScale"

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
        self.unit = unit if unit else super()._extract_property(ScaleProps.unit(), others)
        self._broadcast = super()._extract_attribute('broadcast', others)
        self.goal_weight = goal_weight
        self._latest_records = []
        latest_records = latest_records if latest_records is not None else super()._extract_attribute('latest_records', others)
        if latest_records is not None:
            self._latest_records = [latest_record if isinstance(latest_record, ScaleRecord) else ScaleRecord(**latest_record) for latest_record in latest_records]
        self._device_members = super()._extract_attribute('device_members', others)
        self._user_profile = super()._extract_attribute('user_profile', others)
        show_unknown_key_warning(self, others)

    @property
    def unit(self) -> str:
        return None if self._unit is None else self._unit.value

    @unit.setter
    def unit(self, value: Union[str, DeviceProp]):
        if isinstance(value, str):
            value = DeviceProp(definition=ScaleProps.unit(), value=value)
        self._unit = value

    @property
    def broadcast(self) -> bool:
        return self._broadcast

    @property
    def device_members(self) -> Sequence[dict]:
        return self._device_members

    @property
    def user_profile(self) -> dict:
        return self._user_profile

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
