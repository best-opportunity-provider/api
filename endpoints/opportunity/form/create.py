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

from ...base import (
    app,
    ObjectId,
)
from database.models.opportunity.form import (
    OpportunityFormModel,
    CreateFieldErrorCode,
)
from formatters import (
    Language,
    ErrorTrace,
)
import middleware


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202
    PHONE_NUMBER_FIELD_INVALID_COUNTRY_ID = 203


@app.post('/{language}/private/opportunity/form')
async def create(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[OpportunityFormModel, Body()],
    api_key: Annotated[Any | ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code_mapping={'doesnt_exist': ErrorCode.INVALID_OPPORTUNITY_ID.value},
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    form = middleware.form.create_opportunity_form(
        opportunity,
        body,
        language=language,
        error_code_mapping={
            CreateFieldErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID: (
                ErrorCode.PHONE_NUMBER_FIELD_INVALID_COUNTRY_ID.value
            ),
        },
        model_path=['body'],
    )
    if isinstance(form, ErrorTrace):
        return JSONResponse(form.to_underlying(), status_code=422)
    return JSONResponse({'id': opportunity_id})
