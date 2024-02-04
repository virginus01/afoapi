import sys
from botasaurus import AntiDetectDriver, browser
from PIL import Image


@browser(
    # block_resources=['.css', '.jpg', '.jpeg', '.png', '.svg', '.gif'],
    add_arguments=[],
    reuse_driver=True,
    keep_drivers_alive=True,
    lang='en',
    close_on_crash=True,
    max_retry=3,
    headless=False,
    output=None,
)
def scrape_heading_task(driver: AntiDetectDriver, data):
    try:
        url = "https://topingnow.com/gimages/list/virginus-alajekwu"

        # Open the URL
        driver.get(url)

        heading = driver.text("h1")
        # Take a screenshot
        driver.save_screenshot("screenshot")
        screenshot = Image.open("output/screenshots/screenshot.png")
        screenshot.show()

        return {"heading": heading}

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser window
        driver.quit()


if __name__ == "__main__":
    # Initiate the web scraping task
    scrape_heading_task()
