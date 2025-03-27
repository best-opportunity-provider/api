# TODO:
#   1. POST /private/opportunity?api_key={}
from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse
import pydantic

from database.models.geo import Place
from database.models.trans_string.embedded import TransString

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


@app.post('/private/opportunity')
async def create(
    body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> JSONResponse:
    instance = opportunity.Opportunity.create(
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
