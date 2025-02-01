from ..base import *


@app.post('/api/register')
async def register_mock() -> JSONResponse:
    return choice([
        JSONResponse({
            'email': 'Not a valid email address',
            'username': 'Username can contain characters lowercase letters, uppercase letters and digits',
            'password': 'Password must contain at least one lowercase letter, ' \
                        'one uppercase letter, one digit and one special character',
        }, status_code=422),
        JSONResponse({
            'email': 'Account with provided email already exists',
            'username': 'Account with provided username already exists',
        }, status_code=422),
        JSONResponse({}, status_code=200),
        JSONResponse({}, status_code=500),
    ])
