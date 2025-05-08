from typing import Annotated

from fastapi import (
    Depends,
)
from fastapi.responses import JSONResponse

from ..base import app
from database import (
    PersonalAPIKey,
    User,
)
import formatters as fmt
import middleware


@app.get('/{language}/user')
async def get_user(
    language: fmt.Language,
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=api_key.error_code)
    user: User = api_key.user.fetch()
    return JSONResponse(user.to_dict())
