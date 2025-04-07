from typing import (
    Any,
    Annotated,
)

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
import formatters as fmt
import middleware


class QueryParams(BaseQueryParams):
    opportunity_id: ObjectId


@app.post('/{language}/opportunity/form')
async def create(
    language: fmt.Language,
    query: Annotated[QueryParams, Query()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    ...  # TODO
    return JSONResponse({})
