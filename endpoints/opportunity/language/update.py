# TODO:
#   1. PATCH /private/opportunity-language?id={}&api_key={}

from typing import (
    Annotated,
    Self,
    Literal,
)
from random import choice
from enum import IntEnum

from fastapi import Query, Body
from fastapi.responses import JSONResponse, Response
import pydantic
from pydantic_core import PydanticCustomError

from database.models.opportunity import opportunity
from database.models.trans_string import Language
from database.models import geo

from database.models.geo import (
    Country,
    City,
)
from database.models.trans_string.embedded import ContainedTransString

import formatters as fmt
from ...base import (
    app,
    ID,
    BaseQueryParams,
)

...