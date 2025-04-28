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


@app.post('/{language}/private/opportunity/section')
async def create(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[Union[opportunity.MarkdownSectionModel], pydantic.Field(discriminator='type'), Body()],
    api_key: Annotated[DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opp = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language='en',
        error_code_mapping={'doesnt_exist': ErrorCode.INVALID_OPPORTUNITY_ID.value},
        path=['query', 'opportunity', 'section'],
    )
    if isinstance(opp, fmt.ErrorTrace):
        return JSONResponse(opp.to_underlying(), status_code=422)
    if body.type == 'markdown':
        instance = opportunity.MarkdownSection.create(body.title, body.content)
        opp.add_section(body.type, str(instance.id))
    else:
        raise 1
    return JSONResponse({'id': str(instance.id)})
