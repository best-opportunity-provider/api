from database import OpportunityIndustry

from ..base import ObjectId
import formatters as fmt


def error_fn(*, transformed_error_code: int, path: list[str], **kwargs) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=transformed_error_code,
        message=fmt.TranslatedString(
            en='Indsutry with provided ID doesn\'t exist',
            ru='Индустрии с таким идентификатором не существует',
        ),
        path=path,
    )


error_appender = fmt.enum.ErrorAppender[None](
    transformer=fmt.enum.transformers.SingleErrorTransformer(error_fn),
)


def get_industry_by_id(
    id: ObjectId,
    *,
    language: fmt.Language,
    error_code: int,
    path: list[str],
) -> OpportunityIndustry | fmt.ErrorTrace:
    industry: OpportunityIndustry | None = OpportunityIndustry.objects.with_id(id)
    if industry is None:
        error = fmt.ErrorTrace()
        error_appender(
            error,
            None,
            language=language,
            transformed_error_code=error_code,
            path=path,
        )
        return error
    return industry
