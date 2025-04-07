from typing import Annotated

from fastapi import (
    Depends,
    Query,
)
from fastapi.responses import JSONResponse

from ...base import (
    app,
    BaseQueryParams,
    ObjectId,
)
from database import PersonalAPIKey
import formatters as fmt
import middleware


class QueryParams(BaseQueryParams):
    form_id: ObjectId


@app.post('/{language}/opportunity/response')
async def create(
    language: fmt.Language,
    query: Annotated[QueryParams, Query()],
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    ...  # TODO
    return JSONResponse({})
