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
from database.models import geo


class QueryParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    regex: str = '*'
    api_key: APIKey
    lang: Language

    @pydantic.field_validator('regex')
    @classmethod
    def validate_regex(cls, regex) -> str:
        try:
            re.compile(str)
        except re.PatternError:
            raise PydanticCustomError(
                'pattern_error', 'Places filter should be a valid regular expression'
            )


@app.get('/place')
async def get(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    places = geo.Place.get_all(regex=query.regex)
    return JSONResponse(places, status_code=200)


# @app.get('/place')
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
        ['MIPT', 'HSE', 'MSU', 'ITMO'],
        status_code=200,
    )
