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
import pytz
import sys

ACCESS_TOKEN = ""
COOKIES = ""
excel_data = []

# Previous mappings remain the same
country_mapping = {
    '3857': "India",
    '10': "United_States",
    '8150': "United_Kingdom"
}

industry_mapping = {
    '62': "Computer_Programming"
}

classification_mapping = {
    '620160': "App_Developer",
    '621120': "Cloud_Services",
    '620350': "Computer_Retailer",
    '620355': "Computer_Software",
    '621806': "Computer_Training",
    '620400': "Data_Security",
    '621660': "Programmer",
    '629000': "Other"
}

def validate_integer(value, name):
    if not value or not value.isdigit():
        raise ValueError(f"{name} must be an integer number and is required.")

def load_credentials():
    """Load credentials from the config.env file."""
    load_dotenv("config.env")
    load_dotenv("auth.env", override=True)

    # Load and validate the credentials
    country = os.getenv("COUNTRY", "3857")
    if country not in country_mapping:
        raise ValueError(f"Invalid country code: {country}")

    industry = os.getenv("INDUSTRY", "62")
    if industry not in industry_mapping:
        raise ValueError(f"Invalid industry code: {industry}")

    classification = os.getenv("CLASSIFICATION", "620160")
    if classification not in classification_mapping:
        raise ValueError(f"Invalid classification code: {classification}")

    from_page = os.getenv("FROM_PAGE_NUMBER")
    validate_integer(from_page, "From page number")

    to_page = os.getenv("T0_PAGE_NUMBER")
    validate_integer(to_page, "To page number")

    page_size = os.getenv("PAGE_SIZE")
    validate_integer(page_size, "Page size")

    sleep_sec = os.getenv("SLEEP_IN_SECONDS",1)
    validate_integer(sleep_sec, "Sleeps seconds")

    if int(from_page) > int(to_page):
        raise ValueError(f"From page no. can't be greater than To page no.")

    if int(to_page) * int(page_size) > 10000:
        raise ValueError(f"Please select smaller page no.")

    return {
        "username": os.getenv("BNI_USERNAME"),
        "password": os.getenv("BNI_PASSWORD"),
        "country": country,
        "state": os.getenv("STATE", ""),
        "city": os.getenv("CITY", ""),
        "industry": industry,
        "classification": classification,
        "from_page": from_page,
        "to_page": to_page,
        "page_size": page_size,
        "csv": os.getenv("CSV"),
        "sleep": sleep_sec,
        "cookie": os.getenv("COOKIE")
    }


def fetch_all_pages(credentials, access_token):
    """Fetch data from all pages up to the target page number."""
    all_parsed_data = []
    form_data_template = {
        "searchMembers": "Search Members",
        "formSubmit": "true",
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
    from_page = credentials["from_page"]
    to_page = credentials["to_page"]
    for current_page in range(int(from_page), int(to_page) + 1):
        print(f"\nFetching page {current_page} of {to_page}")

        # Update the current page in form data
        form_data = form_data_template.copy()
        form_data["currentPage"] = current_page

        try:
            # Fetch data for current page
            page_data = fetch_member_data(form_data)
            if page_data:
                # Parse the page data
                parsed_page_data = parse_member_data(page_data, credentials['sleep'])

                if len(parsed_page_data) > 0:
                    all_parsed_data.extend(parsed_page_data)
                else:
                    print("Page records not found.")
                    break

                # Optional: Add a delay between pages to avoid overwhelming the server
                if current_page < int(to_page):
                    print(f"Waiting before fetching next page...")
                    time.sleep(1)  # 1 second delay between pages
            else:
                print("Users data not found.")
                break


        except Exception as e:
            print(f"Error fetching page {current_page}: {e}")
            continue  # Continue with next page even if current page fails

    return all_parsed_data

def authenticate(credentials):
    """Authenticate with the BNI API and return the access token."""
    print("Authenticating...")
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
        raise Exception(f"Authentication failed: Please check username or password.")


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
    if not "password" in response.text.lower():
        print("Users Fetched.")
        excel_data.append(response.json())
        return response.json()
    else:
        print(f"Data fetch failed: please update cookies")
        return None

def parse_member_data(data, sleep_sec):
    """Parse HTML content from fetched data to extract required details."""
    data_array = []
    aa_data = data.get('aaData', [])

    if aa_data:
        soup = BeautifulSoup(aa_data[0], 'html.parser')
        rows = soup.find_all('tr')

        for idx, row in enumerate(rows):
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
                    if uuid_location:
                        uuid = uuid_location.split("=")[1]
                        user_data = fetch_user_data(uuid)
                        phone = user_data.get('content', {}).get('phoneNumber', None)
                        mobile = user_data['content']['mobileNumber']
                        email = user_data['content']['emailAddress']
                        category = user_data['content']['primaryCategory']
                        secondaryCategory = user_data['content']['secondaryCategory']
                        website = user_data['content']['websiteUrl']
                        companyName = user_data['content']['companyName']
                        roleInfo = user_data['content']['roleInfo']
                        linkedIn = extract_linkedin_link(user_data['content']['networkLinks'])
                    else:
                        print("\nUUID not found.")
                        break

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
                'companyName': companyName,
                'city': city.strip() if city else None,
                'industry': industry,
                'classification': classification,
                'phone': phone,
                'mobile': mobile,
                'email': email,
                'website': website,
                'roleInfo': roleInfo,
                'linkedIn': linkedIn
            })

            # Show loading progress
            total_rows = len(rows)
            progress = int((idx + 1) / total_rows * 100)  # Calculate percentage progress
            sys.stdout.write(f"\rFetching personal details of all users... {progress}% complete")
            sys.stdout.flush()
            time.sleep(int(sleep_sec))

        print("\n")
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

def get_timeStamp():
    india_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(india_tz)
    return now

def main():
    credentials = load_credentials()
    try:
        # Authentication
        print(get_timeStamp())
        access_token = authenticate(credentials)
        if access_token:
            print("Authentication successful!")
        global ACCESS_TOKEN
        global COOKIES
        ACCESS_TOKEN = "Bearer " + access_token
        COOKIES = credentials["cookie"]

        # Fetch data from all pages
        all_data = fetch_all_pages(credentials, access_token)

        if all_data:
            # Generate timestamp and filename
            india_tz = pytz.timezone("Asia/Kolkata")
            now = datetime.now(india_tz)
            timestamp = now.strftime("%Y_%b_%d_%H%M%S").upper()
            base_file_name = f"{timestamp}_{country_mapping[credentials['country']]}_{classification_mapping[credentials['classification']]}"

            # Save all collected data
            isCSV = True if credentials['csv'] == '1' else False
            save_data_to_file(all_data, base_file_name, export_as_csv=isCSV)
            print(f"Total records collected: {len(all_data)}")
            print(get_timeStamp())

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()