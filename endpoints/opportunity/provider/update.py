# TODO:
#   1. PATCH /private/opportunity-provider?id={}&api_key={}

from typing import (
    Annotated,
    Self,
    Literal,
)
from random import choice
from enum import IntEnum

from fastapi import Query, Body
from fastapi.responses import JSONResponse, Response
import pydantic

from database.models.opportunity import opportunity
from database.models.trans_string import Language

from database.models.trans_string.embedded import ContainedTransString

import formatters as fmt
from ...base import (
    app,
    ID,
    BaseQueryParams,
)

class QueryParams(BaseQueryParams):
    id: ID

class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    name: ContainedTransString


class DBError(IntEnum):
    INVALID_PROVIDER_ID = 200

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_PROVIDER_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Opportunity provider with provided ID doesn\'t exist',
                    ru='Компании с таким идентификатором не существует',
                ),
                path=['body', 'provider', 'id'] #TODO: ...
            ),
        }
    )
)

@app.patch("/{language}/private/opportunity-provider")
async def patch(
    language: Language, body: Annotated[BodyParams, Body()], query: Annotated[QueryParams, Query()]   
) -> Response:
    formatted_errors = fmt.ErrorTrace()
    if (old_instance := opportunity.OpportunityProvider.objects.get(id=query.id)) is None:
        appender(formatted_errors, DBError.INVALID_PROVIDER_ID, language)
    if len(formatted_errors.errors) == 0:
        instance = opportunity.OpportunityProvider.update(
            old_instance,
        )
        return JSONResponse({'id': instance.id})
    return JSONResponse(formatted_errors.to_underlying())