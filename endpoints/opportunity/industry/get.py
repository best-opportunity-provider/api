from typing import Annotated
from random import choice

from fastapi import Query
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    app,
    APIKey,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import OpportunityIndustry


class QueryParams(pydantic.BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: APIKey
    lang: Language


@app.get('/opportunity-industry')
async def get(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    industries = OpportunityIndustry.get_all()
    return industries


# @app.get('/opportunity-industry')
async def get_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    response = choice(
        [
            None,
            JSONResponse({}, status_code=401),
            JSONResponse({}, status_code=500),
        ]
    )
    if response is not None:
        return response
    return JSONResponse(
        ['IT', 'Hotel business', 'Art', 'Medicine'],
        status_code=200,
    )
