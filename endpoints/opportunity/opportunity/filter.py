from typing import Annotated
from random import choice

from fastapi import Query, Body, Depends
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    ObjectId,
    APIKey,
    app,
)
from database import PersonalAPIKey
from database.models.trans_string import Language
from database.models.opportunity.opportunity import Opportunity

import formatters as fmt
import middleware


class OpportunityFilterBodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    providers: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]
    industries: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]
    tags: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]
    languages: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]
    places: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]


@app.post('/{language}/opportunities')
async def filter_opportunity(
    language: Language,
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
    body: Annotated[OpportunityFilterBodyParams, Body()],
) -> JSONResponse:
    def contains(db_obj, py_objs) -> bool:
        return (str(db_obj.id) in py_objs)

    def have_a_common(db_objs, py_objs) -> bool:
        return bool(set(map(lambda t: str(t.id), db_objs)).intersection(set(py_objs)))

    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    opportunities = Opportunity.get_all()
    # Filtering
    if body.providers:
        opportunities = filter(lambda opp: contains(opp.provider, body.providers), opportunities)
    if body.industries:
        opportunities = filter(lambda opp: contains(opp.industry, body.industries), opportunities)
    if body.tags:
        opportunities = filter(lambda opp: have_a_common(opp.tags, body.tags), opportunities)
    if body.languages:
        opportunities = filter(lambda opp: have_a_common(opp.languages, body.languages), opportunities)
    if body.places:
        opportunities = filter(lambda opp: have_a_common(opp.places, body.places), opportunities)
    return JSONResponse([str(i.id) for i in opportunities])
