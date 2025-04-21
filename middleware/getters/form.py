from database import OpportunityForm

from ..base import ObjectId
import formatters as fmt


def error_fn(*, transformed_error_code: int, path: list[str], **kwargs) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=transformed_error_code,
        message=fmt.TranslatedString(
            en="Provided opportunity doesn't have a submit form",
            ru='Для этой возможности нет формы подачи',
        ),
        path=path,
    )


error_appender = fmt.enum.ErrorAppender[None](
    transformer=fmt.enum.transformers.SingleErrorTransformer(error_fn),
)


def get_opportunity_form_by_id(
    opportunity_id: ObjectId,
    *,
    language: fmt.Language,
    error_code: int,
    path: list[str],
) -> OpportunityForm | fmt.ErrorTrace:
    """Error message assumes, that opportunity with same id exists and was checked before."""

    form: OpportunityForm | None = OpportunityForm.objects.with_id(opportunity_id)
    if form is None:
        error = fmt.ErrorTrace()
        error_appender(
            error,
            None,
            language=language,
            transformed_error_code=error_code,
            path=path,
        )
        return error
    return form
