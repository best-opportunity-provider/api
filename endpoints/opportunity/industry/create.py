# TODO:
#   1. POST /private/opportunity-industry?api_key={}

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


@app.post('/{language}/private/opportunity-industry')
async def create_industry(
    language: Language,
    body: Annotated[opportunity.OpportunityIndustryModel, Body()],
    api_key: Annotated[DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    instance = opportunity.OpportunityIndustry.create(body.name)
    return JSONResponse({'id': str(instance.id)})
