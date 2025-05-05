from .base import get_response_data
from database import (
    OpportunityForm,
    OpportunityFormResponse,
)


def yandex_forms_submit_handler(
    response: OpportunityFormResponse,
    form: OpportunityForm,
) -> None:
    values, tempdir = get_response_data(response, form)
    data = {
        'link': form.submit_method.url,
        'values': values,
    }
    # call submitter with `data`
