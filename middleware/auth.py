from typing import (
    Annotated,
    Literal,
)

from fastapi import (
    Path,
    Query,
    Depends,
)

from .base import APIKey as APIKeyModel
from database import (
    APIKey,
    PersonalAPIKey,
    DeveloperAPIKey,
)
from database.models.user import UserTier
import formatters as fmt


get_api_key_error_appender = fmt.enum.ErrorAppender[APIKey.GetErrorCode | Literal['invalid_tier']](
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
            'invalid_tier': fmt.enum.Error(
                type=202,
                message=fmt.TranslatedString(
                    en="User with provided API key can't access this method",
                    ru='Пользователь с этим API-ключем не может получить доступ к этому методу',
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
        error = get_api_key_error_appender(errors, key_or_error, language=language)
        match error['type']:
            case 201:
                errors.error_code = 403
            case _:
                errors.error_code = 422
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


class GetPersonalAPIKeyWithTier:
    def __init__(self, tier: UserTier):
        self.tier = tier

    async def __call__(
        self,
        language: Annotated[fmt.Language, Path()],
        api_key: Annotated[PersonalAPIKey | fmt.ErrorTrace, Depends(get_personal_api_key)],
    ) -> PersonalAPIKey | fmt.ErrorTrace:
        if isinstance(api_key, fmt.ErrorTrace):
            return api_key
        if api_key.user.fetch().tier < self.tier:
            errors = fmt.ErrorTrace()
            get_api_key_error_appender(errors, 'invalid_tier', language=language)
            errors.error_code = 403
            return errors
        return api_key
