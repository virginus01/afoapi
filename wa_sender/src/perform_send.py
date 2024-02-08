
import time
from botasaurus import AntiDetectDriver, browser


@browser(
    # block_resources=['.css', '.jpg', '.jpeg', '.png', '.svg', '.gif'],
    add_arguments=["--disable-infobars", "--app=https://web.whatsapp.com"],
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
        nums = [{'message': "test 1", 'phone': "2348164614193"},
                {'message': "test 2", 'phone': "2349079979013"}]

        full_screen_height = driver.execute_script(
            "return window.screen.availHeight")

        driver.set_window_size(1080, full_screen_height)
        driver.set_window_position(0, 0)
        url = f"https://web.whatsapp.com/#"
        driver.get(url)
        results = []
        for index, num in enumerate(nums):
            phone = num["phone"]
            msg = num["message"]
            send_url = f"""https://api.whatsapp.com/send/?phone={
                phone}&text={msg}"""

            result = driver.custom_click(
                'span[data-icon="send"]', 2, send_url, index, num)
            results.append(result)

        print(results)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser window
        driver.quit()
        pass
