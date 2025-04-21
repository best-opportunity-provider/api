from .. import getters
from database import OpportunityForm
from database.models.opportunity.form import (
    UpdateOpportunityFormModel,
    CreateFieldErrorCode,
)
import formatters as fmt


type ErrorCodeMapping = dict[CreateFieldErrorCode, int]


def handle_phone_number_invalid_country_id(
    *,
    error_code_mapping: ErrorCodeMapping,
    context: tuple[str, int],
    model_path: list[str],
    **kwargs,
) -> fmt.enum.Error:
    return getters.country.error_fn(
        transformed_error_code=error_code_mapping[
            CreateFieldErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID
        ],
        path=[*model_path, 'fields', context[0], 'whitelist', str(context[1])],
    )


error_appender = fmt.enum.ErrorAppender[CreateFieldErrorCode](
    transformer=fmt.enum.transformers.DictErrorTransformer(
        {
            CreateFieldErrorCode.PHONE_NUMBER_INVALID_COUNTRY_ID: handle_phone_number_invalid_country_id,
        }
    )
)


def update_opportunity_form(
    form: OpportunityForm,
    update_model: UpdateOpportunityFormModel,
    *,
    language: fmt.Language,
    error_code_mapping: ErrorCodeMapping,
    model_path: list[str],
) -> None | fmt.ErrorTrace:
    raw_errors = form.update(update_model)
    if raw_errors is None:
        return
    formatted_errors = fmt.ErrorTrace()
    for raw_error in raw_errors:
        error_appender(
            formatted_errors,
            raw_error.error_code,
            context=raw_error.context,
            language=language,
            error_code_mapping=error_code_mapping,
            model_path=model_path,
        )
    return formatted_errors
