from ..base import *


@app.post('/api/logout')
async def logout_mock() -> JSONResponse:
    return JSONResponse({}, status_code=choice([200, 500]))
