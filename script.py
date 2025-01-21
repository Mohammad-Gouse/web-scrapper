import time
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from datetime import datetime

ACCESS_TOKEN = ""
COOKIES = ""

country_mapping = {
    '3857': "India",
    '10': "United_States"
}

# Classification mapping
classification_mapping = {
    '620160': "App_Developer",
    '621120': "Cloud_Services"
}

def load_credentials():
    """Load credentials from the config.env file."""
    load_dotenv("config.env")
    load_dotenv("auth.env", override=True)
    return {
        "username": os.getenv("BNI_USERNAME"),
        "password": os.getenv("BNI_PASSWORD"),
        "country": os.getenv("COUNTRY"),
        "state": os.getenv("STATE"),
        "city": os.getenv("CITY"),
        "industry": os.getenv("INDUSTRY"),
        "classification": os.getenv("CLASSIFICATION"),
        "page_no": int(os.getenv("PAGE_NUMBER", 1)) if os.getenv("PAGE_NUMBER", "").isdigit() else 1,
        "page_size": int(os.getenv("PAGE_SIZE", 10)) if os.getenv("PAGE_SIZE", "").isdigit() else 10,
        "csv":os.getenv("CSV"),
        "sleep": int(os.getenv("SLEEP_IN_SECONDS", 0)) if os.getenv("SLEEP_IN_SECONDS", "").isdigit() else 1,
        "cookie":os.getenv("COOKIE")
    }

