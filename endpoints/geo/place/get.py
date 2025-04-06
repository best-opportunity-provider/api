from enum import IntEnum
from typing import Annotated

from fastapi import Query
from fastapi.responses import JSONResponse

from ...base import (
    ID,
    BaseQueryParams,
    escape_for_regex,
    app,
)
from database.models.geo import Place
import formatters as fmt
from formatters import Language


class GetByIdQueryParams(BaseQueryParams):
    id: ID


class GetByIdError(IntEnum):
    INVALID_ID = 200


appender = fmt.enum.ErrorAppender[GetByIdError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            GetByIdError.INVALID_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en="Place with provided ID doesn't exist",
                    ru='Локации с таким идентификатором не существует',
                ),
                path=['query', 'id'],
            ),
        }
    )
)


@app.get('/{language}/place')
async def get(
    language: Language,
    query: Annotated[GetByIdQueryParams, Query()],
) -> JSONResponse:
    instance: Place | None = Place.objects.get(id=query.id)
    if instance is None:
        formatted_errors = fmt.ErrorTrace()
        appender(formatted_errors, GetByIdError.INVALID_ID, language=language)
        return JSONResponse(formatted_errors, status_code=403)
    # TODO: return dict representation of a `Place`
    return JSONResponse({})


class GetAllQueryParams(BaseQueryParams):
    filter: str | None = None


@app.get('/{language}/places')
async def get_all(
    language: Language,
    query: Annotated[GetAllQueryParams, Query()],
) -> JSONResponse:
    if query.filter is None:
        places = Place.get_all()
    else:
        places = Place.get_all(regex=escape_for_regex(query.filter))
    # TODO: return list of dicts with representations of `Place`s
    return JSONResponse([])
