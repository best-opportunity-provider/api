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
from database.models.trans_string.embedded import ContainedTransString, ContainedTransStringModel, TransString

import formatters as fmt
from ...base import (
    app,
    ObjectId,
)


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202


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

class OpportunityUpdateBodyParams(pydantic.BaseModel):
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
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[OpportunityUpdateBodyParams, Body()],
    api_key: Annotated[Any | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)

    opportunity = middleware.getters.get_opportunity_by_id(
        opportunity_id,
        language=language,
        error_code=ErrorCode.INVALID_OPPORTUNITY_ID.value,
        path=['query', 'opportunity_id'],
    )
    if isinstance(opportunity, fmt.ErrorTrace):
        return JSONResponse(opportunity.to_underlying(), status_code=422)

    raw_errors = opportunity.update(body)
    if raw_errors is None:
        return JSONResponse({})
    return JSONResponse(errors.to_underlying(), status_code=422)

    # formatted_errors = fmt.ErrorTrace()
    # for raw_error in raw_errors:
    #     error_appender(
    #         formatted_errors,
    #         raw_error.error_code,
    #         context=raw_error.context,
    #         language=language,
    #         error_code_mapping=error_code_mapping,
    #         model_path=model_path,
    #     )
    # return formatted_errors

    # errors = middleware.form.update_opportunity_form(
    #     form,
    #     body,
    #     language=language,
    #     error_code_mapping={
    #         CreateFieldErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID: (
    #             ErrorCode.PHONE_NUMBER_FIELD_INVALID_COUNTRY_ID.value
    #         ),
    #     },

    #     model_path=['body'],
    # )
