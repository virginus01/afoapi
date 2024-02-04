import base64
from io import BytesIO
from botasaurus import AntiDetectDriver, browser
from PIL import Image
from django.http import HttpResponse, JsonResponse


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
def take_screenshot(driver: AntiDetectDriver, request):
    try:

        url = request.GET.get('url', '')
        if not url:
            return HttpResponse({'data': "URL parameter is missing"}, status=400)

        # Open the URL
        driver.get(url)

        # driver.save_screenshot("screenshot")
        driver.set_window_size(1920, 1080,)
        base64_image = driver.get_screenshot_as_base64()
        # screenshot = Image.open()
        # screenshot.show()

        image_bytes = base64.b64decode(base64_image)

        # Create a bytes buffer
        buffer = BytesIO(image_bytes)
        return HttpResponse(buffer, content_type='image/png')

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser window
        driver.quit()


if __name__ == "__main__":
    # Initiate the web scraping task
    take_screenshot()
