from enum import IntEnum
from typing import Annotated
from random import choice

from fastapi import Query
from fastapi.responses import JSONResponse
import pydantic

from ...base import (
    ID,
    BaseQueryParams,
    app,
    APIKey,
)
from database.models.trans_string import Language
from database.models.opportunity.opportunity import Opportunity

import formatters as fmt



class QueryParams(pydantic.BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: APIKey
    lang: Language

class QueryParamsByID(BaseQueryParams):
    model_config = {'extra': 'ignore'}

    id: ID

class DBError(IntEnum):
    INVALID_OPPORTUNITY_ID = 200

appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.INVALID_COUNTRY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Opportunity with provided ID doesn\'t exist',
                    ru='Вакансии с таким идентификатором не существует',
                ),
                path=['body', 'opportunity', 'id']
            ),
        }
    )
)


@app.get('/{language}/opportunity')
async def get(language: Language, query: Annotated[QueryParamsByID, Query()]) -> JSONResponse:
    formatted_errors = fmt.ErrorTrace()
    if (instance := Opportunity.objects.get(id=query.id)) is not None:
        return JSONResponse(instance, status_code=200)
    appender(formatted_errors, DBError.INVALID_OPPORTUNITY_ID, language)
    return JSONResponse(formatted_errors.to_underlying())
    

@app.get('/opportunity')
async def get_all(query: Annotated[QueryParams, Query()]) -> JSONResponse:
    industries = Opportunity.get_all()
    return industries