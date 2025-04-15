from typing import Any

from pydantic import ValidationError

from database import (
    OpportunityForm,
    OpportunityFormResponse,
    User,
)
from database.models.opportunity.form import PostValidationErrorCode
import formatters as fmt
from .. import getters
from .create_model import create_opportunity_form_response_model
from .create_formatter import create_opportunity_form_response_formatter


type ErrorCodeMapping = dict[PostValidationErrorCode, int]


def handle_phone_number_invalid_country_id(
    *, error_code_mapping: ErrorCodeMapping, context: str, data_path: list[str], **kwargs
) -> fmt.enum.Error:
    return getters.country.error_fn(
        transformed_error_code=error_code_mapping[
            PostValidationErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID
        ],
        path=[*data_path, context, 'country_id'],
    )


def handle_phone_number_non_whitelist_country(
    *,
    error_code_mapping: ErrorCodeMapping,
    context: str,
    data_path: list[str],
    **kwargs,
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping[PostValidationErrorCode.PHONE_NUMBER_NON_WHITELIST_COUNTRY],
        message=fmt.TranslatedString(
            en='Phone numbers from this country are not allowed',
            ru='Номера телефонов из этой страны не разрешены',
        ),
        path=[*data_path, context, 'country_id'],
    )


def handle_invalid_choice(
    *,
    error_code_mapping: ErrorCodeMapping,
    context: str,
    data_path: list[str],
    **kwargs,
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping[PostValidationErrorCode.INVALID_CHOICE],
        message=fmt.TranslatedString(
            en='Provided choice is not valid',
            ru='Предоставленный вариант не валиден',
        ),
        path=[*data_path, context],
    )


def handle_file_invalid_id(
    *,
    error_code_mapping: ErrorCodeMapping,
    context: str,
    data_path: list[str],
    **kwargs,
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping[PostValidationErrorCode.FILE_INVALID_ID],
        message=fmt.TranslatedString(
            en="File with provided id doesn't exist",
            ru='Файла с таким идентификатором не существует',
        ),
        path=[*data_path, context],
    )


def handle_file_cant_access(
    *,
    error_code_mapping: ErrorCodeMapping,
    context: str,
    data_path: list[str],
    **kwargs,
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping[PostValidationErrorCode.FILE_CANT_ACCESS],
        message=fmt.TranslatedString(
            en="Can't access file with provided id",
            ru='Невозможно получить доступ к файлу с предоставленным идентификатором',
        ),
        path=[*data_path, context],
    )


def handle_file_exceeds_size(
    *,
    error_code_mapping: ErrorCodeMapping,
    context: str,
    data_path: list[str],
    **kwargs,
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping[PostValidationErrorCode.FILE_EXCEEDS_SIZE],
        message=fmt.TranslatedString(
            en='File with provided id exceeds maximum allowed size',
            ru='Файл с предосталенным идентификатором превышает ограничения по размеру',
        ),
        path=[*data_path, context],
    )


post_validation_error_appender = fmt.enum.ErrorAppender[PostValidationErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            PostValidationErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID: (
                handle_phone_number_invalid_country_id
            ),
            PostValidationErrorCode.PHONE_NUMBER_NON_WHITELIST_COUNTRY: (
                handle_phone_number_non_whitelist_country
            ),
            PostValidationErrorCode.INVALID_CHOICE: handle_invalid_choice,
            PostValidationErrorCode.FILE_INVALID_ID: handle_file_invalid_id,
            PostValidationErrorCode.FILE_CANT_ACCESS: handle_file_cant_access,
            PostValidationErrorCode.FILE_EXCEEDS_SIZE: handle_file_exceeds_size,
        }
    )
)


def create_opportunity_form_response(
    form: OpportunityForm,
    user: User,
    data: dict[str, Any],
    *,
    language: fmt.Language,
    error_code_mapping: ErrorCodeMapping,
    data_path: list[str],
) -> OpportunityFormResponse | fmt.ErrorTrace:
    pydantic_model = create_opportunity_form_response_model(form)
    try:
        pydantic_model.model_validate(data)
    except ValidationError as e:
        error_appender = create_opportunity_form_response_formatter(form)
        errors = fmt.ErrorTrace()
        for error in e.errors():
            error_appender(errors, error['type'], error['loc'], language=language)
        return errors
    response = OpportunityFormResponse.create(user, form, data)
    if isinstance(response, OpportunityFormResponse):
        return response
    errors = fmt.ErrorTrace()
    for raw_error in response:
        post_validation_error_appender(
            errors,
            raw_error.error_code,
            context=raw_error.context,
            language=language,
            error_code_mapping=error_code_mapping,
            data_path=data_path,
        )
    return errors
