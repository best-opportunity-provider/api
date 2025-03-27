# TODO:
#   1. PATCH /private/opportunity?id={}&api_key={}

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
from pydantic_core import PydanticCustomError

from database.models.opportunity import opportunity
from database.models.trans_string import Language
from database.models import geo

from database.models.geo import (
    Country,
    City,
    Place,
)
from database.models.trans_string.embedded import ContainedTransString, TransString

import formatters as fmt
from ...base import (
    app,
    ID,
    BaseQueryParams,
)

class QueryParams(BaseQueryParams):
    id: ID

class ContainedTransStringParam(pydantic.BaseModel):
    model_config = {'extra': 'ignore'}
    content: ContainedTransString
    language: Language

class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }
    name: ContainedTransStringParam

class DBError(IntEnum):
    INVALID_OPPORTUNITY_ID = 200

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_OPPORTUNITY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Opportunity industry with provided ID doesn\'t exist',
                    ru='Индустрии с таким идентификатором не существует',
                ),
                path=['body', 'industry', 'id'] #TODO: ...
            ),
        }
    )
)

class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    fallback_language: Language
    name: TransString
    short_description: TransString
    source: opportunity.OpportunitySource
    provider: opportunity.OpportunityProvider
    industry: opportunity.OpportunityIndustry
    tags: list[opportunity.OpportunityTag]
    languages: list[opportunity.OpportunityLanguage]
    places: list[Place]
    sections: list[opportunity.OpportunitySection]

@app.patch("/{language}/private/opportunity")
async def patch(
    language: Language, body: Annotated[BodyParams, Body()], query: Annotated[QueryParams, Query()]   
) -> Response:
    formatted_errors = fmt.ErrorTrace()
    if (old_instance := opportunity.Opportunity.objects.get(id=query.id)) is None:
        appender(formatted_errors, DBError.INVALID_OPPORTUNITY_ID, language)
    if len(formatted_errors.errors) == 0:
        instance = opportunity.Opportunity.update(
            old_instance,
            body.fallback_language,
            body.name,
            body.short_description,
            body.source,
            body.provider,
            body.industry,
            body.tags,
            body.languages,
            body.places,
            body.sections,
        )
        return JSONResponse({'id': instance.id})
    return JSONResponse(formatted_errors.to_underlying())