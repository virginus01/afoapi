import base64
from io import BytesIO
import traceback
from botasaurus import AntiDetectDriver, browser
from PIL import Image
from django.http import HttpResponse, JsonResponse
import boto3


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
        traceback.print_exc()
    finally:
        # Close the browser window
        driver.quit()


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
    cache=False

)
def save_screenshot(driver: AntiDetectDriver, data):

    try:
        # Open the URL
        driver.get(data["url"])
        path = f"output/screenshots/{data["slug"]}.png"
        driver.set_window_size(1920, 1080,)
        driver.save_screenshot(data["slug"])

        return {'path': path, 'driver': driver}

    except Exception as e:
        print(f"An error occurred: {e}")
        # driver.quit()
        traceback.print_exc()
        return {'path': ''}
    finally:
        # Close the browser window
        # driver.quit()
        pass


def upload_image_to_s3(file_path, bucket_name, s3_key):
    # Create an S3 client
    s3 = boto3.client('s3')
    # Upload file to S3 bucket
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        # print(f"{s3_key} upload Successful")
    except FileNotFoundError as e:
        print(f"The file was not found {e}")
    except ConnectionError as exc:
        print("Connection error occurred: {0}".format(exc))
