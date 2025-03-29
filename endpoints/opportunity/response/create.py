# TODO:
#   1. POST /opportunity/response?opportunity={id}&api_key={}
from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse

import pydantic

from database.models.opportunity import response
from database.models.opportunity.form import OpportunityForm, OpportunityFormModel
from database.models.user import User

from ...base import (
    ID,
    app,
    BaseQueryParams,
)

class QueryParams(BaseQueryParams):
    opportunity: ID

class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    user: User
    form: OpportunityFormModel
    form_version: int
    data: dict


@app.post('/opportunity/response')
async def create(body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> JSONResponse:
    instance = response.OpportunityFormResponse.create(
        body.user,
        body.form,
        body.form_version,
        body.data
    )
    return JSONResponse({'id': instance.id})