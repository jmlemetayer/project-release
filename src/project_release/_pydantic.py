"""Pydantic helpers."""
from typing import Any
from typing import List
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from pydantic import ValidationInfo
from pydantic import field_validator
from pydantic_core import PydanticUndefined

T = TypeVar("T")
Listable = Union[T, List[T]]


class UseDefaultValueModel(BaseModel):
    """Pydantic model for correct use of default values."""

    @field_validator("*", mode="before")
    @classmethod
    def _use_default_value_if_none(cls, data: Any, info: ValidationInfo) -> Any:
        if (
            info.field_name
            and cls.model_fields[info.field_name].get_default() is not PydanticUndefined
            and not cls.model_fields[info.field_name].is_required()
            and data is None
        ):
            return cls.model_fields[info.field_name].get_default()
        return data
