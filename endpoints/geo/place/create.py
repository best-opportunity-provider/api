from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse

from ...base import (
    app,
    BaseQueryParams,
)
from database.models.geo import (
    Place,
    PlaceModel,
)
from formatters import Language


@app.post('/{language}/private/place')
async def create(
    language: Language,
    body: Annotated[PlaceModel, Body()],
    query: Annotated[BaseQueryParams, Query()],
) -> JSONResponse:
    # TODO: retrieve actual `Country`/`City` instances from body and use them to create `Place`
    ...
    # INVALID:
    # instance = Place.create(body.name, body.language, body.location)
    # return JSONResponse({'id': instance.id})
