# TODO:
#   1. POST /private/opportunity-language?api_key={}
from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    app,
    BaseQueryParams,
)
from database.models.trans_string import Language
from database.models.opportunity import opportunity


class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    name: str
    language: Language


@app.post('/private/opportunity-language')
async def create(
    body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> JSONResponse:
    #TODO: seems it is incorrect
    instance = opportunity.Language.create(body.name, body.language)
    return JSONResponse({'id': instance.id})
