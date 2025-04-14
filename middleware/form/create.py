from .update import ErrorCodeMapping, error_appender
from database import (
    Opportunity,
    OpportunityForm,
)
from database.models.opportunity.form import OpportunityFormModel
from formatters import (
    Language,
    ErrorTrace,
)


def create_opportunity_form(
    opportunity: Opportunity,
    create_model: OpportunityFormModel,
    *,
    language: Language,
    error_code_mapping: ErrorCodeMapping,
    model_path: list[str],
) -> OpportunityForm | ErrorTrace:
    form = OpportunityForm.create(opportunity, create_model)
    if isinstance(form, OpportunityForm):
        return form
    formatted_errors = ErrorTrace()
    for raw_error in form:
        error_appender(
            formatted_errors,
            raw_error.error_code,
            context=raw_error.context,
            language=language,
            error_code_mapping=error_code_mapping,
            model_path=model_path,
        )
    return formatted_errors
