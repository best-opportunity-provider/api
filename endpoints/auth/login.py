from typing import Annotated, Optional
from fastapi import Body, Request
from fastapi.responses import JSONResponse
from random import choice

from database.models.api import PersonalAPIKey
from database.models.user import User
from formatters.base import Language

from ..base import app

@app.post('/login')
async def login(request: Request, body: Annotated[User.LoginModel, Body()]) -> JSONResponse:
    user: Optional['User'] = User.login(body)
    if user is None:
        return JSONResponse({})
    PersonalAPIKey.generate(user, request.client.host)
    return JSONResponse(user.id, status_code=200)


async def login_mock() -> JSONResponse:
    response = choice(
        [
            None,
            JSONResponse({}, status_code=401),
            JSONResponse({}, status_code=500),
        ]
    )
    if response is not None:
        return response
    return JSONResponse(
        {
            'api_key': 'dev-b99834e241f308f19623478b8d40c764cec7f0bd248bb3a5c8e6737ec4bada0b',
        },
        status_code=200,
    )
