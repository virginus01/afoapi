import requests
from concurrent.futures import ThreadPoolExecutor
from functools import partial

def push_attack(url, session):
    try:
        response = session.get(url, timeout=10)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print(f"Page {url} visited successfully")
        else:
            print(f"Failed to visit {url}. Status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"Timeout occurred. Could not visit {url} within 10 seconds.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for {url}: {e}")

def push_attacks(url, num_attacks=2, max_workers=10):
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Use a partial function to pass both URL and session to the worker
            worker = partial(push_attack, session=session)
            # Start tasks to visit the webpage concurrently
            futures = [executor.submit(worker, url) for _ in range(num_attacks)]
            # Wait for all tasks to complete
            for num, future in enumerate(futures):
                print(num+1)
                future.result()