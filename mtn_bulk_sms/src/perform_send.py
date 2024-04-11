
import asyncio
import os
import time
import traceback
from botasaurus import AntiDetectDriver, browser
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3
from pathlib import Path
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
async def mtn_bulk_sms(driver: AntiDetectDriver, request):
    try:
        limit = 5
        batch_size = 1
        msg_to_paste = os.getenv("DEFAULT_MSG")
        full_screen_height = driver.execute_script(
            "return window.screen.availHeight")
        full_screen_width = driver.execute_script(
            "return window.screen.availWidth")

        driver.set_window_size(full_screen_width-20, full_screen_height)
        driver.set_window_position(0, 0)
        url = f"https://bulksms.mymtn.com.ng/"
        driver.get(url)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="col-md-5 cent loginbutton"]/button[@class="btn btn-white full-btn" and contains(text(), "Login")]'))
        )

        if login_button:
            login_button.click()
            # Find the email and password input fields
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="email"]'))
            )
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="password"]'))
            )

            # Fill in the email and password
            email_input.send_keys(os.getenv("MTN_BULK_SMS_EMAIL"))
            password_input.send_keys(os.getenv("MTN_BULK_SMS_PASS"))

            # Find and click the login button
            procceed_login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@class="btn btn-yellow" and contains(text(), "Login")]'))
            )
            if procceed_login_button:
                procceed_login_button.click()

                # Wait for the link to be clickable
                messaging_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//a[@href="/sms/compose" and contains(text(), "Messaging")]'))
                )
                # Click the link
                messaging_link.click()

                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(
                    script_dir, '..', '..', 'db.local.sqlite3')
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                # Connect to the SQLite database
                print("Connected to the database successfully")

                # Execute a query to select all rows from the bulk_sms table where status is not 1 with a limit of 1000
                # table columns: id, phone, sms_status
                cursor.execute(
                    f"SELECT * FROM bulk_sms WHERE sms_status IS NULL LIMIT {limit}")

                # Fetch all rows from the result set
                rows = cursor.fetchall()

                # Split rows into batches of 10

                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i+batch_size]
                    comma_separated_numbers = ', '.join(
                        [number for _, number, _ in batch])

                    print(f"sending to {comma_separated_numbers}")

                    number_radio = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'input[value="number"]')
                        )
                    )

                    # Check the radio button
                    number_radio.click()

                    # paste numbers
                    textarea = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//textarea[@id="comment"]'))
                    )

                    # Enter text into the textarea
                    text_to_paste = comma_separated_numbers
                    textarea.clear()  # Clear any existing text
                    textarea.send_keys(text_to_paste)

                    dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'select[name="senderId"]')
                        )
                    )

                    # Create a Select object
                    select = Select(dropdown)

                    # Select the option by visible text
                    select.select_by_visible_text('N-Exam')

                    # paste message
                    textarea2 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//textarea[@id="smsMsg"]'))
                    )

                    # Enter text into the textarea

                    textarea2.clear()  # Clear any existing text
                    textarea2.send_keys(msg_to_paste)

                    submit = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//button[@class="btn btn-yellow full-btn" and contains(text(), "Send SMS")]'))
                    )

                    # Scroll to the element and click
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", submit)
                    driver.execute_script("arguments[0].click();",  submit)

                    print(f"waiting for {2}")
                    time.sleep(2)

                    success = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//button[@class="btn btn-yellow full-btn" and contains(text(), "Compose New SMS")]'))
                    )

                    if success:
                        driver.execute_script(
                            "arguments[0].click();",  success)

                        for num in batch:
                            print(f"updating {num[1]}")
                            cursor.execute(f"""
                                UPDATE bulk_sms
                                SET sms_status = 1
                                WHERE id IS {num[0]}
                            """)
                            # Commit the transaction
                            conn.commit()

                    else:
                        print("message not sent")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        # Close the browser window
        driver.quit()
        pass





script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '..', '..', 'db.local.sqlite3')

