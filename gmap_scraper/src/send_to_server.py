import datetime
import requests
import json


def post_topics(data):
    try:
        # Replace 'your_api_endpoint' with the actual endpoint URL
        api_endpoint = 'http://localhost:3000/api/post/post_topics'
        post_data = []

        for item in data:
            try:
                query = str(item.get("query")).replace(
                    '"', "").replace(',', '').strip()

                if not query:
                    continue

                d = {
                    'title': query,
                    'description': f'This is list of {query}',
                    'body': f'This is list of {query}',
                    'createdAt': datetime.datetime.now().isoformat(),
                    'topId': '{top}',
                    'image': '',
                    'selectedImage': '',
                    'lists': item.get("places")
                }
                if len(item.get("places")) >= 1:
                    print(f"""{len(item.get("places"))
                               } lists appended to {query}""")
                    post_data.append(d)

            except Exception as e:
                print(f"Error processing item: {str(e)}")

        data_to_send = {
            'postData': post_data,
            'isImport': True,
            'update': True,
            'source': "gmap",
        }

        json_data = json.dumps(data_to_send)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(api_endpoint, data=json_data, headers=headers)

        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'message': response.text}

    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f"Request failed: {str(e)}"}
    except Exception as e:
        return {'success': False, 'message': f"An error occurred: {str(e)}"}
