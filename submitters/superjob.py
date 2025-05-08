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


def superjob_submit_handler(
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
    driver.find_element(By.XPATH, '//*[@id=":Rbja6j6cvfesrnnjb:"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*/input[@name="contactInfo.name"]').send_keys(
        data['values']['firstname']
    )
    driver.find_element(By.XPATH, '//*/input[@name="contactInfo.surname"]').send_keys(
        data['values']['lastname']
    )
    driver.find_element(By.XPATH, '//*/input[@name="contactInfo.phoneNumber"]').send_keys(
        data['values']['phone']
    )
    driver.find_element(By.XPATH, '//*/input[@name="contactInfo.dateOfBirth"]').send_keys(
        data['values']['birthday']
    )
    time.sleep(1)
    # driver.find_element(By.XPATH, '//*[@id=":r5:"]').click()
    time.sleep(2)
    driver.get('https://google.com')
