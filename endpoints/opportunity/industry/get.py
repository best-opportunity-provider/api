from enum import IntEnum
from typing import Annotated, Any
from random import choice

from fastapi import Query, Depends
from fastapi.responses import JSONResponse
import pydantic

from ...base import app, ObjectId
from database.models.trans_string import Language
from database.models.opportunity.opportunity import OpportunityIndustry

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_INDUSTRY_ID = 200


@app.get('/{language}/opportunity-industry')
async def get(
    language: Language,
    industry_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    industry = middleware.getters.get_industry_by_id(
        industry_id,
        language=language,
        error_code=ErrorCode.INVALID_INDUSTRY_ID.value,
        path=['body', 'industry', 'id'],
    )
    if isinstance(industry, fmt.ErrorTrace):
        return JSONResponse(industry.to_underlying(), status_code=422)
    return industry.to_dict(language)


@app.get('/{language}/opportunity-industry/all')
async def get_all_industries(
    language: fmt.Language,
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    industries = OpportunityIndustry.get_all()
    return JSONResponse([i.to_dict(language) for i in industries])
