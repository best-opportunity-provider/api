# TODO:
#   1. GET /opportunity-tag?search={}&api_key={}
from enum import IntEnum
from typing import Annotated
from random import choice
import re

from fastapi import Query
from fastapi.responses import JSONResponse
import pydantic
from pydantic_core import PydanticCustomError

from ...base import (
    ID,
    BaseQueryParams,
    app,
    APIKey,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import OpportunityTag

import formatters as fmt

class QueryParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    regex: str = '*'
    api_key: APIKey
    lang: Language

    @pydantic.field_validator('regex')
    @classmethod
    def validate_regex(cls, regex: str) -> str:
        try:
            re.compile(str)
        except re.PatternError:
            raise PydanticCustomError(
                'pattern_error', 'Tags filter should be a valid regular expression'
            )

class QueryParamsByID(BaseQueryParams):
    model_config = {'extra': 'ignore'}

    id: ID

class DBError(IntEnum):
    INVALID_TAG_ID = 200

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_TAG_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Tag with provided ID doesn\'t exist',
                    ru='Тэга с таким идентификатором не существует',
                ),
                path=['body', 'tag', 'id']
            ),
        }
    )
)

@app.get('/{language}/opportunity')
async def get(language: Language, query: Annotated[QueryParamsByID, Query()]) -> JSONResponse:
    formatted_errors = fmt.ErrorTrace()
    if (instance := OpportunityTag.objects.get(id=query.id)) is not None:
        return JSONResponse(instance, status_code=200)
    appender(formatted_errors, DBError.INVALID_TAG_ID, language)
    return JSONResponse(formatted_errors.to_underlying())


@app.get('/opportunity-tag')
async def get_all(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    tags = OpportunityTag.get_all(regex=query.regex)
    return tags

# @app.get('/opportunity-tag')
async def get_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    response = choice (
        [
            None,
            JSONResponse({}, status_code=401),
            JSONResponse({}, status_code=500),
        ]
    )
    if response is not None:
        return response
    return JSONResponse(
        ['Rust', 'Cpp', 'Csharp', 'UDClang'],
        status_code=200,
    )