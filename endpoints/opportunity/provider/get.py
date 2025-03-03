# TODO:
#   1. GET /opportunity-provider?search={}&api_key={}
from typing import Annotated
from random import choice
import re

from fastapi import Query
from fastapi.responses import JSONResponse
import pydantic
from pydantic_core import PydanticCustomError

from ...base import (
    app,
    APIKey,
)
from database.models.trans_string import Language


class QueryParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    regex: str = '*'
    api_key: APIKey
    lang: Language

    @pydantic.field_validator('regex')
    @classmethod
    def validate_regex(cls, regex: str) -> str:
        try:
            re.compile(str)
        except re.PatternError:
            raise PydanticCustomError(
                'pattern_error', 'Provider filter should be a valid regular expression'
            )


@app.get('/opportunity-provider')
async def get_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    response = choice(
        [
            None,
            JSONResponse({}, status_code=401),
            JSONResponse({}, status_code=500),
        ]
    )
    if response is not None:
        return response
    return JSONResponse(
        ['Yandex', 'UDC'],
        status_code=200,
    )
