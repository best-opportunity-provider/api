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
from database.models.opportunity.opportunity import OpportunityLanguage

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_LANGUAGE_ID = 200


@app.get('/{language}/opportunity-language')
async def get_language(
    language: Language,
    language_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    instance = middleware.getters.get_language_by_id(
        language_id,
        language=language,
        error_code=ErrorCode.INVALID_LANGUAGE_ID.value,
        path=['body', 'language', 'id'],
    )
    if isinstance(instance, fmt.ErrorTrace):
        return JSONResponse(instance.to_underlying(), status_code=422)
    return instance.to_dict(language)


@app.get('/{language}/opportunity-language/all')
async def get_all_languages(
    language: Language,
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    languages = OpportunityLanguage.get_all()
    return JSONResponse([i.to_dict(language) for i in languages])
