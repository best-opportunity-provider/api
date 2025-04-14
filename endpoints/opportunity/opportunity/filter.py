from typing import Annotated
from random import choice

from fastapi import Query
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    ObjectId,
    APIKey,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import Opportunity

class QueryParams(pydantic.BaseModel):
    model_config = ({'extra': 'ignore'},)

    api_key: APIKey
    lang: Language


class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    providers: Annotated[list[ID], pydantic.Field(default_factory=list)]
    industries: Annotated[list[ID], pydantic.Field(default_factory=list)]
    tags: Annotated[list[ID], pydantic.Field(default_factory=list)]
    languagess: Annotated[list[ID], pydantic.Field(default_factory=list)]
    countries: Annotated[list[ID], pydantic.Field(default_factory=list)]
    cities: Annotated[list[ID], pydantic.Field(default_factory=list)]
    translations: Annotated[list[Language], pydantic.Field(default_factory=list)]



@app.post('/opportunities')
async def filter(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    ...

# @app.post('/opportunities')
async def filter_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    response = choice(
        [
            None,
            JSONResponse({}, status_code=401),
            JSONResponse({}, status_code=500),
        ]
    )
    if response is not None:
        return response
    return JSONResponse(
        [
            {
                'id': generate_object_id(),
                'name': 'Software engineer',
                'short_description': 'Very cool mnogo denyag dota2',
                'provider': {
                    'id': generate_object_id(),
                    'name': 'UDC',
                    'logo': 'https://example.com',
                },
                'industry': {
                    'id': generate_object_id(),
                    'name': 'IT',
                },
                'tags': [
                    {'id': generate_object_id(), 'name': 'Rust'},
                    {'id': generate_object_id(), 'name': 'Remote'},
                ],
                'languages': [
                    {'id': generate_object_id(), 'name': 'Russian'},
                    {'id': generate_object_id(), 'name': 'English'},
                ],
                'places': [
                    {'id': generate_object_id(), 'name': 'Russia, Moscow, MIPT'},
                    {'id': generate_object_id(), 'name': 'Russia, St.Petersburg, ITMO'},
                ],
            },
        ],
        status_code=200,
    )
