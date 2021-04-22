"""Classes for constructing Wyze-specific data strtucture"""

import distutils.util
import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime
from functools import wraps
from typing import (Any, Callable, Iterable, Optional, Sequence, Set, Union)

from wyze_sdk.errors import WyzeObjectFormationError, WyzeRequestError


def datetime_to_epoch(datetime: datetime, ms: bool = True) -> int:
    """
    Convert a python datetime to number of (milli-) seconds since epoch.
    """
    if ms:
        return int(datetime.timestamp() * 1000)
    return int(datetime.timestamp())


def epoch_to_datetime(epoch: Union[int, float], ms: bool = False) -> datetime:
    """
    Convert number of (milli-) seconds since epoch to a python datetime.
    """
    if isinstance(epoch, (int, float)):
        return datetime.fromtimestamp(float(epoch) / 1000 if ms else float(epoch))


def show_unknown_key_warning(name: Union[str, object], others: dict):
    if "type" in others:
        others.pop("type")
    if "product_type" in others:
        others.pop("product_type")
    if len(others) > 0:
        keys = ", ".join(others.keys())
        logger = logging.getLogger(__name__)
        if isinstance(name, object):
            name = name.__class__.__name__
        logger.debug(
            f"!!! {name}'s constructor args ({keys}) were ignored."
            f" If they should be supported by this library, report this issue to the project"
            f" https://github.com/shauntarves/wyze-sdk/issues"
        )


class BaseObject:
    def __str__(self):
        return f"<wyze_sdk.{self.__class__.__name__}>"


class JsonObject(BaseObject, metaclass=ABCMeta):

    @property
    @abstractmethod
    def attributes(self) -> Set[str]:
        """Provide a set of attributes of this object that will make up its JSON structure"""
        return set()

    def _extract_attribute(self, name: str, others: dict) -> Any:
        """
        Extracts a single value by name from a variety of locations in an object.
        """
        if name in others:
            return others.pop(name)
        elif 'property_list' in others:
            for property in others['property_list']:
                if (name == property['pid']):
                    return property['value']
        elif 'data' in others and 'property_list' in others['data']:
            for property in others['data']['property_list']:
                if (name == property['pid']):
                    return property['value']
        elif 'device_params' in others and name in others['device_params']:
            return self._extract_attribute(name, others['device_params'])
        elif 'device_setting' in others and name in others['device_setting']:
            return self._extract_attribute(name, others['device_setting'])

    def validate_json(self) -> None:
        """
        Raises:
          WyzeObjectFormationError if the object was not valid
        """
        for attribute in (func for func in dir(self) if not func.startswith("__")):
            method = getattr(self, attribute, None)
            if callable(method) and hasattr(method, "validator"):
                method()

    def get_non_null_attributes(self) -> dict:
        """
        Construct a dictionary out of non-null keys (from attributes property)
        present on this object.
        """
        def to_dict_compatible(
            value: Union[dict, list, object]
        ) -> Union[dict, list, Any]:
            if isinstance(value, list):  # skipcq: PYL-R1705
                return [to_dict_compatible(v) for v in value]
            else:
                to_dict = getattr(value, "to_dict", None)
                if to_dict and callable(to_dict):  # skipcq: PYL-R1705
                    return {
                        k: to_dict_compatible(v) for k, v in value.to_dict().items()  # type: ignore
                    }
                else:
                    return value

        def is_not_empty(self, key: str) -> bool:
            value = getattr(self, key, None)
            if value is None:
                return False
            has_len = getattr(value, "__len__", None) is not None
            if has_len:  # skipcq: PYL-R1705
                return len(value) > 0
            else:
                return value is not None

        return {
            key: to_dict_compatible(getattr(self, key, None))
            for key in sorted(self.attributes)
            if is_not_empty(self, key)
        }

    def to_dict(self, *args) -> dict:
        """
        Extract this object as a JSON-compatible, Wyze-API-valid dictionary.

        Args:
          *args: Any specific formatting args (rare; generally not required)
        Raises:
          WyzeObjectFormationError if the object was not valid
        """
        self.validate_json()
        return self.get_non_null_attributes()

    def __repr__(self):
        dict_value = self.get_non_null_attributes()
        if dict_value:  # skipcq: PYL-R1705
            return f"<wyze_sdk.{self.__class__.__name__}: {dict_value}>"
        else:
            return self.__str__()


class JsonValidator:

    def __init__(self, message: str):
        """
        Decorate a method on a class to mark it as a JSON validator. Validation
            functions should return true if valid, false if not.
        Args:
            message: Message to be attached to the thrown WyzeObjectFormationError
        """
        self.message = message

    def __call__(self, func: Callable) -> Callable[..., None]:
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            if not func(*args, **kwargs):
                raise WyzeObjectFormationError(self.message)

        wrapped_f.validator = True
        return wrapped_f


class EnumValidator(JsonValidator):

    def __init__(self, attribute: str, enum: Iterable[str]):
        super().__init__(
            f"{attribute} attribute must be one of the following values: "
            f"{', '.join(enum)}"
        )


class PropDef(object):
    """
    The translation definition to convert between the API data properties and
    reasonable python equivalents.
    """
    def __init__(
        self,
        pid: str,
        type: Any,
        api_type: Optional[Any] = None,
        acceptable_values: Optional[Sequence[Any]] = None,
    ):
        self._pid = pid
        self._type = type
        self._api_type = api_type
        self._acceptable_values = acceptable_values

    @property
    def pid(self):
        return self._pid

    @property
    def api_type(self):
        return self._api_type

    @property
    def type(self):
        return self._type

    def validate(self, value: Any):
        if not isinstance(value, self._type):
            try:
                value = bool(distutils.util.strtobool(str(value))) if self._type == bool else self._type(value)
            except TypeError:
                logging.debug(f"could not cast value {value} into expected type {self._type}")
                raise WyzeRequestError(f"{value} must be of type {self._type}")

        if self._acceptable_values is None:
            logging.debug("acceptable_values is not set, passing")
            return

        if value in self._acceptable_values:
            logging.debug(f"value {value} found in acceptable_values, passing")
            return

        raise WyzeRequestError(f"{value} must be one of {self.acceptable_values}")
