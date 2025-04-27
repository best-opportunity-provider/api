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
    countries: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]
    cities: Annotated[list[ObjectId], pydantic.Field(default_factory=list)]
    translations: Annotated[list[Language], pydantic.Field(default_factory=list)]


@app.post('/opportunities')
async def filter(
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
    body: Annotated[OpportunityFilterBodyParams, Body()],
) -> JSONResponse:
    def contains(db_obj, py_objs) -> bool:
        return (db_obj.pk() in py_objs)

    def have_a_common(db_objs, py_objs) -> bool:
        return bool(set(map(lambda t: t.pk(), db_objs)).intersection(set(py_objs)))

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
    if body.countries:
        opportunities = filter(lambda opp: have_a_common(map(lambda t: t.country, opp.places), body.countries), opportunities)
    if body.cities:
        opportunities = filter(lambda opp: have_a_common(map(lambda t: t.city, opp.places), body.cities), opportunities)
    # TODO: lang
    return JSONResponse(list(opportunities))


# @app.post('/opportunities')
# async def filter_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
#     response = choice(
#         [
#             None,
#             JSONResponse({}, status_code=401),
#             JSONResponse({}, status_code=500),
#         ]
#     )
#     if response is not None:
#         return response
#     return JSONResponse(
#         [
#             {
#                 'id': generate_object_id(),
#                 'name': 'Software engineer',
#                 'short_description': 'Very cool mnogo denyag dota2',
#                 'provider': {
#                     'id': generate_object_id(),
#                     'name': 'UDC',
#                     'logo': 'https://example.com',
#                 },
#                 'industry': {
#                     'id': generate_object_id(),
#                     'name': 'IT',
#                 },
#                 'tags': [
#                     {'id': generate_object_id(), 'name': 'Rust'},
#                     {'id': generate_object_id(), 'name': 'Remote'},
#                 ],
#                 'languages': [
#                     {'id': generate_object_id(), 'name': 'Russian'},
#                     {'id': generate_object_id(), 'name': 'English'},
#                 ],
#                 'places': [
#                     {'id': generate_object_id(), 'name': 'Russia, Moscow, MIPT'},
#                     {'id': generate_object_id(), 'name': 'Russia, St.Petersburg, ITMO'},
#                 ],
#             },
#         ],
#         status_code=200,
#     )
