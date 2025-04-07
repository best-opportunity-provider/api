from random import choice

from database.models.pydantic_base import ObjectId
import pydantic

from config import app
from middleware.base import APIKey


__all__ = [
    'app',
    'APIKey',
    'ObjectId',
    'BaseQueryParams',
    'escape_for_regex',
]


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