@browser(
    # block_resources=['.css', '.jpg', '.jpeg', '.png', '.svg', '.gif'],
    add_arguments=["--disable-infobars"],
    reuse_driver=True,
    keep_drivers_alive=True,
    lang='en',
    close_on_crash=True,
    max_retry=3,
    headless=True,
    output=None,
    parallel=None
)
def mtn_bulk_sms_lite(driver: AntiDetectDriver, request):
    try:
        limit = 1000
        batch_size = 1
        msg_to_paste = os.getenv("DEFAULT_MSG")
        full_screen_height = driver.execute_script("return window.screen.availHeight")
        full_screen_width = driver.execute_script("return window.screen.availWidth")

        driver.set_window_size(full_screen_width - 20, full_screen_height)
        driver.set_window_position(0, 0)
        url = f"https://bulksms.mymtn.com.ng/"
        driver.get(url)
        
        
        while True:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="col-md-5 cent loginbutton"]/button[@class="btn btn-white full-btn" and contains(text(), "Login")]'))
            )

            if login_button:
                login_button.click()
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
                )
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
                )

                email_input.send_keys(os.getenv("MTN_BULK_SMS_EMAIL"))
                password_input.send_keys(os.getenv("MTN_BULK_SMS_PASS"))

                procceed_login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//button[@class="btn btn-yellow" and contains(text(), "Login")]'))
                )
                if procceed_login_button:
                    procceed_login_button.click()

                    messaging_link = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//a[@href="/sms/compose" and contains(text(), "Messaging")]'))
                    )
                    messaging_link.click()

                    # Use a context manager for the database connection
                    with sqlite3.connect(file_path) as conn:
                        cursor = conn.cursor()

                        cursor.execute(
                            f"SELECT * FROM bulk_sms WHERE sms_status IS NULL AND wa_status IS NULL LIMIT {limit}"
                        )
                        rows = cursor.fetchall()

                        for i in range(0, len(rows), batch_size):
                            batch = rows[i:i + batch_size]
                            phone_numbers = [row[1] for row in batch]
                            comma_separated_numbers = ', '.join(phone_numbers)

                            print(f"processing {i+1}/{limit}")

                            try:
                                try:
                                    iniSuccess = WebDriverWait(driver, 5).until(
                                                EC.visibility_of_element_located(
                                                    (By.XPATH, '//button[@class="btn btn-yellow full-btn" and contains(text(), "Compose New SMS")]'))
                                            )
                                    driver.execute_script("arguments[0].click();", iniSuccess)
                                except Exception as e:
                                    pass
                                
                                number_radio = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="number"]'))
                                )
                                number_radio.click()

                                textarea = WebDriverWait(driver, 2).until(
                                    EC.presence_of_element_located((By.XPATH, '//textarea[@id="comment"]'))
                                )
                                text_to_paste = comma_separated_numbers
                                textarea.clear()
                                textarea.send_keys(text_to_paste)

                                dropdown = WebDriverWait(driver, 2).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="senderId"]'))
                                )
                                select = Select(dropdown)
                                select.select_by_visible_text('N-Exam')

                                textarea2 = WebDriverWait(driver, 2).until(
                                    EC.presence_of_element_located((By.XPATH, '//textarea[@id="smsMsg"]'))
                                )
                                textarea2.clear()
                                textarea2.send_keys(msg_to_paste)
                                time.sleep(1)
                                submit = WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located(
                                        (By.XPATH, '//button[@class="btn btn-yellow full-btn" and contains(text(), "Send SMS")]'))
                                )
                               
                                driver.execute_script("arguments[0].scrollIntoView(true);", submit)
                               
                                driver.execute_script("arguments[0].click();", submit)

                                max_retries = 50
                                retry_count = 0

                                while retry_count < max_retries:
                                    try:
                                        success = WebDriverWait(driver, 5).until(
                                            EC.visibility_of_element_located(
                                                (By.XPATH, '//button[@class="btn btn-yellow full-btn" and contains(text(), "Compose New SMS")]'))
                                        )
                                        break  # Break the loop if element is found
                                    except Exception as e:
                                        print(f"Element not found, retrying in 1 second... Retry {retry_count}/{max_retries}")
                                        retry_count += 1
                                       
                                        if retry_count == max_retries:
                                            print("Maximum retry count reached. Exiting loop.")
                                            break
                                        
                                        time.sleep(1)  # Wait for 1 second before retrying

                                if success:
                                    driver.execute_script("arguments[0].click();", success)
                                    status = 1
                                else:
                                    print("message not sent")
                                    status = 2
                                    continue
                                if status is 1:
                                    for num in batch:
                                        try:
                                            print(f"updating {num[1]}")
                                            cursor.execute(f"""
                                                UPDATE bulk_sms
                                                SET sms_status = {status}
                                                WHERE id IS {num[0]}
                                            """)
                                            # Commit the changes immediately
                                            conn.commit()
                                            
                                        except sqlite3.Error as e:
                                            print("Error updating record:", e)
                                            traceback.print_exc()
                                            
                            except Exception as e:
                                print(f"An error occurred: {e}")
                                traceback.print_exc()
                                continue  # Continue to the next iteration even if an error occurs
            break

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        driver.quit()
