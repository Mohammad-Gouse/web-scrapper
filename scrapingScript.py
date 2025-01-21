from os import access


import json
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from datetime import datetime
import getPersonalDetails

load_dotenv()

username = os.getenv("BNI_USERNAME")
password = os.getenv("BNI_PASSWORD")
country = os.getenv("COUNTRY")
state = os.getenv("STATE")
city = os.getenv("CITY")
industry = os.getenv("INDUSTRY")
classification = os.getenv("CLASSIFICATION")


# API endpoint for authentication
url = "https://api.bniconnectglobal.com/auth-api/authenticate"

# Payload with credentials
payload = {
    "client_id": "IDENTITY_PORTAL",
    "user_id": username,  # Replace with your actual username
    "password": password  # Replace with your actual password
}

# Headers, assuming you need to provide authorization (e.g., a Bearer token)
headers = {
    'Authorization': 'Basic SURFTlRJVFlfUE9SVEFMOkdjVlN2JE1vODk1d0I2XjRTNA==',  # Replace <your_token_here> with actual token, if applicable
    'Content-Type': 'application/json'  # Make sure Content-Type is set to JSON
}

access_token = ''

# Send POST request with headers and payload
response = requests.post(url, json=payload, headers=headers)

# Check if authentication was successful
if response.status_code == 200:
    print("Authentication successful!")
    # Extract and print response data
    response_data = response.json()  # Assuming the response is in JSON format
    access_token = response_data["content"]["access_token"]
    # print(json.dumps(response_data["content"], indent=4))
    # print(json.dumps(response_data["metaData"], indent=4))
else:
    print(f"Failed to authenticate. HTTP Status Code: {response.status_code}")
    print(response.text)  # To see the actual error message

# user_id = "210e21b0-5fff-11e8-a2ac-0050568c2b4f"
# personalData = getPersonalDetails.fetch_member_data(user_id, access_token)
# if personalData:
#     print(json.dumps(personalData, indent=4))


# API endpoint for submitting the form data
url = "https://www.bniconnectglobal.com/web/secure/networkAddConnectionsJson"

# Headers for the POST request
headers = {
    'cookie': 'loggedOutStatus=false; logCurTime=1737035075643; OLDSESSIONID=B65DD4B69FA5009EB194C9B6F24B63EC; JSESSIONID=C297F9E6F869EF6BA6FA415977441F09; lastSelectedLandingMenuId=0',
}

# Form data for the POST request
form_data = {
    "searchMembers": "Search Members",
    "formSubmit": "true",
    "currentPage": "1",
    "perPage": "100",
    "memberKeywords": "",
    "memberFirstName": "",
    "memberLastName": "",
    "memberCompanyName": "",
    "memberIdCountry": country,
    "memberCity": city,
    "memberState": state,
    "memberPrimaryCategory": industry,
    "memberSecondaryCategory": classification
}

# Flag to control export format
export_as_csv = False  # Set to True for CSV, False for Excel

# Send POST request
response = requests.post(url, headers=headers, data=form_data)

# Initialize an empty list to store data
data_array = []

country_mapping = {
    "3857": "India",
    "10": "United_States"
}

# Classification mapping
classification_mapping = {
    "620160": "App_Developer",
    "621120": "Cloud_Services"
}

if response.status_code == 200:
    try:
        response_data = response.json()
        aa_data = response_data.get('aaData', [])
        soup = BeautifulSoup(aa_data[0], 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            # Extract relevant data
            link = row.find('a', class_='link')
            name = link.text.strip() if link else None
            user_id = None
            if link and link.has_attr('href'):
                # Extract userId from the 'href' attribute
                href = link['href']
                if "userId=" in href:
                    user_id = href.split("userId=")[-1]

            chapter = row.find_all('td')[2].text if len(row.find_all('td')) > 2 else None
            company = row.find_all('td')[3].text if len(row.find_all('td')) > 3 else None
            city = row.find_all('td')[4].text if len(row.find_all('td')) > 4 else None
            industry_full = row.find_all('td')[5].text.strip() if len(row.find_all('td')) > 5 else None

            # Split industry into two fields
            if industry_full and ">" in industry_full:
                industry, classification = map(str.strip, industry_full.split('>', 1))
            else:
                industry, classification = industry_full, None


            # phone_number = None
            # email_address = None
            # if personalData:
            #     phone_number = personalData["content"].get("phoneNumber", None)
            #     email_address = personalData["content"].get("emailAddress", None)

            # Append the parsed data
            data_array.append({
                'name': name,
                'userId': user_id,
                'chapter': chapter.strip() if chapter else None,
                'company': company.strip() if company else None,
                'city': city.strip() if city else None,
                'industry': industry,
                'classification': classification,
                # 'phoneNumber': phone_number,  # Add phoneNumber
                # 'emailAddress': email_address  # Add emailAddress
            })

        # Convert data_array to a DataFrame
        df = pd.DataFrame(data_array)

        # Generate dynamic file name
        now = datetime.now()
        timestamp = now.strftime("%Y_%b_%d_%H%M%S").upper()
        # Get country and classification names from mappings
        country = form_data["memberIdCountry"]
        classification = form_data["memberSecondaryCategory"]

        country_name = country_mapping.get(country, "UnknownCountry")
        classification_name = classification_mapping.get(classification, "UnknownClassification")

        # Generate the file name
        base_file_name = f"{timestamp}_{country_name}_{classification_name}"

        if export_as_csv:
            # Export as CSV
            file_path = f"output/csv/{base_file_name}.csv"
            df.to_csv(file_path, index=False)
            print(f"Data saved successfully to {file_path}")
        else:
            # Export as Excel
            file_path = f"output/xlsx/{base_file_name}.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.title = "Data Export"

            # Write DataFrame to Excel
            for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
                ws.append(row)

            # Adjust column widths based on the data
            for col in ws.columns:
                max_length = 0
                col_letter = col[0].column_letter  # Get column letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = max_length + 5  # Add padding
                ws.column_dimensions[col_letter].width = adjusted_width

            # Align the header cells
            for cell in ws[1]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.style = "Title"

            # Save the Excel workbook
            wb.save(file_path)
            print(f"Data saved successfully to {file_path}")

    except ValueError as e:
        print("Error parsing JSON:", e)
else:
    print(f"Request failed. HTTP Status Code: {response.status_code}")
    print(response.text)