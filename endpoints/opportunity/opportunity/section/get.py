from enum import IntEnum
from typing import Annotated
from random import choice

from fastapi import Query, Depends
from fastapi.responses import JSONResponse
import pydantic

from ....base import (
    ObjectId,
    APIKey,
    app,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import Opportunity

from database import PersonalAPIKey
import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_SECTION_ID = 200


@app.get('/opportunity/sections')
async def get_all_sections(
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    sections = OpportunitySection.get_all()
    return sections


@app.get('/{language}/opportunity/section')
async def get_section_by_id(
    language: Language,
    section_id: Annotated[ObjectId, Query()],
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
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
    return JSONResponse(section.to_dict(language))
