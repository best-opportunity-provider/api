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
    INVALID_OPPORTUNITY_ID = 200


@app.get('/{language}/opportunity/sections')
async def get_all_sections(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code_mapping={'doesnt_exist': ErrorCode.INVALID_OPPORTUNITY_ID.value},
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, fmt.ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    return JSONResponse(opportunity.section_dict(language))
