from typing import Annotated
from enum import IntEnum

from fastapi import Query, Body
from fastapi.responses import JSONResponse

from database.models.trans_string import Language
from database.models.geo import (
    Place,
    PlaceModel,
)
import formatters as fmt
from ...base import (
    app,
    ID,
    BaseQueryParams,
)


class QueryParams(BaseQueryParams):
    id: ID


class Error(IntEnum):
    INVALID_PLACE_ID = 200
    INVALID_COUNTRY_ID = 201
    INVALID_CITY_ID = 202


appender = fmt.enum.ErrorAppender[Error](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            Error.INVALID_PLACE_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en="Place with provided ID doesn't exist",
                    ru='Локации с таким идентификатором не существует',
                ),
                path=['body', 'place', 'id'],
            ),
            Error.INVALID_COUNTRY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en="Coutry with provided ID doesn't exist",
                    ru='Страны с таким идентификатором не существует',
                ),
                path=['body', 'location', 'id'],
            ),
            Error.INVALID_CITY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en="City with provided ID doesn't exist",
                    ru='Города с таким идентификатором не существует',
                ),
                path=['body', 'location', 'id'],
            ),
        }
    )
)


@app.patch('/{language}/private/place')
async def patch(
    language: Language,
    body: Annotated[PlaceModel, Body()],
    query: Annotated[QueryParams, Query()],
) -> JSONResponse:
    # TODO: move this to some sort of a middleware, because exact same code appears in get
    instance = Place.objects.get(id=query.id)
    if instance is None:
        ...
        return JSONResponse({}, status_code=403)
    # TODO: retrieve actual `Country`/`City` instances from body and use them to update `Place`
    ...
    return JSONResponse({})
    # INVALID:
    # formatted_errors = fmt.ErrorTrace()
    # if body.location.type == 'country':
    #     if (instance := geo.Country.objects.get(id=body.location.id)) is not None:
    #         location = instance
    #     else:
    #         appender(formatted_errors, DBError.INVALID_COUNTRY_ID, query.language)
    # else:
    #     if (instance := geo.City.objects.get(id=body.location.id)) is not None:
    #         location = instance
    #     else:
    #         appender(formatted_errors, DBError.INVALID_CITY_ID, language)

    # if (old_instance := geo.Place.objects.get(id=query.id)) is None:
    #     appender(formatted_errors, DBError.INVALID_PLACE_ID, language)

    # if len(formatted_errors.errors) == 0:
    #     instance = geo.Place.update(old_instance, body.name.content, location)
    #     return JSONResponse({'id': instance.id})
    # return JSONResponse(formatted_errors.to_underlying())