def authenticate(credentials):
    """Authenticate with the BNI API and return the access token."""
    url = "https://api.bniconnectglobal.com/auth-api/authenticate"
    payload = {
        "client_id": "IDENTITY_PORTAL",
        "user_id": credentials["username"],
        "password": credentials["password"],
    }
    headers = {
        'Authorization': 'Basic SURFTlRJVFlfUE9SVEFMOkdjVlN2JE1vODk1d0I2XjRTNA==',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["content"]["access_token"]
    else:
        raise Exception(f"Authentication failed: {response.status_code} - {response.text}")


def parse_cookies(input_string):
    # Splitting the input string by semicolon
    cookie_pairs = input_string.split(';')

    # Initializing an empty dictionary to store parsed cookies
    cookies_dict = {}

    for pair in cookie_pairs:
        # Stripping extra spaces and splitting by '=' to separate key and value
        key, value = pair.strip().split('=')

        # Adding the key-value pair to the dictionary
        cookies_dict[key] = value

    return cookies_dict


def extract_linkedin_link(data):
    # Try to get the LinkedIn URL by first checking for the key 'linkedin'
    linkedin_link = data.get('network.connections.connectiondetails.linkedin', None)

    # If the 'orkut' key doesn't exist, check for the 'orkut' key
    if linkedin_link is None:
        linkedin_link = data.get('network.connections.connectiondetails.orkut', None)

    # Return the LinkedIn link if found, otherwise None
    return linkedin_link

def fetch_member_data(form_data):
    """Fetch member data using the POST API request."""

    print("Fetching Users...")
    url = "https://www.bniconnectglobal.com/web/secure/networkAddConnectionsJson"
    headers = {
        'cookie': COOKIES
    }

    response = requests.post(url, headers=headers, data=form_data)
    if response.status_code == 200:
        print("Users Fetched.")
        return response.json()
    else:
        raise Exception(f"Data fetch failed: {response.status_code} - {response.text}")

def parse_member_data(data, sleep_sec):
    """Parse HTML content from fetched data to extract required details."""
    data_array = []
    aa_data = data.get('aaData', [])

    if aa_data:
        print("Processing....")
        soup = BeautifulSoup(aa_data[0], 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            link = row.find('a', class_='link')
            name = link.text.strip() if link else None
            user_id = None
            phone = None
            mobile = None
            email = None
            category = None
            secondaryCategory = None
            roleInfo = None
            website = None
            companyName = None
            linkedIn = None
            if link and link.has_attr('href'):
                href = link['href']
                if "userId=" in href:
                    user_id = href.split("userId=")[-1]
                    uuid_location = fetch_redirect_location(user_id)
                    uuid = uuid_location.split("=")[1]
                    user_data = fetch_user_data(uuid)
                    phone = user_data['content']['phoneNumber']
                    mobile = user_data['content']['mobileNumber']
                    email = user_data['content']['emailAddress']
                    category = user_data['content']['primaryCategory']
                    secondaryCategory = user_data['content']['secondaryCategory']
                    website =  user_data['content']['websiteUrl']
                    companyName =  user_data['content']['companyName']
                    roleInfo = user_data['content']['roleInfo']
                    linkedIn = extract_linkedin_link(user_data['content']['networkLinks'])


            chapter = row.find_all('td')[2].text if len(row.find_all('td')) > 2 else None
            company = row.find_all('td')[3].text if len(row.find_all('td')) > 3 else None
            city = row.find_all('td')[4].text if len(row.find_all('td')) > 4 else None
            industry_full = row.find_all('td')[5].text.strip() if len(row.find_all('td')) > 5 else None

            if industry_full and ">" in industry_full:
                industry, classification = map(str.strip, industry_full.split('>', 1))
            else:
                industry, classification = industry_full, None

            data_array.append({
                'name': name,
                'userId': user_id,
                'chapter': chapter.strip() if chapter else None,
                # 'company': company.strip() if company else None,
                'companyName': companyName,
                'city': city.strip() if city else None,
                'industry': industry,
                'classification': classification,
                'phone':phone,
                'mobile':mobile,
                'email':email,
                'website':website,
                'roleInfo':roleInfo,
                'linkedIn': linkedIn
            })
            time.sleep(int(sleep_sec))
    print("Process Done")
    return data_array

def save_data_to_file(data, base_file_name, export_as_csv=False):
    """Save data to CSV or Excel file."""

    df = pd.DataFrame(data)
    if export_as_csv:
        print("Generating CSV file.")
        file_path = f"output/csv/{base_file_name}.csv"
        df.to_csv(file_path, index=False)
    else:
        print("Generating Excel file.")
        file_path = f"output/xlsx/{base_file_name}.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Data Export"

        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
            ws.append(row)

        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 5

        for cell in ws[1]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.style = "Title"

        wb.save(file_path)

    print(f"Data saved successfully to {file_path}")


def fetch_redirect_location(user_id):
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
    url = f"https://www.bniconnectglobal.com/web/secure/networkHome?userId={user_id}"
    # Create a session to manage cookies
    session = requests.Session()

    # Set up session headers with Authorization token
    session.headers.update({
        "Authorization": ACCESS_TOKEN
    })


    # Update the session's cookies
    session.cookies.update(parse_cookies(COOKIES))


    # Make a GET request through the session
    response = session.get(url, allow_redirects=False)

    if 'Location' in response.headers:
        location_url = response.headers['Location']
        return location_url
    else:
        print("No Location Header Found.")
        return None

def fetch_user_data(uuid):
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
        "Authorization": ACCESS_TOKEN
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers)

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



def main():
    credentials = load_credentials()
    try:
        access_token = authenticate(credentials)
        if access_token:
            print("Authentication successful!")
        global ACCESS_TOKEN
        global COOKIES
        ACCESS_TOKEN = "Bearer"+" "+access_token
        COOKIES = credentials["cookie"]
        print()

        form_data = {
            "searchMembers": "Search Members",
            "formSubmit": "true",
            "currentPage": credentials["page_no"],
            "perPage": credentials["page_size"],
            "memberKeywords": "",
            "memberFirstName": "",
            "memberLastName": "",
            "memberCompanyName": "",
            "memberIdCountry": credentials["country"],
            "memberCity": credentials["city"],
            "memberState": credentials["state"],
            "memberPrimaryCategory": credentials["industry"],
            "memberSecondaryCategory": credentials["classification"]
        }

        data = fetch_member_data(form_data)
        parsed_data = parse_member_data(data, credentials['sleep'])
        now = datetime.now()
        timestamp = now.strftime("%Y_%b_%d_%H%M%S").upper()
        base_file_name = f"{timestamp}_{country_mapping[credentials['country']]}_{classification_mapping[credentials['classification']]}"
        isCSV = True if credentials['csv'] == '1' else False
        save_data_to_file(parsed_data, base_file_name, export_as_csv=isCSV)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
