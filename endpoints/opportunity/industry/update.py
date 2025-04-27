# TODO:
#   1. PATCH /private/opportunity-industry?id={}&api_key={}

from typing import (
    Annotated, Any
)
from enum import IntEnum

from fastapi import Query, Body, Depends
from fastapi.responses import JSONResponse, Response
import pydantic

from database.models.opportunity import opportunity
from database.models.trans_string import Language

from database.models.trans_string.embedded import ContainedTransString, ContainedTransStringModel

import formatters as fmt
import middleware
from ...base import (
    app,
    ObjectId
)


class ErrorCode(IntEnum):
    INVALID_INDUSTRY_ID = 200


appender = fmt.enum.ErrorAppender[ErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            ErrorCode.INVALID_INDUSTRY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Opportunity industry with provided ID doesn\'t exist',
                    ru='Индустрии с таким идентификатором не существует',
                ),
                path=['body', 'industry', 'id']
            ),
        }
    )
)

@app.patch('/{language}/private/opportunity-industry')
async def patch(
    language: Language,
    industry_id: Annotated[ObjectId, Query()],
    body: Annotated[opportunity.OpportunityIndustryModel, Body()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    industry = middleware.getters.get_industry_by_id(
        industry_id,
        language=language,
        error_code=ErrorCode.INVALID_INDUSTRY_ID.value,
        path=['query', 'industry_id'],
    )
    if isinstance(industry, fmt.ErrorTrace):
        return JSONResponse(industry.to_underlying(), status_code=422)
    industry.update(body.name)
    return JSONResponse({})
