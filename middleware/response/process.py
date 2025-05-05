from database import (
    OpportunityForm,
    OpportunityFormResponse,
)
from database.models.opportunity.form import (
    YandexFormsSubmitMethod,
)
from submitters import (
    yandex_forms_submit_handler,
)

HANDLERS = {
    YandexFormsSubmitMethod: yandex_forms_submit_handler,
}


def process_opportunity_form_response(
    response: OpportunityFormResponse,
    form: OpportunityForm,
) -> None:
    response.state = OpportunityFormResponse.State.ERROR
    response.save()
    HANDLERS[type(form.submit_method)](response, form)
    response.state = OpportunityFormResponse.State.PROCESSED
    response.save()
