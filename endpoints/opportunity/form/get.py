from typing import (
    Any,
    Annotated,
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
from formatters import (
    Language,
    ErrorTrace,
)
import middleware


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202
    OPPORTUNITY_WITHOUT_FORM = 203


@app.get('/{language}/opportunity/form')
async def get(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    api_key: Annotated[Any | ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code=ErrorCode.INVALID_OPPORTUNITY_ID.value,
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)
    form = middleware.getters.get_opportunity_form_by_id(
        opportunity_id,
        language=language,
        error_code=ErrorCode.OPPORTUNITY_WITHOUT_FORM.value,
        path=['query', 'opportunity_id'],
    )
    if isinstance(form, ErrorTrace):
        return JSONResponse(form.to_underlying(), status_code=422)
    # IMPORTANT: `fmt.Language` and `database.Language` are different enums, but
    #            we rely on that their definitions are identical
    return JSONResponse(form.to_dict(language))
