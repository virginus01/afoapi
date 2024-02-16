import random
import re as rex
import json
from datetime import datetime
import string
import sys

from src.scraper_utils import create_search_link


def toiso(date):
    return date.isoformat()


def convert_timestamp_to_iso_date(timestamp):
    # Convert from microseconds to milliseconds
    milliseconds = int(timestamp) / 1000
    # Create a new Date object
    date = datetime.utcfromtimestamp(milliseconds)
    # Return the date in the specified format
    return toiso(date)


def clean_link(link):
    if link is not None:
        # Remove everything starting from "&opi"
        opi_index = link.find('&opi')
        if opi_index != -1:
            link = link[:opi_index]

        # Remove "/url?q=" if it's at the start of the link
        if link.startswith('/url?q='):
            link = link[len('/url?q='):]

    return link


def safe_get(data, *keys):
    for key in keys:
        try:
            data = data[key]
        except (IndexError, TypeError, KeyError):
            return None
    return data


def get_categories(data):
    return safe_get(data, 6, 13)


def get_place_id(data):
    return safe_get(data, 6, 78)


def get_hl_from_link_competitors(link):
    # Regular expression to find the 'hl' parameter in the URL
    match = rex.search(r"[?&]hl=([^&]+)", link)

    # If found, return the value, otherwise return 'en'
    return match.group(1) if match else None


def extract_google_maps_contributor_url(input_url):
    if input_url is not None:
        # Define a regular expression pattern to match the desired URL
        pattern = r'https://www\.google\.com/maps/contrib/\d+'

        # Use re.search to find the first match in the input_url
        match = rex.search(pattern, input_url)

        if match:
            # Extract the matched URL
            contributor_url = match.group(0)

            # Add "/reviews?entry=ttu" to the end of the URL
            contributor_url += '/reviews?entry=ttu'

            return contributor_url
        else:
            return None


def get_rating(data):
    return safe_get(data, 6, 4, 7)


def get_reviews(data):
    return safe_get(data, 6, 4, 8)


def get_price_range(data):
    rs = safe_get(data, 6, 4, 2)

    if rs is not None:
        return len(rs) * "$"


def get_title(data):
    return safe_get(data, 6, 11)


def get_phone(data):
    return safe_get(data, 6, 178, 0, 3)


def get_about(data):
    return safe_get(data, 6, 154, 0, 0)


def get_address(data):
    return safe_get(data, 6, 18)


def get_website(data):
    return clean_link(safe_get(data, 6, 7, 0))


def get_main_category(data):
    return safe_get(data, 6, 13, 0)


def get_feautured_image(data):
    return safe_get(data, 6, 37, 0, 0, 6, 0)


def get_images_0(data):
    image = safe_get(data, 6, 171, 0, 0, 3, 0, 6, 0)
    if image is None:
        return ''
    else:
        return image


def get_images_1(data):
    image = safe_get(data, 6, 171, 0, 1, 3, 0, 6, 0)
    if image is None:
        return ''
    else:
        return image


def get_images_2(data):
    image = safe_get(data, 6, 171, 0, 2, 3, 0, 6, 0)
    if image is None:
        return ''
    else:
        return image


def get_images_3(data):

    image = safe_get(data, 6, 171, 0, 3, 3, 0, 6, 0)
    if image is None:
        return ''
    else:
        return image


def get_workding_days(data):
    return safe_get(data, 6, 203, 0)


def get_time_zone(data):
    return safe_get(data, 6, 30)


def get_icon(data):
    return safe_get(data, 6, 157)


def get_location(data):
    return safe_get(data, 6, 166)


def get_lang_long(data):
    return safe_get(data, 6, 107)


def get_lang_short(data):
    return safe_get(data, 6, 110)


def get_country(data):
    return safe_get(data, 6, 243)


def parse(data):
    # Assuming 'input_string' is provided to the function in some way
    input_string = json.loads(data)[3][6]  # Replace with actual input
    substring_to_remove = ")]}'"

    modified_string = input_string
    if input_string.startswith(substring_to_remove):
        modified_string = input_string[len(substring_to_remove):]

    return json.loads(modified_string)


def get_hl_from_link(link):
    # Regular expression to find the 'hl' parameter in the URL
    match = rex.search(r"[?&]hl=([^&]+)", link)

    # If found, return the value, otherwise return 'en'
    return match.group(1) if match else 'en'


