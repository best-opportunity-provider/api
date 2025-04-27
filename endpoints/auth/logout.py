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
    api_key.expire()
    return JSONResponse({})
