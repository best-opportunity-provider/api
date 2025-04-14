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
    CreateFieldErrorCode,
    UpdateOpportunityFormModel,
)
import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202
    OPPORTUNITY_WITHOUT_FORM = 203
    PHONE_NUMBER_FIELD_INVALID_COUNTRY_ID = 204


@app.patch('/{language}/private/opportunity/form')
async def update(
    language: fmt.Language,
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[UpdateOpportunityFormModel, Body()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code=ErrorCode.INVALID_OPPORTUNITY_ID.value,
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, fmt.ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    form = middleware.getters.get_opportunity_form_by_id(
        opportunity_id,
        language=language,
        error_code=ErrorCode.OPPORTUNITY_WITHOUT_FORM.value,
        path=['query', 'opportunity_id'],
    )
    if isinstance(form, fmt.ErrorTrace):
        return JSONResponse(form.to_underlying(), status_code=422)
    errors = middleware.form.update_opportunity_form(
        form,
        body,
        language=language,
        error_code_mapping={
            CreateFieldErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID: (
                ErrorCode.PHONE_NUMBER_FIELD_INVALID_COUNTRY_ID.value
            ),
        },
        model_path=['body'],
    )
    if isinstance(errors, fmt.ErrorTrace):
        return JSONResponse(errors.to_underlying(), status_code=422)
    return JSONResponse({})
