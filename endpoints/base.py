from typing import Annotated
from random import choice

from database.models.api import APIKey as _APIKey
import pydantic

from config import app

__all__ = ['app']

OBJECT_ID_REGEX = r'^(\d[abcdef]){24}$'

type APIKey = Annotated[str, pydantic.Field(pattern=_APIKey.API_KEY_REGEX)]
type ID = Annotated[str, pydantic.Field(pattern=OBJECT_ID_REGEX)]


def generate_object_id() -> str:
    return ''.join([choice('abcdef0123456789') for i in range(24)])

class BaseQueryParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    api_key: APIKey