from typing import Annotated
from enum import IntEnum

from fastapi import (
    Body,
    Depends,
)
from fastapi.responses import JSONResponse

from ...base import app
from database import (
    DeveloperAPIKey,
    Opportunity,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import (
    CreateModel,
)
import middleware
import formatters as fmt


class ErrorCode(IntEnum):
    INVALID_PROVIDER_ID = 200
    INVALID_INDUSTRY_ID = 201


@app.post('/{language}/private/opportunity')
async def create(
    language: Language,
    body: Annotated[CreateModel, Body()],
    api_key: Annotated[
        DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    provider = middleware.getters.get_provider_by_id(
        body.provider,
        language=language,
        error_code=ErrorCode.INVALID_PROVIDER_ID.value,
        path=['query', 'opp_create', 'provider_id'],
    )
    if isinstance(provider, fmt.ErrorTrace):
        return JSONResponse(provider.to_underlying(), status_code=422)
    industry = middleware.getters.get_industry_by_id(
        body.industry,
        language=language,
        error_code=ErrorCode.INVALID_INDUSTRY_ID.value,
        path=['query', 'opp_create', 'industry_id'],
    )
    if isinstance(provider, fmt.ErrorTrace):
        return JSONResponse(industry.to_underlying(), status_code=422)
    instance = Opportunity.create(
        body.fallback_language,
        body.name.to_document(),
        body.short_description.to_document(),
        body.source.to_document(),
        provider,
        body.category,
        industry,
    )
    return JSONResponse({'id': str(instance.id)})
