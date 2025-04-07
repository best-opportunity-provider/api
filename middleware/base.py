from typing import Annotated

import pydantic

from database import APIKey as _APIKey
from database.models.pydantic_base import ObjectId


__all__ = [
    'APIKey',
    'ObjectId',
]

type APIKey = Annotated[str, pydantic.Field(pattern=_APIKey.API_KEY_REGEX)]
