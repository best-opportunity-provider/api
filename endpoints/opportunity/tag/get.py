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
from database.models.opportunity.opportunity import OpportunityTag

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_TAG_ID = 200


@app.get('/{language}/opportunity-tag')
async def get_tag(
    language: Language,
    tag_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    tag = middleware.getters.get_tag_by_id(
        tag_id,
        language=language,
        error_code=ErrorCode.INVALID_TAG_ID.value,
        path=['body', 'tag', 'id'],
    )
    if isinstance(tag, fmt.ErrorTrace):
        return JSONResponse(tag.to_underlying(), status_code=422)
    return tag.to_dict(language)


@app.get('/{language}/opportunity-tag/all')
async def get_all_tags(
    language: Language,
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    tags = OpportunityTag.get_all()
    return JSONResponse([i.to_dict(language) for i in tags])
