# import requests
# import json
# # import scrapingScript
#
#
# # Define the URL and Authorization token
# url = "https://bniconnectglobal.com/web/secure/networkHome?userId=197637"
# # authorization_token = (
# #     "Bearer"+" "+scrapingScript.access_token
# # )
#
# # Define headers
# headers = {
#     "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbmRpdmlkdWFsVHlwZSI6Ik1FTUJFUiIsInVzZXJfbmFtZSI6ImRoYXdhbEB0ZXhwbGUuY29tIiwiY29uY2VwdCI6IkNPTk5FQ1QiLCJpbmRpdmlkdWFsSWQiOjY3ODU1MDksImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiJdLCJjbGllbnRfaWQiOiJJREVOVElUWV9QT1JUQUwiLCJsb2NhbGVDb2RlIjoiZW5fSU4iLCJzY29wZSI6WyJjb3JlIiwicHVibGljX2NoYXB0ZXJfZGV0YWlscyIsImdyb3VwcyIsInRpcHMiLCJwdWJsaWNfdHJhbnNsYXRpb25zIiwibWVtYmVyIiwib25saW5lX2FwcGxpY2F0aW9ucyIsInNvY2lhbCIsInB1YmxpY19wb3J0YWwiXSwiYWNjZXB0ZWRUb1MiOls4XSwiYXRpIjoiYTM3ZDU5YjQtMGJhYi00ZDM0LWI1OTAtNzFmM2M4NzA0NDNhIiwiaWQiOiIxNjg2MTAxIiwiZXhwIjoxNzM3MTIxMTAzLCJyb2xlR3JvdXBzIjpbIk1FTUJFUiJdLCJqdGkiOiJjNDIxOTY4Yi0xNTJkLTQ2YjEtOWFkMi1mMjU3NTI0NGQzODUiLCJrZXkiOiI2NzhhMjUwZjgyZGRlNzFkN2E1NDJmYjgifQ.123K1mjuDob7bQcOiAEx4MtFCOr_bhNv7yjDBtlVJeg',
# }
#
# # Make a GET request
# response = requests.get(url, headers=headers)
#
# # Print response status code and JSON data
# print("Response Status Code:", response.status_code)
# try:
#     response_data = response.json()  # Attempt to parse the response as JSON
#     print("Response JSON:", print(json.dumps(response_data, indent=4)))
# except ValueError:
#     print("Error parsing JSON response.")
#     print("Raw Response Text:", response.text)

# cookies code
import requests
import json

# Define the URL
url = "https://www.bniconnectglobal.com/web/secure/networkHome?userId=197729"

# Create a session to manage cookies
session = requests.Session()

auth_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbmRpdmlkdWFsVHlwZSI6Ik1FTUJFUiIsInVzZXJfbmFtZSI6ImRoYXdhbEB0ZXhwbGUuY29tIiwiY29uY2VwdCI6IkNPTk5FQ1QiLCJpbmRpdmlkdWFsSWQiOjY3ODU1MDksImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiJdLCJjbGllbnRfaWQiOiJJREVOVElUWV9QT1JUQUwiLCJsb2NhbGVDb2RlIjoiZW5fSU4iLCJzY29wZSI6WyJjb3JlIiwicHVibGljX2NoYXB0ZXJfZGV0YWlscyIsImdyb3VwcyIsInRpcHMiLCJwdWJsaWNfdHJhbnNsYXRpb25zIiwibWVtYmVyIiwib25saW5lX2FwcGxpY2F0aW9ucyIsInNvY2lhbCIsInB1YmxpY19wb3J0YWwiXSwiYWNjZXB0ZWRUb1MiOls4XSwiYXRpIjoiYTM3ZDU5YjQtMGJhYi00ZDM0LWI1OTAtNzFmM2M4NzA0NDNhIiwiaWQiOiIxNjg2MTAxIiwiZXhwIjoxNzM3MTIxMTAzLCJyb2xlR3JvdXBzIjpbIk1FTUJFUiJdLCJqdGkiOiJjNDIxOTY4Yi0xNTJkLTQ2YjEtOWFkMi1mMjU3NTI0NGQzODUiLCJrZXkiOiI2NzhhMjUwZjgyZGRlNzFkN2E1NDJmYjgifQ.123K1mjuDob7bQcOiAEx4MtFCOr_bhNv7yjDBtlVJeg"

# Set up session headers with Authorization token
session.headers.update({
    "Authorization": auth_token
})

# Define initial cookies as a dictionary
initial_cookies = {
    "loggedOutStatus": "false",
    "logCurTime": "1737106729950",
    "JSESSIONID": "5C16AF5FA6F1BC50B3B14B7A3E57809F",
    "OLDSESSIONID": "5C16AF5FA6F1BC50B3B14B7A3E57809F",
    "lastSelectedLandingMenuId": "0"
}

# Update the session's cookies
session.cookies.update(initial_cookies)

# Make a GET request through the session
response = session.get(url, allow_redirects=False)

if 'Location' in response.headers:
    location_url = response.headers['Location']
    print(f"Location Header Found: {location_url}")


def fetch_user_data(uuid):
    # url = f"https://bniconnectglobal.com/web/secure/networkHome?userId={user_id}"
    url = "https://api.bniconnectglobal.com/member-api/v2/home?uuId={uuid}"

    # Authorization header with the token (replace with a dynamic token fetching logic if required)
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

# old code

# import requests
# import json
# # import scrapingScript
#
#
# def fetch_member_data(user_id, access_token):
#     """
#     Fetch member data for the given user_id from the BNI API.
#
#     Args:
#         user_id (str): The UUID of the user to fetch data for.
#
#     Returns:
#         dict: Parsed JSON data from the API response.
#     """
#     # Define the URL template
#     base_url = "https://api.bniconnectglobal.com/member-api/v2/home?uuId={}"
#     url = base_url.format(user_id)
#
#     # Authorization token from scrapingScript
#     authorization_token = "Bearer " + access_token
#
#     # Define headers
#     headers = {
#         "Authorization": authorization_token,
#     }
#
#     # Make a GET request
#     response = requests.get(url, headers=headers)
#
#     # Check for a successful response
#     if response.status_code == 200:
#         try:
#             # Parse the JSON data
#             response_data = response.json()
#             return response_data
#         except ValueError:
#             print("Error parsing JSON response.")
#             return None
#     else:
#         print(f"Request failed with status code: {response.status_code}")
#         return None
