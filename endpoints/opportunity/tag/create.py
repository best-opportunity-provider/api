from typing import Annotated

from fastapi import Query, Body, Depends
from fastapi.responses import JSONResponse

import pydantic

from ...base import (
    app,
)
from database import DeveloperAPIKey
from database.models.trans_string import Language
from database.models.opportunity import opportunity

import formatters as fmt
import middleware


@app.post('/{language}/private/opportunity-tag')
async def create_tag(
    language: Language,
    body: Annotated[opportunity.OpportunityTagModel, Body()],
    api_key: Annotated[DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    instance = opportunity.OpportunityTag.create(name=body.name)
    return JSONResponse({'id': str(instance.id)})
