# TODO:
#   1. DELETE /private/opportunity/section?id={}&api_key={}
from typing import Annotated, Union

from fastapi import Query, Body
from fastapi.responses import JSONResponse

import pydantic

from ....base import (
    ObjectId,
    app,
)
from database.models.trans_string import Language
from database.models.opportunity import opportunity

import middleware


class ErrorCode(IntEnum):
    INVALID_SECTION_ID = 202


@app.delete('/private/opportunity/section')
async def create(
    section_id: Annotated[ObjectId, Query()],
    api_key: Annotated[DeveloperAPIKey | ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    section = middleware.getters.get_section_by_id(
        section_id,
        language='en',
        error_code=ErrorCode.INVALID_SECTION_ID.value,
        path=['query', 'section_id'],
    )
    if isinstance(section, fmt.ErrorTrace):
        return JSONResponse(section.to_underlying(), status_code=422)
    section.delete()
    return JSONResponse({'ok': True})
