from database import OpportunityLanguage

from ..base import ObjectId
import formatters as fmt


def error_fn(*, transformed_error_code: int, path: list[str], **kwargs) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=transformed_error_code,
        message=fmt.TranslatedString(
            en='Language with provided ID doesn\'t exist',
            ru='Языка с таким идентификатором не существует',
        ),
        path=path,
    )


error_appender = fmt.enum.ErrorAppender[None](
    transformer=fmt.enum.transformers.SingleErrorTransformer(error_fn),
)


def get_language_by_id(
    id: ObjectId,
    *,
    language: fmt.Language,
    error_code: int,
    path: list[str],
) -> OpportunityLanguage | fmt.ErrorTrace:
    lang: OpportunityLanguage | None = OpportunityLanguage.objects.with_id(id)
    if lang is None:
        error = fmt.ErrorTrace()
        error_appender(
            error,
            None,
            language=language,
            transformed_error_code=error_code,
            path=path,
        )
        return error
    return lang
