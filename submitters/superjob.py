import time
from datetime import datetime

from .base import (
    ResponseData,
    get_response_data,
)
from .config import (
    webdriver,
    service,
    options,
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
    driver = webdriver.Chrome(options=options, service=service)
    driver.set_page_load_timeout(30)
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
    phone = (
        data['values']['phone'][1:]
        if data['values']['phone'][0] == '8'
        else data['values']['phone'][2:]
    )
    driver.find_element(By.XPATH, '//*/input[@name="contactInfo.phoneNumber"]').send_keys(phone)
    date_of_birth = datetime.fromisoformat(data['values']['birthday'])
    driver.find_element(By.XPATH, '//*/input[@name="contactInfo.dateOfBirth"]').send_keys(
        date_of_birth.strftime('%d.%m.%Y')
    )
    time.sleep(1)
    # driver.find_element(By.XPATH, '//*[@id=":r5:"]').click()
    # time.sleep(5)
    driver.close()
