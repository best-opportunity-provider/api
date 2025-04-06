from typing import Annotated
from fastapi import Body
from fastapi.responses import JSONResponse

from database.models.user import (
    User,
    CreateModel,
)
from ..base import app
from database.models.utils import Error
from formatters.base import Language
import formatters as fmt


appender = fmt.enum.ErrorAppender[User.CreateErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            User.CreateErrorCode.NON_UNIQUE_USERNAME: fmt.enum.Error(
                type=200,
                message=fmt.TranslatedString(
                    en='User with provided name is already exist',
                    ru='Пользователь с таким именем уже существует',
                ),
                path=['body', 'username'],
            ),
        }
    )
)


@app.post('/{language}/register')
async def register(language: Language, body: Annotated[CreateModel, Body()]) -> JSONResponse:
    instance = User.create(body)
    if isinstance(instance, Error):
        formatted_errors = fmt.ErrorTrace()
        appender(formatted_errors, instance, language)
        return JSONResponse(formatted_errors.to_underlying(), status_code=403)
    return JSONResponse(instance.id, status_code=200)
