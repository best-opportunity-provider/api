from enum import IntEnum
from typing import Annotated
from fastapi import Body
from fastapi.responses import JSONResponse
from random import choice

import pydantic

from database.models.user import User
from formatters.base import Language

from ..base import app
from ...database.models.utils import Error

import formatters as fmt


class DBError(IntEnum):
    NOT_UNIQUE_USERNAME = 200


appender = fmt.enum.ErrorAppender[DBError](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            DBError.NOT_UNIQUE_USERNAME: fmt.enum.Error(
                type=fmt.enum.infer,
                message=fmt.TranslatedString(
                    en='User with provided name is already exist',
                    ru='Пользователь с таким юзернеймом уже существует',
                ),
                path=['body', 'username'],
            ),
        }
    )
)


@app.post('/{language}/register')
async def register(language: Language, body: Annotated[User.CreateModel, Body()]) -> JSONResponse:
    instance: User | Error[User.CreateErrorCode] = User.create(body)
    formatted_errors = fmt.ErrorTrace()
    if isinstance(instance, Error[User.CreateErrorCode]):
        appender(formatted_errors, DBError.NOT_UNIQUE_USERNAME, language)
        return JSONResponse(formatted_errors.to_underlying())
    return JSONResponse(instance.id, status_code=200)


# @app.post('/register')
async def register_mock() -> JSONResponse:
    return choice(
        [
            JSONResponse(
                {
                    'email': 'Not a valid email address',
                    'username': 'Username can contain characters lowercase letters, uppercase letters and digits',
                    'password': 'Password must contain at least one lowercase letter, '
                    'one uppercase letter, one digit and one special character',
                },
                status_code=422,
            ),
            JSONResponse(
                {
                    'email': 'Account with provided email already exists',
                    'username': 'Account with provided username already exists',
                },
                status_code=422,
            ),
            JSONResponse({}, status_code=200),
            JSONResponse({}, status_code=500),
        ]
    )
