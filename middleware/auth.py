from typing import Annotated
from enum import IntEnum

from fastapi import (
    Path,
    Query,
)

from .base import APIKey as APIKeyModel
from database import (
    APIKey,
    PersonalAPIKey,
)
import formatters as fmt


class GetAPIKeyError(IntEnum):
    INVALID_API_KEY = 0
    INVALID_KEY_TYPE = 1


ERRORS = {
    'invalid_key': fmt.enum.Error(
        type=200,
        message=fmt.TranslatedString(
            en='Provided API key is invalid',
            ru='Предоставленный API-ключ недействителен',
        ),
        path=['query', 'api_key'],
    ),
    'invalid_key_type_personal': fmt.enum.Error(
        type=201,
        message=fmt.TranslatedString(
            en='Provided API key must be personal',
            ru='Предоставленный API-ключ должен быть персональным',
        ),
        path=['query', 'api_key'],
    ),
}

get_personal_api_key_error_appender = fmt.enum.ErrorAppender[GetAPIKeyError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            GetAPIKeyError.INVALID_API_KEY: ERRORS['invalid_key'],
            GetAPIKeyError.INVALID_KEY_TYPE: ERRORS['invalid_key_type_personal'],
        }
    )
)


async def get_personal_api_key(
    language: Annotated[fmt.Language, Path()],
    api_key: Annotated[APIKeyModel, Query()],
) -> PersonalAPIKey | fmt.ErrorTrace:
    if (key := APIKey.get(api_key)) is not None:
        if isinstance(key, PersonalAPIKey):
            return key
        errors = fmt.ErrorTrace()
        get_personal_api_key_error_appender(
            errors, GetAPIKeyError.INVALID_KEY_TYPE, language=language
        )
        return errors
    errors = fmt.ErrorTrace()
    get_personal_api_key_error_appender(errors, GetAPIKeyError.INVALID_API_KEY, language=language)
    return errors
