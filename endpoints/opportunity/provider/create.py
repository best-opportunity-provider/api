# TODO:
#   1. POST /private/opportunity-provider?api_key={}
from typing import Annotated

from fastapi import Query, Body
from fastapi.responses import JSONResponse

import pydantic

from database.models.file import File
from database.models.opportunity import opportunity
from database.models.trans_string.embedded import ContainedTransString

from ...base import (
    app,
    BaseQueryParams,
)
from database.models.trans_string import Language
from database.models.geo import (
    Country,
    City,
)

class BodyParams(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    name: ContainedTransString
    # logo: File // TODO: файлик разве не соло в бодике?


@app.post('private/opportunity-provider')
async def create(body: Annotated[BodyParams, Body()], query: Annotated[BaseQueryParams, Query()]
) -> JSONResponse:
    instance = opportunity.OpportunityProvider.create(body.name)
    return JSONResponse({'id': instance.id})