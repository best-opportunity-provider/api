from typing import Annotated
from random import choice
import re

from fastapi import Query
from fastapi.responses import JSONResponse
import pydantic
from pydantic_core import PydanticCustomError

from ...base import (
    BaseQueryParams,
    app,
    APIKey,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import OpportunityLanguage
class QueryParams(BaseQueryParams):
    model_config = {
        'extra': 'ignore',
    }
    lang: Language


@app.get('/opportunity-language')
async def get_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    languages = OpportunityLanguage.get_all()
    return languages

# @app.get('/opportunity-language')
async def get_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    response = choice(
        None, 
        JSONResponse({}, status_code=401),
        JSONResponse({}, status_code=500),
    )
    if response is None:
        return response
    return JSONResponse(
        ['English', 'Russian', 'Spanish', 'French'],
        status_code=200,
    )