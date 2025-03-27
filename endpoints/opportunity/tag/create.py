# TODO:
#   1. POST /private/opportunity-tag?api_key={}
from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse

import pydantic

from database.models.opportunity import opportunity
from database.models.trans_string.embedded import ContainedTransString

from ...base import (
    app,
    BaseQueryParams,
)
class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    name: ContainedTransString


@app.post('private/opportunity-tag')
async def create(body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> JSONResponse:
    instance = opportunity.OpportunityTag.create(body.name)
    return JSONResponse({'id': instance.id})