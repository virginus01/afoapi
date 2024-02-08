import time
from botasaurus import AntiDetectDriver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SecureDriver(AntiDetectDriver):

    def custom_click2(self: WebDriver, selector, wait=10, url='', index=0):

        elm = self.get_element_or_none_by_selector(
            "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1)", 5)

        while elm is None:
            try:
                elm = self.get_element_or_none_by_selector(
                    "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1)",
                    5
                )
            except:
                print("Element not found, retrying...")
                time.sleep(10)

        print("sleeping")
        time.sleep(wait)

        self.execute_script(f"""arguments['0'].innerHTML = '<a href=\"{
                            url}\">send</a>';""", elm)

        elm2 = self.get_element_or_none_by_selector(
            "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1) > a", 5)

        if elm2 is None:
            raise NoSuchElementException(
                f"Cannot locate element with selector 2")
        else:

            self.js_click(elm2)
            time.sleep(5)
            el = self.get_element_or_none_by_selector(
                selector, 2)
            self.js_click(el)
            print("clicked")
