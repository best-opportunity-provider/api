from typing import Annotated
from fastapi import Query
from fastapi.responses import JSONResponse
from random import choice

from database.models.api import PersonalAPIKey

from ..base import BaseQueryParams, app


@app.post('/logout')
async def logout(query: Annotated[BaseQueryParams, Query()]) -> JSONResponse:
    PersonalAPIKey.get(query.api_key).expire()
    return JSONResponse({})


async def logout_mock() -> JSONResponse:
    return JSONResponse({}, status_code=choice([200, 500]))
