from typing import Annotated
from fastapi import Query
from fastapi.responses import JSONResponse
from random import choice

from database.models.api import PersonalAPIKey

from ..base import app


@app.post('/logout')
async def logout(
    api_key: Annotated[Any | ErrorTrace, Depends(middleware.auth.get_personal_api_key)],
) -> JSONResponse:
    if isinstance(api_key, ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    PersonalAPIKey.get(api_key).expire()
    return JSONResponse({})


async def logout_mock() -> JSONResponse:
    return JSONResponse({}, status_code=choice([200, 500]))
