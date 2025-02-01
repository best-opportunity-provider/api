from ..base import *


@app.post('/api/login')
async def login_mock() -> JSONResponse:
    response = choice([
        None,
        JSONResponse({}, status_code=401),
        JSONResponse({}, status_code=500),
    ])
    if response is not None:
        return response
    return JSONResponse({
        'api_key': 'dev-b99834e241f308f19623478b8d40c764cec7f0bd248bb3a5c8e6737ec4bada0b',
    }, status_code=200)
