import requests
import json

from getPersonalDetails import auth_token



def fetch_redirect_location(url, auth_token, initial_cookies):
    """
    Fetches the redirect location URL if present in the response headers.

    Parameters:
        url (str): The initial URL to make the GET request.
        auth_token (str): The Authorization token.
        initial_cookies (dict): Cookies to update in the session.

    Returns:
        str: The location URL from the response headers, if found.
        None: If no location header is present.
    """
    # Create a session to manage cookies
    session = requests.Session()

    # Set up session headers with Authorization token
    session.headers.update({
        "Authorization": auth_token
    })

    # Update the session's cookies
    session.cookies.update(initial_cookies)

    # Make a GET request through the session
    response = session.get(url, allow_redirects=False)

    if 'Location' in response.headers:
        location_url = response.headers['Location']
        print(f"Location Header Found: {location_url}")
        return location_url
    else:
        print("No Location Header Found.")
        return None

def fetch_user_data(uuid, auth_token):
    """
    Fetches user data from the API using the provided UUID.

    Parameters:
        uuid (str): The unique identifier of the user.
        auth_token (str): The Authorization token.

    Returns:
        dict: JSON response if the API call is successful and returns valid JSON.
        str: Error message if JSON parsing fails or the API call is unsuccessful.
    """
    url = f"https://api.bniconnectglobal.com/member-api/v2/home?uuId={uuid}"

    headers = {
        "Authorization": auth_token
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        print("Response Status Code:", response.status_code)

        # Parse and return JSON response if successful
        response.raise_for_status()
        response_data = response.json()
        return response_data

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except ValueError:
        return f"Error parsing JSON response. Raw response: {response.text}"
    except Exception as err:
        return f"An unexpected error occurred: {err}"

if __name__ == "__main__":
    # Define the URL and Authorization token
    initial_url = "https://www.bniconnectglobal.com/web/secure/networkHome?userId=197729"
    auth_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbmRpdmlkdWFsVHlwZSI6Ik1FTUJFUiIsInVzZXJfbmFtZSI6ImRoYXdhbEB0ZXhwbGUuY29tIiwiY29uY2VwdCI6IkNPTk5FQ1QiLCJpbmRpdmlkdWFsSWQiOjY3ODU1MDksImF1dGhvcml0aWVzIjpbIjY3OGEzNDlkZTk2ZGM4MWE1Y2U3MmRjZiJdLCJjbGllbnRfaWQiOiJNRU1CRVJfUFJPRklMRV9QT1JUQUwiLCJsb2NhbGVDb2RlIjoiZW5fSU4iLCJzY29wZSI6WyJjb3JlIiwibWVtYmVyIiwic29jaWFsIl0sImFjY2VwdGVkVG9TIjpbOF0sImlkIjoiMTY4NjEwMSIsImV4cCI6MTczNzEyMjEyOSwicm9sZUdyb3VwcyI6WyJNRU1CRVIiXSwianRpIjoiNmVkYWRmZDktYTUzZS00MDVhLThmMDUtMzFmMTVjNTlhMTQxIiwia2V5IjoiNjc4YTM0OWRlOTZkYzgxYTVjZTcyZGNmIn0.BX8v-pmbYXLo2zV1vSdE7CDHb-oJ-8cH_q-UY3OXS78"
    # Define initial cookies as a dictionary
    initial_cookies = {
        "loggedOutStatus": "false",
        "logCurTime": "1737111311870",
        "JSESSIONID": "2FEB64E3A89F94A41D8CB8B81B4CF66D",
        "OLDSESSIONID": "2FEB64E3A89F94A41D8CB8B81B4CF66D",
        "lastSelectedLandingMenuId": "0"
    }

    # Fetch redirect location
    redirect_location = fetch_redirect_location(initial_url, auth_token, initial_cookies)

    if redirect_location:
        print("Redirect Location:", redirect_location)

    # Example UUID
    user_uuid = redirect_location.split("=")[1]
    print("uuid: ",user_uuid)

    # Fetch user data
    user_data = fetch_user_data(user_uuid, auth_token)

    if isinstance(user_data, dict):
        print("User Data:", json.dumps(user_data, indent=4))
    # else:
    #     print("Error:", user_data)
