from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from trader.utilities.environment import REMOTE_WEBDRIVER_HOST, REMOTE_WEBDRIVER_PORT


def create_remote_web_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Remote(f"{REMOTE_WEBDRIVER_HOST}:{REMOTE_WEBDRIVER_PORT}/wd/hub", options=options)
