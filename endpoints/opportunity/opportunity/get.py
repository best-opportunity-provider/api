from typing import (
    Annotated,
    Any,
)
from enum import IntEnum

from fastapi import (
    Query,
    Depends,
)
from fastapi.responses import JSONResponse

from ...base import (
    app,
    ObjectId,
)
from database.models.trans_string import Language
from database.models.user import UserTier

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 203
    NOT_FREE_OPPORTUNITY = 204


@app.get('/{language}/opportunity')
async def get_opportunity_by_id(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    api_key: Annotated[
        Any | fmt.ErrorTrace, Depends(middleware.auth.GetPersonalAPIKeyWithTier(UserTier.PAID))
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=api_key.error_code)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code_mapping={'doesnt_exist': ErrorCode.INVALID_OPPORTUNITY_ID.value},
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, fmt.ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    return JSONResponse(opportunity.to_dict(language))


@app.get('/{language}/opportunity/min')
async def get_opportunity_by_id_min(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=api_key.error_code)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code_mapping={'doesnt_exist': ErrorCode.INVALID_OPPORTUNITY_ID.value},
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, fmt.ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    return JSONResponse(opportunity.to_dict_min(language))


@app.get('/{language}/opportunity/free')
async def get_opportunity_by_id_free(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=api_key.error_code)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code_mapping={
            'doesnt_exist': ErrorCode.INVALID_OPPORTUNITY_ID.value,
            'not_free': ErrorCode.NOT_FREE_OPPORTUNITY.value,
        },
        path=['query', 'opportunity_id'],
        free=True,
    )
    if isinstance(opportunity, fmt.ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    return JSONResponse(opportunity.to_dict(language))
