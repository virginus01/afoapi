import datetime
import sys
import requests
import json


def post_topics(data):

    # print(data)
    # print(places)
    # sys.exit()
    try:
        # Replace 'your_api_endpoint' with the actual endpoint URL
        api_endpoint = 'http://localhost:3000/api/post/post_topics'

        # Your data to be sent in the POST request

        post_data = []

        for item in data:
            try:
                d = {
                    'title': item["query"],
                    'description': f'This is like of {item["query"]} in Nigeria as of year',
                    'body': f'This is like of {item["query"]} in Nigeria as of year',
                    'createdAt': str(datetime.datetime.now()),
                    'topId': f'{{top}}',
                    'image': '',
                    'selectedImage': '',
                    'lists': item["places"]
                }
                post_data.append(d)
            except Exception as e:
                print(f"Error processing item {item}: {str(e)}")

        data_to_send = {
            'postData': post_data,
            'isImport': True,
            'update': True,
            'source': "gmap",
        }
        # Convert the data to JSON format (if needed)

        json_data = json.dumps(data_to_send)

        # Set the headers if sending JSON data
        headers = {'Content-Type': 'application/json'}

        # Make the POST request
        response = requests.post(api_endpoint, data=json_data, headers=headers)

        # Check the response status and print the result
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'message': response.text}

    except Exception as e:
        return {'success': False, 'message': str(e)}
