# TODO:
#   1. PATCH /private/opportunity?id={}&api_key={}

from typing import (
    Annotated,
    Self,
    Literal,
    Any
)
from random import choice
from enum import IntEnum

from fastapi import Query, Body, Depends
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
import middleware
from ...base import (
    app,
    ObjectId,
)


class ErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 202


appender = fmt.enum.ErrorAppender[ErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            ErrorCode.INVALID_OPPORTUNITY_ID: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='Opportunity industry with provided ID doesn\'t exist',
                    ru='Возможности с таким идентификатором не существует',
                ),
                path=['body', 'industry', 'id']
            ),
        }
    )
)


@app.patch("/{language}/private/opportunity")
async def patch(
    language: Language,
    opportunity_id: Annotated[ObjectId, Query()],
    body: Annotated[opportunity.UpdateOpportunityModel, Body()],
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
