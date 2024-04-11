import random
import sqlite3
import time
import traceback
from botasaurus import AntiDetectDriver, browser
import asyncio
import os
import time
import traceback
from botasaurus import AntiDetectDriver, browser
from httpcore import TimeoutException
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote
from selenium.common.exceptions import StaleElementReferenceException


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


@browser(
    # block_resources=['.css', '.jpg', '.jpeg', '.png', '.svg', '.gif'],
    add_arguments=["--disable-infobars"],
    reuse_driver=True,
    keep_drivers_alive=True,
    lang='en',
    close_on_crash=True,
    max_retry=3,
    headless=False,
    output=None,
    parallel=None

)
def click_and_send(driver: AntiDetectDriver, request):
    try:
        limit = 3
        batch_size = 1
        msg_to_paste = os.getenv("DEFAULT_WA_MSG")

        full_screen_height = driver.execute_script(
            "return window.screen.availHeight")
        full_screen_width = driver.execute_script(
            "return window.screen.availWidth")

        driver.set_window_size(full_screen_width, full_screen_height)
        driver.set_window_position(0, 0)
        url = f"https://web.whatsapp.com/#"
        driver.get(url)

        try:
            elm = driver.get_element_or_none_by_selector(
                "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1)", 5)

            wait_time = 50
            
            while True:
                elm = driver.get_element_or_none_by_selector(
                    "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1)",
                    10
                )
           
                if elm is not None:
                    if "Point your phone at this screen to capture the QR code" in elm.text:
                        print(
                            "Point your phone at this screen to capture the QR code")
                        time.sleep(5)
                    elif "Loading your chats" in elm.text:
                        print("Loading your chats wait")
                        wait_time += 10
                        time.sleep(5)
                    elif "Search or start new chat" not in elm.text:
                        print("not fully loaded")
                        wait_time += 5
                        time.sleep(5)
                    else:
                        break
                elif elm is None:
                    print("still loading element not found")
                    wait_time += 5
                    time.sleep(5)
                else:
                    break

            print(f"waiting for {wait_time} seconds")
            time.sleep(wait_time)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(
                script_dir, '..', '..', 'db.local.sqlite3')
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            # Connect to the SQLite database
            print("Connected to the database successfully")

            # Execute a query to select all rows from the bulk_sms table where status is not 1 with a limit of 1000
            # table columns: id, phone, wa_status
            cursor.execute(
                f"SELECT * FROM bulk_sms WHERE wa_status IS NULL LIMIT {limit}")

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Split rows into batches
            for i in range(0, len(rows), batch_size):
                indx = str(int(i)+1)
                batch = rows[i:i+batch_size]
                for num_index, num in enumerate(batch):
                    name = fetchName(num[1][-10:], "Candidate")
                    
                    if num[3] is not None:
                        msg_to_paste = replaceName(num[3], name)
                    else:
                        msg_to_paste = replaceName(os.getenv("DEFAULT_WA_MSG"), name)
                        
                    msg_to_paste = quote(msg_to_paste)
                    
                    phone = process_number("2348164614193")
                    print(f"---- sending msg to {phone} -----")
                    send_url = f"""https://api.whatsapp.com/send/?phone={
                        phone}&text={msg_to_paste}&type=phone_number&app_absent=0"""
             
                    driver.execute_script(f"arguments[0].innerHTML = '<a href=\"{
                        send_url}\" id=\"contact{phone}\">{phone}</a>';", elm)

                    sending_link = driver.get_element_or_none_by_selector(
                        "html > body > div:nth-of-type(1) > div > div > div:nth-of-type(3) > div > div:nth-of-type(1) > a", 1)

                    if sending_link is None:
                        print("Cannot locate element with link to click")
                    else:
                        
                        driver.js_click(sending_link)
                        
                        if str(indx) == str('1') and str(num_index) == "1":
                            print(f"initial waiting: {wait_time/2}")
                            time.sleep(wait_time/2)
                        else:
                            time.sleep(2)
                         
                         
                        try:   
                            el = driver.get_element_or_none_by_selector(
                                'span[data-icon="send"]', 2)

                            status = 0
                            if el is None:
                                print(
                                    f"Cannot locate element with selector span[data-icon='send']")
                                status = 2
                            else:
                            # msg_area = driver.get_elements_or_none_by_xpath(
                                    #'//span[@class="selectable-text copyable-text"]', 5)
                                #msg_area[0].send_keys(msg_to_paste[1:])
                                
                                time.sleep(1)
                                driver.js_click(el)
                                status = 1
                                print(f"---- message sent to {phone} -----")
                           
                        except StaleElementReferenceException:
                          
                            el = driver.get_element_or_none_by_selector('span[data-icon="send"]', 2)
                            if el:
                                time.sleep(1)
                                driver.js_click(el)
                                status = 1
                                print(f"---- message sent to {phone} -----")
                            
                        driver.execute_script(
                            "arguments[0].parentNode.removeChild(arguments[0]);", sending_link)

                        cursor.execute(f"""
                            UPDATE bulk_sms
                            SET wa_status = '{status}',
                                name = '{name}'
                            WHERE id = {num[0]}
                        """)
                        conn.commit()
 
            print("sleeping after batch")
            time.sleep(int(random.randint(1, 10)))
        except Exception as e:
            print(e)
            traceback.print_exc()
            pass

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        pass

    finally:
        # Close the browser window
        driver.quit()
        pass


def process_number(number):
    # Convert number to string
    number_str = str(number)

    # Check if the number starts with '0' or if its length is 11 digits
    if number_str.startswith('0') or len(number_str) == 11:
        # Extract last 10 digits
        last_10_digits = number_str[-10:]

        # Append '234' before the last 10 digits
        final_number = '234' + last_10_digits

        return final_number
    else:
        # Return original number
        return number_str

def replaceName(msg, name):
    body = str(msg)
    # Perform replacement and assign the result back to `body`
    final_body = body.replace("%name%", name)
    final_body = final_body.replace("%random%", str(random.randint(111111111, 999999999)))
    return final_body


def fetchName(account, default):
    time.sleep(int(random.randint(1, 5)))
    return default
    opay = resolve(account, "999992")
    palmpay = resolve(account, "999991")
    fcmb = resolve(account, "214")

    if opay is not False:
        return opay
    elif palmpay is not False:
        return palmpay
    elif fcmb is not False:
        return fcmb
    else: return default

def resolve(account, code):
    url = 'https://api.paystack.co/bank/resolve'
    params = {'account_number': account, 'bank_code': code}
    headers = {'Authorization': 'Bearer sk_test_a1943aba06966d9cf955f5f1a5381002c92098e7'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if(data["status"] == True):
            return data["data"]["account_name"]
        else:
            return False
    else:
        return False