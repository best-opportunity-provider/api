# TODO:
#   1. PATCH /private/place?id={}&api_key={}

from typing import (
    Annotated,
    Self,
    Literal,
)
from random import choice
from enum import IntEnum

from fastapi import Query, Body
from fastapi.responses import JSONResponse, Response
import pydantic
from pydantic_core import PydanticCustomError

from database.models.trans_string import Language
from database.models import geo

from database.models.geo import (
    Country,
    City,
)
from database.models.trans_string.embedded import ContainedTransString, ContainedTransStringModel

import formatters as fmt
from ...base import (
    app,
    ID,
    BaseQueryParams,
)


class QueryParams(BaseQueryParams):
    id: ID
   

class CityModel(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }
    type: Literal['city']
    id: ID


class CountryModel(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }
    type: Literal['country']
    id: ID


class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }
    name: ContainedTransStringModel
    location: Annotated[CityModel | CountryModel, pydantic.Field(discriminator='type')]


class DBError(IntEnum):
    INVALID_COUNTRY_ID = 200
    INVALID_CITY_ID = 201

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_COUNTRY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Coutry with provided ID doesn\'t exist',
                    ru='Страны с таким идентификатором не существует',
                ),
                path=['body', 'location', 'id']
            ),
            DBError.INVALID_CITY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='City with provided ID doesn\'t exist',
                    ru='Города с таким идентификатором не существует',
                ),
                path=['body', 'location', 'id']
            ),
            DBError.INVALID_PLACE_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Place with provided ID doesn\'t exist',
                    ru='Местоположения с таким идентификатором не существует',
                ),
                path=['body', 'place', 'id']
            ),
        }
    )
)

@app.patch('/{language}/private/place')
async def patch(
    language: Language, body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> Response:
    formatted_errors = fmt.ErrorTrace()
    if body.location.type == 'country':
        if (instance := geo.Country.objects.get(id=body.location.id)) is not None:
            location = instance
        else:
            appender(formatted_errors, DBError.INVALID_COUNTRY_ID, query.language)
    else:
        if (instance := geo.City.objects.get(id=body.location.id)) is not None:
            location = instance
        else:
            appender(formatted_errors, DBError.INVALID_CITY_ID, language)

    if (old_instance := geo.Place.objects.get(id=query.id)) is None:
        appender(formatted_errors, DBError.INVALID_PLACE_ID, language)

    if len(formatted_errors.errors) == 0:
        instance = geo.Place.update(old_instance, body.name.content, location)
        return JSONResponse({'id': instance.id})
    return JSONResponse(formatted_errors.to_underlying())

async def patch_mock(query: Annotated[QueryParams, Query()]) -> Response:
    response = choice(
        [
            None,
            Response(status_code=401),
            Response(status_code=422),
            Response(status_code=500),
        ]
    )
    if response is not None:
        return response
    return Response(status_code=200)
