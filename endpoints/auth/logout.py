from typing import Annotated

from fastapi import Depends
from fastapi.responses import JSONResponse

from ..base import app
from database import PersonalAPIKey
import formatters as fmt
import middleware


@app.post('/logout')
async def logout(
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key, status_code=api_key.error_code)
    api_key.expire()
    return JSONResponse({})
