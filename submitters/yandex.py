import time

from .base import (
    ResponseData,
    get_response_data,
)
from .config import (
    driver,
    By,
)
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
    run_submitter(data)


def run_submitter(data: ResponseData) -> None:
    driver.get(data['link'])
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(data['values']['cv'])
    time.sleep(0.5)
    driver.find_element(By.ID, 'answer_param_name').send_keys(data['values']['firstname'])
    time.sleep(0.5)
    driver.find_element(By.ID, 'answer_param_surname').send_keys(data['values']['lastname'])
    time.sleep(0.5)
    driver.find_element(By.ID, 'answer_param_phone').send_keys(data['values']['phone'])
    time.sleep(0.5)
    driver.find_element(By.ID, 'answer_non_profile_email_5257').send_keys(data['values']['email'])
    for but in driver.find_elements(By.XPATH, "//input[@type='checkbox']"):
        if not but.is_selected():
            but.click()
    time.sleep(0.5)
    # driver.find_elements(By.TAG_NAME, 'button')[-1].click()
    time.sleep(2)
