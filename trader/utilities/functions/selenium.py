from time import sleep
from selenium.webdriver.remote.webdriver import WebDriver


WEB_DRIVER_SCROLL_INCREMENT = 500
WEB_DRIVER_SCROLL_DELAY_SECONDS = 0.5


def fully_scroll_page(web_driver: WebDriver) -> None:
    current_y_offset = web_driver.execute_script("return window.pageYOffset")
    while True:
        web_driver.execute_script(f"window.scrollBy(0, {WEB_DRIVER_SCROLL_INCREMENT})")
        new_y_offset = web_driver.execute_script("return window.pageYOffset")
        if new_y_offset == current_y_offset:
            break
        current_y_offset = new_y_offset
        sleep(WEB_DRIVER_SCROLL_DELAY_SECONDS)
