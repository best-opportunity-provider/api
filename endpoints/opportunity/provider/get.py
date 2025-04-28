# TODO:
#   1. GET /opportunity-provider?search={}&api_key={}
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
from database.models.opportunity.opportunity import OpportunityProvider

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_PROVIDER_ID = 200
    INVALID_REGEX = 201


@app.get('/{language}/opportunity-provider/all')
async def get_all_providers(
    language: Language,
    api_key: Annotated[
        Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    providers = OpportunityProvider.get_all(regex='')
    return JSONResponse([i.to_dict(language) for i in providers])


@app.get('/{language}/opportunity-provider/id')
async def get_provider_by_id(
    language: Language,
    provider_id: Annotated[ObjectId, Query()],
    api_key: Annotated[
        Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    provider = middleware.getters.get_provider_by_id(
        provider_id,
        language=language,
        error_code=ErrorCode.INVALID_PROVIDER_ID.value,
        path=['query', 'provider_id'],
    )
    if isinstance(provider, fmt.ErrorTrace):
        return JSONResponse(provider.to_underlying(), status_code=422)
    return JSONResponse(provider.to_dict(language))


@app.get('/{language}/opportunity-provider')
async def get_provider_by_regex(
    language: fmt.Language,
    search: Annotated[str, Query()],
    api_key: Annotated[
        Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    providers = OpportunityProvider.get_all(regex=f'{search}')
    return JSONResponse([i.to_dict(language) for i in providers])
