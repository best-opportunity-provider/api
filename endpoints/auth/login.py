from typing import Annotated, Optional
from datetime import (
    UTC,
    datetime,
    timedelta,
)

from fastapi import Body, Request
from fastapi.responses import JSONResponse

from database.models.api import PersonalAPIKey
from database.models.user import (
    User,
    LoginModel,
)
from ..base import app


class BodyModel(LoginModel):
    remember_me: bool = False


@app.post('/login')
async def login(request: Request, body: Annotated[BodyModel, Body()]) -> JSONResponse:
    user: Optional['User'] = User.login(body)
    if user is None:
        return JSONResponse({}, status_code=401)
    api_key = PersonalAPIKey.generate(
        user,
        request.client.host,
        datetime.now(UTC) + (timedelta(days=365) if body.remember_me else timedelta(hours=2)),
    )
    return JSONResponse({'api_key': str(api_key)})
