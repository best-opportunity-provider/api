from enum import IntEnum
from typing import Annotated, Any
from random import choice

from fastapi import Query, Depends
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    app,
    ObjectId
)
from database.models.trans_string import Language
from database.models.geo import City, Country, Place

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_PLACE_ID = 200


@app.get('/{language}/place')
async def get_place(
    language: Language,
    place_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    place = middleware.getters.get_place_by_id(
        place_id,
        language=language,
        error_code=ErrorCode.INVALID_PLACE_ID.value,
        path=['body', 'place', 'id'],
    )
    if isinstance(industry, fmt.ErrorTrace):
        return JSONResponse(place.to_underlying(), status_code=422)
    return place.to_dict(language)


@app.get('/{language}/place/all')
async def get_all_languages(
    language: Language,
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
    regex: str
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    places = Place.get_all(regex=escape_for_regex(regex))
    return JSONResponse([i.to_dict(language) for i in places])
