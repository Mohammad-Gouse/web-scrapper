# import requests
# from bs4 import BeautifulSoup
#
# # API endpoint for submitting the form data
# url = "https://www.bniconnectglobal.com/web/secure/networkAddConnectionsJson"
#
# # Headers to be included in the request (you provided these in the question)
# headers = {
#     'cookie': 'loggedOutStatus=false; logCurTime=1736949653584; JSESSIONID=DCC1A11B279E6863425375CE18B866E1; OLDSESSIONID=DCC1A11B279E6863425375CE18B866E1; lastSelectedLandingMenuId=0',
# }
#
# # Form data to be sent in the POST request (as provided in your example)
# form_data = {
#     "searchMembers": "Search Members",
#     "formSubmit": "true",
#     "currentPage": "1",
#     "perPage": "100",
#     "memberKeywords": "",
#     "memberFirstName": "",
#     "memberLastName": "",
#     "memberCompanyName": "",
#     "memberIdCountry": "3857",
#     "memberCity": "",
#     "memberState": "",
#     "memberPrimaryCategory": "62",
#     "memberSecondaryCategory": "620160"
# }
#
# # Send POST request with the headers and form data
# response = requests.post(url, headers=headers, data=form_data)
#
# # Initialize an empty list to store parsed data
# data = []
# data_array = []
#
# # Check if the request was successful
# if response.status_code == 200:
#     try:
#         response_data = response.json()
#         aa_data = response_data.get('aaData', [])
#         soup = BeautifulSoup(aa_data[0], 'html.parser')
#         rows = soup.find_all('tr')
#
#         for row in rows:
#             # Extract relevant data for each <tr>
#             name = row.find('a', class_='link').text if row.find('a', class_='link') else None
#             chapter = row.find_all('td')[2].text if len(row.find_all('td')) > 2 else None
#             company = row.find_all('td')[3].text if len(row.find_all('td')) > 3 else None
#             city = row.find_all('td')[4].text if len(row.find_all('td')) > 4 else None
#             industry = row.find_all('td')[5].text if len(row.find_all('td')) > 5 else None
#
#             # Append the data as an object to the array
#             data_array.append({
#                 'name': name.strip() if name else None,
#                 'chapter': chapter.strip() if chapter else None,
#                 'company': company.strip() if company else None,
#                 'city': city.strip() if company else None,
#                 'industry':industry.strip() if company else None,
#             })
#
#         # Output the array
#         # print(data_array)
#         for idx, entry in enumerate(data_array):
#             print(f"{idx}. Name: {entry['name']}, Company: {entry['company']}, City: {entry['city']}")
#
#
#     except ValueError as e:
#         print("Error parsing JSON:", e)
# else:
#     print(f"Request failed. HTTP Status Code: {response.status_code}")
#     print(response.text)  # To view any error or response message from the server


import requests
from bs4 import BeautifulSoup
import pandas as pd

# API endpoint for submitting the form data
url = "https://www.bniconnectglobal.com/web/secure/networkAddConnectionsJson"

# Headers to be included in the request (you provided these in the question)
headers = {
    'cookie': 'loggedOutStatus=false; logCurTime=1737021526523; JSESSIONID=2B3C1363CDD7EDE5051AE2EC28448016; OLDSESSIONID=2B3C1363CDD7EDE5051AE2EC28448016; lastSelectedLandingMenuId=0',
}

# Form data to be sent in the POST request (as provided in your example)
form_data = {
    "searchMembers": "Search Members",
    "formSubmit": "true",
    "currentPage": "1",
    "perPage": "100",
    "memberKeywords": "",
    "memberFirstName": "",
    "memberLastName": "",
    "memberCompanyName": "",
    "memberIdCountry": "3857",
    "memberCity": "",
    "memberState": "",
    "memberPrimaryCategory": "62",
    "memberSecondaryCategory": "620160"
}

# Send POST request with the headers and form data
response = requests.post(url, headers=headers, data=form_data)

# Initialize an empty list to store parsed data
data_array = []

# Check if the request was successful
if response.status_code == 200:
    try:
        response_data = response.json()
        aa_data = response_data.get('aaData', [])
        soup = BeautifulSoup(aa_data[0], 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            # Extract relevant data for each <tr>
            name = row.find('a', class_='link').text if row.find('a', class_='link') else None
            chapter = row.find_all('td')[2].text if len(row.find_all('td')) > 2 else None
            company = row.find_all('td')[3].text if len(row.find_all('td')) > 3 else None
            city = row.find_all('td')[4].text if len(row.find_all('td')) > 4 else None
            industry = row.find_all('td')[5].text if len(row.find_all('td')) > 5 else None

            # Append the data as an object to the array
            data_array.append({
                'name': name.strip() if name else None,
                'chapter': chapter.strip() if chapter else None,
                'company': company.strip() if company else None,
                'city': city.strip() if company else None,
                'industry': industry.strip() if company else None,
            })

        # Convert data_array into a DataFrame and save it to CSV
        df = pd.DataFrame(data_array)

        # Save the DataFrame to a CSV file
        csv_file_path = 'output_data.csv'
        df.to_csv(csv_file_path, index=False)

        print(f"Data saved successfully to {csv_file_path}")

    except ValueError as e:
        print("Error parsing JSON:", e)
else:
    print(f"Request failed. HTTP Status Code: {response.status_code}")
    print(response.text)  # To view any error or response message from the server
