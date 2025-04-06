from typing import Annotated
from random import choice

from database.models.api import APIKey as _APIKey
from database.models.pydantic_base import ObjectId
import pydantic

from config import app


__all__ = ['app']

type APIKey = Annotated[str, pydantic.Field(pattern=_APIKey.API_KEY_REGEX)]
type ID = ObjectId


def generate_object_id() -> str:
    return ''.join([choice('abcdef0123456789') for i in range(24)])


def escape_for_regex(string: str) -> str:
    import re

    return re.escape(string)


class BaseQueryParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    api_key: APIKey
