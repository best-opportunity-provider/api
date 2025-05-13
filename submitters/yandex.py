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
    EC,
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
    driver = webdriver.Chrome(options=options, service=service)
    driver.set_page_load_timeout(30)
    driver.get(data['link'])
    wait = WebDriverWait(driver, 20)
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
    checkboxes = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']"))
    )
    for checkbox in checkboxes:
        driver.execute_script('arguments[0].click();', checkbox)
    time.sleep(0.5)
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@type='submit']")
    ))
    submit_button.click()
    time.sleep(5)
    driver.close()