def extract_business_name(url):
    # Regular expression to match the pattern in the URL
    match = rex.search(r"maps/place/([^/]+)", url)
    if match:
        return match.group(1)
    return None


def extract_coordinates(data):
    link = safe_get(data, 6, 42)
    # Regular expression pattern to match coordinates in the link
    pattern = r'@(-?\d+\.\d+),(-?\d+\.\d+)'

    # Find coordinates in the link using regular expression
    match = rex.search(pattern, link)

    if match:
        # Extract latitude and longitude from the matched groups
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        return latitude, longitude
    else:
        return None


def find_most_common_element(ls):
    if not ls:
        return None  # Handle empty list case

    # Dictionary to count occurrences of each element
    element_count = {}
    for element in ls:
        if element in element_count:
            element_count[element] += 1
        else:
            element_count[element] = 1

    # Find the most common element
    max_count = max(element_count.values())
    common_elements = [k for k, v in element_count.items() if v == max_count]

    # Return the first element if all occur equally, else return the most common one
    return common_elements[0]


def parse_extract_possible_map_link(data):
    # Assuming 'input_string' is provided to the function in some way
    loaded = json.loads(data)

    input_string = safe_get(loaded, 3, -1)   # Replace with actual input
    substring_to_remove = ")]}'"

    modified_string = input_string
    if input_string.startswith(substring_to_remove):
        modified_string = input_string[len(substring_to_remove):]

    return json.loads(modified_string)


def perform_extract_possible_map_link(input_str):
    data = parse_extract_possible_map_link(input_str)
    return safe_get(data, 6, 27) or safe_get(data, 0, 1, 0, 14, 27)


def check_data(data):
    try:
        # Define the pool of characters to choose from
        characters = string.ascii_letters + string.digits  # Alphanumeric characters

        # Generate random code
        random_code = ''.join(random.choice(characters) for _ in range(10))

        n = 0

        with open(f'output.txt', 'a', encoding='utf-8') as file:
            for key in data:
                if key is not None:
                    output_line = f"key: {n} {str([key])}\n"
                    print(
                        output_line+"------------------------------------------------------------------------------")
                    file.write(output_line)
                n += 1
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    sys.exit()


def get_detailed_reviews(data):
    reviews = []
    data = safe_get(data, 6, 52, 0)
    if data is not None:
        for r in data:
            r_data = {
                'reviewer': safe_get(r, 0, 1),
                'reviewer_image': safe_get(r, 0, 0),
                'review': safe_get(r, 3)
            }
            reviews.append(r_data)
    return reviews


def extract_data(input_str, link):

    try:
        data = parse(input_str)
        # if data[6][203][0] is not None:
        # check_data(data[6][203][0])
        # print(get_workding_days(data))
        # sys.exit()

        all_images = f"{get_images_0(data)}, {get_images_1(data)}, {
            get_images_2(data)}, {get_images_3(data)}"

        categories = get_categories(data)
        place_id = get_place_id(data)
        title = get_title(data)
        rating = get_rating(data)
        reviews = get_reviews(data)
        address = get_address(data)
        website = get_website(data)
        main_category = get_main_category(data)
        about = get_about(data)
        featured_image = get_feautured_image(data)
        phone = get_phone(data)
        detailed_reviews = get_detailed_reviews(data)
        workday_timing = get_workding_days(data)
        time_zone = get_time_zone(data)
        location = get_location(data)
        lat = extract_coordinates(data)[0]
        long = extract_coordinates(data)[1]
        icon = get_icon(data)
        lang_long = get_lang_long(data)
        lang_short = get_lang_short(data)
        country = get_country(data)

        return {
            'place_id': place_id,
            'name': title,
            'link': link,
            'main_category': main_category,
            'categories': categories,
            'rating': rating,
            'reviews': reviews,
            'address': address,
            'website': website,
            'about': about,
            'featured_image': featured_image,
            'phone': phone,
            'all_images': all_images,
            'detailed_reviews': detailed_reviews,
            'workday_timing': workday_timing,
            'time_zone': time_zone,
            'location': location,
            'latitude': lat,
            'longitude': long,
            'lang_long': lang_long,
            'lang_short': lang_short,
            'country': country,
            'icon': icon,
        }
    except Exception as e:
        print(f"error in extract_data: {e}")
        pass
