from typing import Annotated

from fastapi import Query, Body, Depends
from fastapi.responses import JSONResponse

import pydantic

from ...base import (
    app,
)
from database import DeveloperAPIKey
from database.models.trans_string import Language
from database.models.geo import (
    Place,
    PlaceModel,
)

import formatters as fmt
import middleware


@app.post('/{language}/private/place')
async def create_place(
    language: Language,
    body: Annotated[PlaceModel, Body()],
    api_key: Annotated[DeveloperAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_developer_api_key)],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=403)
    instance = Place.create(name=body.name, location=body.location)
    return JSONResponse({'id': str(instance.id)})
