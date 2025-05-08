import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


service = ChromeService(executable_path=f'{os.getcwd()}/submitters/chromedriver.exe')
options = webdriver.ChromeOptions()
options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--headless")
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
)
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(30)

__all__ = [
    'driver',
    'By',
    'WebDriverWait',
]
