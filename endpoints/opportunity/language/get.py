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
from database.models.opportunity.opportunity import OpportunityLanguage

import formatters as fmt
class QueryParams(BaseQueryParams):
    model_config = {
        'extra': 'ignore',
    }
    lang: Language

class QueryParamsByID(BaseQueryParams):
    model_config = {'extra': 'ignore'}

    id: ID

class DBError(IntEnum):
    INVALID_LANGUAGE_ID = 200

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_LANGUAGE_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Language with provided ID doesn\'t exist',
                    ru='Языка с таким идентификатором не существует',
                ),
                path=['body', 'language', 'id']
            ),
        }
    )
)


@app.get('/{language}/opportunity')
async def get(language: Language, query: Annotated[QueryParamsByID, Query()]) -> JSONResponse:
    formatted_errors = fmt.ErrorTrace()
    if (instance := OpportunityLanguage.objects.get(id=query.id)) is not None:
        return JSONResponse(instance, status_code=200)
    appender(formatted_errors, DBError.INVALID_LANGUAGE_ID, language)
    return JSONResponse(formatted_errors.to_underlying())

@app.get('/opportunity-language')
async def get_all(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    languages = OpportunityLanguage.get_all()
    return languages

# @app.get('/opportunity-language')
async def get_mock(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    response = choice(
        None, 
        JSONResponse({}, status_code=401),
        JSONResponse({}, status_code=500),
    )
    if response is None:
        return response
    return JSONResponse(
        ['English', 'Russian', 'Spanish', 'French'],
        status_code=200,
    )