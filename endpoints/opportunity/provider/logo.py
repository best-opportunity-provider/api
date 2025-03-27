# TODO:
#   1. GET /opportunity-provider/logo?id={}&api_key={}
#   2. PUT /private/opportunity-provider/logo?id={}&api_key={}

from enum import IntEnum
from typing import Annotated

from fastapi import Body, Query
from fastapi.responses import FileResponse, JSONResponse, Response
import pydantic

from database.models.file import File
from database.models.opportunity import opportunity
from formatters.base import Language

from ...base import (
    ID,
    BaseQueryParams,
    app,
)
from database.models.opportunity.opportunity import OpportunityIndustry

import formatters as fmt

class QueryParams(BaseQueryParams):
    id: ID

class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    logo: File

class DBError(IntEnum):
    INVALID_OPPORTUNITY_ID = 200

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_OPPORTUNITY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Opportunity with provided ID doesn\'t exist',
                    ru='Стажировки с таким идентификатором не существует',
                ),
                path=['body', 'provider', 'id'] #TODO: ...
            ),
        }
    )
)

@app.get('/{language}/opportunity-provider/logo')
async def get(
    language: Language, query: Annotated[QueryParams, Query()]) -> JSONResponse:
    formatted_errors = fmt.ErrorTrace()
    if (instance := opportunity.Opportunity.objects.get(id=query.id)) is None:
        appender(formatted_errors, DBError.INVALID_OPPORTUNITY_ID, language)
    if len(formatted_errors.errors) == 0:
        return FileResponse(instance.logo)
    return JSONResponse(formatted_errors.to_underlying())

@app.get('/{language}/private/opportunity-provider/logo')
async def patch(
    language: Language, body: Annotated[BodyParams, Body()], query: Annotated[QueryParams, Query()]   
) -> JSONResponse:
    formatted_errors = fmt.ErrorTrace()
    if (instance := opportunity.Opportunity.objects.get(id=query.id)) is None:
        appender(formatted_errors, DBError.INVALID_OPPORTUNITY_ID, language)
    if len(formatted_errors.errors) == 0:
        opportunity.Opportunity.set_logo(instance, body.logo)
        return JSONResponse({'id': instance.id})
    return JSONResponse(formatted_errors.to_underlying())
    