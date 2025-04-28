# ===== Logging config =====

import logging
import os
from datetime import datetime

LOGS_FOLDER = f'logs/{datetime.now().strftime("%Y.%m.%d")}'
LOG_NAME = datetime.now().strftime('%H-%M-%S')

os.makedirs(LOGS_FOLDER, exist_ok=True)
logging.basicConfig(
    filename=f'{LOGS_FOLDER}/{LOG_NAME}.log',
    format='[%(levelname)s @ %(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG,
)

logger = logging.getLogger()

# ===== App config =====

HOST: str = '127.0.0.1'
PORT: int = 8001

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ===== Database config =====

from database import config as dbcfg  # noqa: E402


def connect_mongo_db(
    user: str, password: str, host: str, port: int, db_name: str, auth_db_name: str
) -> None:
    import mongoengine as mongo

    mongo.connect(
        host=f'mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource={auth_db_name}'
    )


connect_mongo_db(
    user=dbcfg.MONGO_USERNAME,
    password=dbcfg.MONGO_PASSWORD,
    host=dbcfg.MONGO_HOST,
    port=dbcfg.MONGO_PORT,
    db_name=dbcfg.MONGO_DB_NAME,
    auth_db_name=dbcfg.MONGO_AUTH_DB_NAME,
)


import minio  # noqa: E402


def get_minio_client(access_key: str, secret_key: str, host: str, port: int) -> minio.Minio:
    return None


minio_client = get_minio_client(
    access_key=dbcfg.MINIO_ACCESS_KEY,
    secret_key=dbcfg.MINIO_SECRET_KEY,
    host=dbcfg.MINIO_HOST,
    port=dbcfg.MINIO_PORT,
)
