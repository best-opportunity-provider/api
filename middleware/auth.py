from typing import Annotated

from fastapi import (
    Path,
    Query,
)

from .base import APIKey as APIKeyModel
from database import (
    APIKey,
    PersonalAPIKey,
    DeveloperAPIKey,
)
import formatters as fmt


get_api_key_error_appender = fmt.enum.ErrorAppender[APIKey.GetErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            APIKey.GetErrorCode.INVALID_CATEGORY: fmt.enum.Error(
                type=200,
                message=fmt.TranslatedString(
                    en='API keys of this category are not allowed for this method',
                    ru='API-ключи этой категории не могут использоваться в этом методе',
                ),
                path=['query', 'api_key'],
            ),
            APIKey.GetErrorCode.INVALID_KEY: fmt.enum.Error(
                type=201,
                message=fmt.TranslatedString(
                    en='Provided API key is invalid',
                    ru='Предоставленный API-ключ недействителен',
                ),
                path=['query', 'api_key'],
            ),
        }
    )
)


async def get_personal_api_key(
    language: Annotated[fmt.Language, Path()],
    api_key: Annotated[APIKeyModel, Query()],
) -> PersonalAPIKey | fmt.ErrorTrace:
    key_or_error = APIKey.get(api_key, allowed_categories=[APIKey.Category.PERSONAL])
    if isinstance(key_or_error, APIKey.GetErrorCode):
        errors = fmt.ErrorTrace()
        get_api_key_error_appender(errors, key_or_error, language=language)
        return errors
    return key_or_error


async def get_developer_api_key(
    language: Annotated[fmt.Language, Path()],
    api_key: Annotated[APIKeyModel, Query()],
) -> DeveloperAPIKey | fmt.ErrorTrace:
    key_or_error = APIKey.get(api_key, allowed_categories=[APIKey.Category.DEVELOPER])
    if isinstance(key_or_error, APIKey.GetErrorCode):
        errors = fmt.ErrorTrace()
        get_api_key_error_appender(errors, key_or_error, language=language)
        return errors
    return key_or_error
