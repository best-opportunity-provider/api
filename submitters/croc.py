import time

from .base import (
    ResponseData,
    get_response_data,
)
from .config import (
    webdriver,
    service,
    options,
    By,
    WebDriverWait,
)
from database import (
    OpportunityForm,
    OpportunityFormResponse,
)


def croc_submit_handler(
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
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="form_text_1"]').send_keys(
        data['values']['firstname'] + ' ' + data['values']['lastname']
    )
    driver.find_element(By.XPATH, '//*[@id="form_text_2"]').send_keys(data['values']['email'])
    phone = (
        data['values']['phone'][1:]
        if data['values']['phone'][0] == '8'
        else data['values']['phone'][2:]
    )
    driver.find_element(By.XPATH, '//*[@id="form_text_3"]').send_keys(phone)
    driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(data['values']['cv'])
    driver.find_element(By.XPATH, '//*[@id="responseForm"]/div/form/div[11]/div/div/label').click()
    time.sleep(1)
    driver.find_element(By.CLASS_NAME, 'vacancy-response__send-btn').click()
    time.sleep(3)
    driver.close()
