from typing import (
    Any,
    Annotated,
)
from enum import IntEnum

from fastapi import (
    Query,
    Body,
    Depends,
)
from fastapi.responses import JSONResponse

from ....base import (
    app,
    ObjectId,
)
import formatters as fmt
import middleware

from database.models.opportunity.opportunity import (
    OpportunitySectionModels
)


class ErrorCode(IntEnum):
    INVALID_SECTION_ID = 202


@app.patch('/{language}/private/opportunity/section')
async def update_section(
    language: fmt.Language,
    section_id: Annotated[ObjectId, Query()],
    body: Annotated[OpportunitySectionModels, Body()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    section = middleware.getters.get_section_by_id(
        section_id,
        language=language,
        error_code=ErrorCode.INVALID_SECTION_ID.value,
        path=['query', 'section_id'],
    )
    if isinstance(section, fmt.ErrorTrace):
        return JSONResponse(section.to_underlying(), status_code=422)
    section.update(body)
    return JSONResponse({})
