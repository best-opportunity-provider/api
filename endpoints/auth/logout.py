from fastapi.responses import JSONResponse
from random import choice

from ..base import app


@app.post('/logout')
async def logout_mock() -> JSONResponse:
    return JSONResponse({}, status_code=choice([200, 500]))
