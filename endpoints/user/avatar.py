# TODO:
#   1. GET /user/avatar?id={username}&api_key={}
#   2. PUT /user/avatar?api_key={}

from typing import Annotated
from random import choice

from fastapi import Query
from fastapi.responses import (
    JSONResponse,
    Response,
)
import pydantic

from ..base import (
    app,
    APIKey,
)

from database.models.user import USERNAME_REGEX

type Username = Annotated[str, pydantic.Field(pattern=USERNAME_REGEX)]


class QueryParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    username: Username
    api_key: APIKey


@app.get('/user/avatar')
async def get_mock(query: Annotated[QueryParams, Query()]) -> Response:
    return choice(
        [
            Response(status_code=401),
            Response(status_code=500),
        ]
    )
