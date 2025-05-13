from typing import (
    Annotated,
)

from fastapi import (
    Form,
    UploadFile,
    Depends,
)
from fastapi.responses import JSONResponse

from ..base import (
    app,
    minio_client,
)
from database import (
    PersonalAPIKey,
    UserInfo,
    File,
)
import formatters as fmt
import middleware


class FormModel(UserInfo.UpdateModel):
    cv: UploadFile


@app.post('/{language}/user/info')
async def update(
    language: fmt.Language,
    form: Annotated[FormModel, Form()],
    api_key: Annotated[
        PersonalAPIKey | fmt.ErrorTrace, Depends(middleware.auth.get_personal_api_key)
    ],
) -> JSONResponse:
    if isinstance(api_key, fmt.ErrorTrace):
        return JSONResponse(api_key.to_underlying(), status_code=api_key.error_code)
    cv = File.create(
        minio_client,
        form.cv.file,
        form.cv.filename.rsplit('.', maxsplit=1)[-1],
        bucket=File.Bucket.USER_CV,
        size_bytes=form.cv.size,
        owner_id=api_key.user.id,
    )
    assert isinstance(cv, File)
    user_info: UserInfo | None = UserInfo.objects.with_id(api_key.user.id)
    assert user_info is not None
    if user_info.cv is not None:
        user_info.cv.fetch().mark_for_deletion()
    user_info.cv = cv
    user_info.update(form)
    user_info.save()
    return JSONResponse({})
