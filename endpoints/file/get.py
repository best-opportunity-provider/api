from typing import (
    Annotated,
    Literal,
)
from enum import IntEnum

from fastapi import (
    Query,
    Depends,
)
from fastapi.responses import (
    Response,
    JSONResponse,
)

from ..base import (
    app,
    minio_client,
    ObjectId,
)
from database import (
    PersonalAPIKey,
)
import formatters as fmt
import middleware


class ErrorCode(IntEnum):
    INVALID_FILE_ID = 203
    CANT_ACCESS_FILE = 204


error_appender = fmt.enum.ErrorAppender[Literal['cant_access']](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            'cant_access': fmt.enum.Error(
                type=ErrorCode.CANT_ACCESS_FILE.value,
                message=fmt.TranslatedString(
                    en="Can't access file with specified id",
                    ru='Невозможно получить доступ к файлу с этим идентификатором',
                ),
                path=['query', 'id'],
            ),
        }
    )
)


extension_to_media_type = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
}


@app.get('/{language}/file')
async def get_file(
    language: fmt.Language,
    id: Annotated[ObjectId, Query()],
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> Response:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=api_key.error_code)
    file = middleware.getters.get_file_by_id(
        id,
        language=language,
        error_code=ErrorCode.INVALID_FILE_ID.value,
        path=['query', 'id'],
    )
    if isinstance(file, fmt.ErrorTrace):
        return JSONResponse(file.to_underlying(), status_code=422)
    if not file.can_access(api_key.user.id):
        errors = fmt.ErrorTrace()
        error_appender(errors, 'cant_access', language=language)
        return JSONResponse(errors.to_underlying(), status_code=403)
    return Response(
        file.download(minio_client),
        media_type=extension_to_media_type[file.extension.split('.')[-1]],
    )
