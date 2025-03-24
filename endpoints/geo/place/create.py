# TODO:
#   1. POST /private/place?api_key={}

from typing import Annotated
from random import choice

from fastapi import Query, Body
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    app,
    BaseQueryParams,
    generate_object_id,
)
from database.models.trans_string import Language
from database.models.geo import (
    Country,
    City,
)
from database.models import geo


class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    name: str
    language: Language
    location: Country | City


@app.post('/private/place')
async def create(
    body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> JSONResponse:
    instance = geo.Place.create(body.name, body.language, body.location)
    return JSONResponse({'id': instance.id})


async def create_mock(query: Annotated[BaseQueryParams, Query()]) -> JSONResponse:
    response = choice(
        [
            None,
            JSONResponse({}, status_code=401),
            JSONResponse({}, status_code=500),
            JSONResponse({}, status_code=422),
        ]
    )
    if response is not None:
        return response
    return JSONResponse({'id': generate_object_id()})
