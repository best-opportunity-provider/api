from typing import Literal

from database import Opportunity

from ..base import ObjectId
import formatters as fmt


type ErrorCode = Literal['doesnt_exist', 'not_free']
type ErrorCodeMapping = dict[ErrorCode, int]


def doesnt_exist_error_fn(
    *, error_code_mapping: ErrorCodeMapping, path: list[str], **kwargs
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping['doesnt_exist'],
        message=fmt.TranslatedString(
            en="Opportunity with provided id doesn't exist",
            ru='Возможности с таким идентификатором не существует',
        ),
        path=path,
    )


def not_free_error_fn(
    *, error_code_mapping: ErrorCodeMapping, path: list[str], **kwargs
) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=error_code_mapping['not_free'],
        message=fmt.TranslatedString(
            en="Free users can't access opportunity with provided id",
            ru='Бесплатные пользователи не имеют доступа к возможности с этим идентификатором',
        ),
        path=path,
    )


error_appender = fmt.enum.ErrorAppender[ErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            'doesnt_exist': doesnt_exist_error_fn,
            'not_free': not_free_error_fn,
        }
    ),
)


def get_opportunity_by_id(
    id: ObjectId,
    *,
    language: fmt.Language,
    error_code_mapping: ErrorCodeMapping,
    path: list[str],
    free: bool = False,
) -> Opportunity | fmt.ErrorTrace:
    opportunity: Opportunity | None = Opportunity.objects.with_id(id)
    if opportunity is None:
        error = fmt.ErrorTrace()
        error_appender(
            error,
            'doesnt_exist',
            language=language,
            error_code_mapping=error_code_mapping,
            path=path,
        )
        return error
    if free and not opportunity.is_free:
        error = fmt.ErrorTrace()
        error_appender(
            error,
            'not_free',
            language=language,
            error_code_mapping=error_code_mapping,
            path=path,
        )
        return error
    return opportunity
