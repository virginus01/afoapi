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

    def custom_click(self: WebDriver, selector, wait=10, url='', index=0, data={}):
        phone = data.get("phone", "23481")
        msg = data.get("message", "no message")
        result = {'id': phone, 'success': True, "info": 'sent'}
        try:
            i = str(int(index)+1)

            elm = None
            elm = self.get_element_or_none_by_selector(
                "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1)", 5)

            while True:
                elm = self.get_element_or_none_by_selector(
                    "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1)",
                    10
                )
                if elm is not None:
                    if "Point your phone at this screen to capture the QR code" in elm.text:
                        print(
                            "Point your phone at this screen to capture the QR code")
                        time.sleep(10)
                    elif "Loading your chats" in elm.text:
                        print("Loading your chats wait")
                        time.sleep(10)
                    else:
                        break
                else:
                    print("loading chats")
                    time.sleep(30)

            print("waiting for 3 seconds")
            time.sleep(3)

            self.execute_script(f"arguments[0].innerHTML = '<a href=\"{
                                url}\" id=\"contact{i}\">{i}</a>';", elm)

            elm2 = self.get_element_or_none_by_selector(
                "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1) > a", 5)

            if elm2 is None:
                result = {'id': phone, 'success': False,
                          "info": 'Cannot locate element with selector 2'}
            else:
                time.sleep(1)
                self.js_click(elm2)

                if str(i) == str('1'):
                    time.sleep(50)
                    print("initial waiting")
                else:
                    pass

                el = self.get_element_or_none_by_selector(
                    selector, wait)

                if el is None:
                    print(f"Cannot locate element with selector {selector}")
                    result = {'id': phone, 'success': False,
                              "info": f"Cannot locate element with selector {selector}"}

                else:
                    self.js_click(el)
                    print(f"---- message sent to {phone} -----")
                    result = {'id': phone, 'success': True,
                              "info": f"message sent to {phone}"}

        except Exception as e:
            print(e)
            result = {'id': phone, 'success': False, "info": e}

        finally:
            time.sleep(5)
            return result
