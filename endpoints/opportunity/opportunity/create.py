# TODO:
#   1. POST /private/opportunity?api_key={}
from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse
import pydantic

from database.models.geo import Place, PlaceModel
from database.models.trans_string.embedded import TransString, TransStringModel

from ...base import (
    app
)
from database import DeveloperAPIKey
from database.models.trans_string import Language
from database.models.opportunity import opportunity
import middleware


class OpportunityCreateBodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    fallback_language: Language
    name: TransStringModel
    short_description: TransStringModel
    source: opportunity.OpportunitySourceModel
    provider: opportunity.OpportunityProviderModel
    industry: opportunity.OpportunityIndustryModel
    tags: list[opportunity.OpportunityTagModel]
    languages: list[opportunity.OpportunityLanguageModel]
    places: list[PlaceModel]
    sections: list[opportunity.OpportunitySectionModel]


@app.post('/private/opportunity')
async def create(
    body: Annotated[OpportunityCreateBodyParams, Body()],
    api_key: Annotated[DeveloperAPIKey | ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
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
