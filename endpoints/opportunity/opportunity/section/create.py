# TODO:
#   1. POST /private/opportunity/section?opportunity={id}&api_key={}
from typing import Annotated, Union, Literal
from enum import IntEnum

from fastapi import Query, Body, Depends
from fastapi.responses import JSONResponse

import pydantic

from ....base import (
    ObjectId,
    app,
)
from database.models.trans_string import Language
from database.models.trans_string.embedded import (
    TransString,
    ContainedTransString,
    TransStringModel,
)
from database.models.opportunity import opportunity
from database import DeveloperAPIKey

import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202


class MarkdownSectionModel(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    type: Literal['markdown']
    title: TransStringModel
    content: TransStringModel


@app.post('/private/opportunity/section')
async def create(
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[Union[MarkdownSectionModel], pydantic.Field(discriminator='type'), Body()],
    api_key: Annotated[DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opp = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language='en',
        error_code=ErrorCode.INVALID_OPPORTUNITY_ID.value,
        path=['query', 'opportunity', 'section'],
    )
    if isinstance(opp, fmt.ErrorTrace):
        return JSONResponse(opp.to_underlying(), status_code=422)
    instance = opportunity.OpportunitySection.create(body.title, body.content)
    opp.update(push__sections=instance)
    return JSONResponse({'id': instance.id})
