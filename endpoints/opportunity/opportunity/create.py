# TODO:
#   1. POST /private/opportunity?api_key={}
from typing import Annotated
from enum import IntEnum

from fastapi import Query, Body, Depends
from fastapi.responses import JSONResponse
import pydantic

from database.models.geo import Place, PlaceModel
from database.models.opportunity.opportunity import CreateModel
from database.models.trans_string.embedded import TransString, TransStringModel

from ...base import (
    app
)
from database import DeveloperAPIKey
from database.models.trans_string import Language
from database.models.opportunity import opportunity
import middleware
import formatters as fmt


class ErrorCode(IntEnum):
    INVALID_PROVIDER_ID = 200
    INVALID_INDUSTRY_ID = 201


@app.post('/private/opportunity')
async def create(
    body: Annotated[CreateModel, Body()],
    api_key: Annotated[DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    provider = middleware.getters.get_provider_by_id(
        body.provider,
        language=language,
        error_code=ErrorCode.INVALID_PROVIDER_ID.value,
        path=['query', 'opp_create', 'provider_id'],
    )
    if isinstance(provider, ErrorTrace):
        return JSONResponse(provider.to_underlying(), status_code=422)

    industry = middleware.getters.get_industry_by_id(
        body.industry,
        language=language,
        error_code=ErrorCode.INVALID_INDUSTRY_ID.value,
        path=['query', 'opp_create', 'industry_id'],
    )
    if isinstance(provider, ErrorTrace):
        return JSONResponse(industry.to_underlying(), status_code=422)
    
    instance = opportunity.Opportunity.create(
        body.fallback_language,
        body.name,
        body.short_description,
        body.source,
        provider,
        body.category,
        industry
    )
    return JSONResponse({'id': str(instance.id)})
