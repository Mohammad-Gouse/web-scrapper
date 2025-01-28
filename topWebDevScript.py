import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz

region_code_map = {
    'usa':'62a2fa4c402a5b380221ee33',
    'uk':'62a45bbb449a1f3821047f7e',
    'canada':'62a45bec449a1f3821047fab',
    'australia':'62a45c0d449a1f3821047fc8',
    'europe':'62a45c4d05f31f68b3bcf78c',
    'asia':'62a45c71402a5b380223472e',
    'mena':'62a45c95402a5b380223474d'
}

def fetch_uk_cities(country_code):
    url = f"https://api.jsonbin.io/v3/b/{country_code}"  # API URL

    try:
        response = requests.get(url)  # Make a GET request
        response.raise_for_status()  # Raise an error for bad HTTP status codes (4xx and 5xx)
        data = response.json()  # Parse response as JSON
        return data.get('record')  # Return the parsed JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None  # Return None in case of an error



def fetch_agency_data(url,country, city):
    url = url+country+'/'
    url = url+city
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the page content
        data_array = []
        soup = BeautifulSoup(response.content, 'html.parser')
        boxList = soup.find('div', class_='agency-horizontal-posts-grid w-dyn-items')
        if boxList:
            role_listitem = boxList.find_all('div', role='listitem')
            for item in role_listitem:
                company_name = item.find('div', class_='card-company-name').get_text(strip=True)
                website_link = item.find('a', string='Visit Website')['href']
                data_array.append({
                    "company": company_name.strip(),
                    "Website": website_link.strip(),
                    "city":city,
                    "country":country
                })
            return data_array
    else:
        return []



def save_data_to_file(data, base_file_name, export_as_csv=False):
    """Save data to CSV or Excel file."""

    df = pd.DataFrame(data)
    if export_as_csv:
        print("Generating CSV file.")
        file_path = f"output-topweb/csv/{base_file_name}.csv"
        df.to_csv(file_path, index=False)
    else:
        print("Generating Excel file.")
        file_path = f"output-topweb/xlsx/{base_file_name}.xlsx"
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



def main():
    data_array = []
    load_dotenv("topWebDevConfig.env")
    region = os.getenv("REGION")
    if region not in region_code_map:
        print("Invalid region")
        return
    csv = os.getenv("CSV")
    cities = fetch_uk_cities(region_code_map[region])
    for city in cities:
        # print(city.get('slug'))
        data = fetch_agency_data("https://topwebdevelopersnetwork.com/companies/", region, city.get('slug'))
        if data:
            data_array.extend(data)

    india_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(india_tz)
    timestamp = now.strftime("%Y_%b_%d_%H%M%S").upper()
    base_file_name = f"{timestamp}_{region}"
    isCSV = True if csv == '1' else False
    save_data_to_file(data_array, base_file_name, export_as_csv=isCSV)

if __name__ == "__main__":
    main()

