from typing import (
    Any,
    Annotated,
)
from enum import IntEnum

from fastapi import (
    Depends,
    Query,
    Body,
)
from fastapi.responses import JSONResponse

from ...base import (
    app,
    ObjectId,
)
from database import PersonalAPIKey
from database.models.opportunity.form import PostValidationErrorCode
import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202
    OPPORTUNITY_WITHOUT_FORM = 203
    PHONE_NUMBER_INVALID_COUNTRY_ID = 204
    PHONE_NUMBER_NON_WHITELIST_COUNTRY = 205
    INVALID_CHOICE = 206
    FILE_INVALID_ID = 207
    FILE_CANT_ACCESS = 208
    FILE_EXCEEDS_SIZE = 209


form_error_code_mapping = {
    PostValidationErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID: (
        ErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID.value
    ),
    PostValidationErrorCode.PHONE_NUMBER_NON_WHITELIST_COUNTRY: (
        ErrorCode.PHONE_NUMBER_NON_WHITELIST_COUNTRY.value
    ),
    PostValidationErrorCode.INVALID_CHOICE: ErrorCode.INVALID_CHOICE.value,
    PostValidationErrorCode.FILE_INVALID_ID: ErrorCode.FILE_INVALID_ID.value,
    PostValidationErrorCode.FILE_CANT_ACCESS: ErrorCode.FILE_CANT_ACCESS.value,
    PostValidationErrorCode.FILE_EXCEEDS_SIZE: ErrorCode.FILE_EXCEEDS_SIZE.value,
}


@app.post('/{language}/opportunity/response')
async def create(
    language: fmt.Language,
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[dict[str, Any], Body()],
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
    form = middleware.getters.get_opportunity_form_by_id(
        opportunity_id,
        language=language,
        error_code=ErrorCode.OPPORTUNITY_WITHOUT_FORM.value,
        path=['query', 'opportunity_id'],
    )
    if isinstance(form, fmt.ErrorTrace):
        return JSONResponse(form.to_underlying(), status_code=422)
    response = middleware.response.create_opportunity_form_response(
        form,
        api_key.user.fetch(),
        body,
        language=language,
        error_code_mapping=form_error_code_mapping,
        data_path=['body'],
    )
    if isinstance(response, fmt.ErrorTrace):
        return JSONResponse(response.to_underlying(), status_code=422)
    return JSONResponse({'id': str(response.id)})
