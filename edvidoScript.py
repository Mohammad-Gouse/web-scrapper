import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment

def fetch_location():
    cities = [
        "abu-dhabi",
        "adelaide",
        "amsterdam",
        "athens",
        "atlanta",
        "austin",
        "bangkok",
        "barcelona",
        "bath",
        "beijing",
        "belgrade",
        "berlin",
        "birmingham",
        "boston",
        "bournemouth",
        "brighton",
        "brisbane",
        "bristol",
        "brussels",
        "budapest",
        "cairo",
        "calgary",
        "cambridge",
        "canberra",
        "cardiff",
        "charlotte",
        "chester",
        "chicago",
        "cincinnati",
        "cleveland",
        "columbus",
        "copenhagen",
        "dallas",
        "denver",
        "detroit",
        "dubai",
        "dublin",
        "edinburgh",
        "exeter",
        "glasgow",
        "halifax",
        "hamburg",
        "helsinki",
        "ho-chi-minh",
        "hong-kong",
        "houston",
        "islamabad",
        "istanbul",
        "kansas-city",
        "katowice",
        "kelowna",
        "krakow",
        "kuala-lumpur",
        "kuwait",
        "lancaster",
        "las-vegas",
        "leeds",
        "leicester",
        "lisbon",
        "liverpool",
        "london",
        "los-angeles",
        "madrid",
        "manchester",
        "manila",
        "melbourne",
        "miami",
        "milan",
        "minneapolis",
        "montreal",
        "mumbai",
        "munich",
        "nashville",
        "new-delhi",
        "new-jersey",
        "new-york",
        "newcastle",
        "northampton",
        "nottingham",
        "orlando",
        "oslo",
        "ottawa",
        "oxford",
        "paris",
        "perth",
        "philadelphia",
        "phoenix",
        "portland",
        "prague",
        "preston",
        "rotterdam",
        "sacramento",
        "san-diego",
        "san-francisco",
        "seattle",
        "seoul",
        "shanghai",
        "sheffield",
        "singapore",
        "sofia",
        "southampton",
        "stockholm",
        "sydney",
        "tel-aviv",
        "tokyo",
        "toronto",
        "tunisia",
        "turkiye",
        "vancouver",
        "vienna",
        "warsaw",
        "washington-dc",
        "winnipeg",
        "wroclaw",
        "zagreb",
        "zurich"
    ]
    return cities

def fetch_agency_data(url, endpoint):
    url += endpoint
    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the page content
        data_array = []
        soup = BeautifulSoup(response.content, 'html.parser')
        tbody = soup.find('tbody')
        tr = tbody.find_all('tr')
        for idx, row in enumerate(tr):
            agency = row.find_all('td')[0].text if len(row.find_all('td')) > 0 else None
            desc = row.find_all('td')[1].text if len(row.find_all('td')) > 1 else None
            people = row.find_all('td')[3].text if len(row.find_all('td')) > 3 else None
            location = row.find_all('td')[4].text if len(row.find_all('td')) > 4 else None
            website = row.find_all('td')[5].text if len(row.find_all('td')) > 5 else None
            data_array.append({
                "Agency": agency.strip(),
                "Description": desc.strip(),
                "People": people.strip(),
                "Location": location.strip(),
                "Website": website.strip()
            })
        return data_array
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
        return None

def save_data_to_file(data, base_file_name, export_as_csv=False):
    """Save data to CSV or Excel file."""

    df = pd.DataFrame(data)
    if export_as_csv:
        print("Generating CSV file.")
        file_path = f"output-edvido/csv/{base_file_name}.csv"
        df.to_csv(file_path, index=False)
    else:
        print("Generating Excel file.")
        file_path = f"output-edvido/xlsx/{base_file_name}.xlsx"
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



def generate_cities_excel():
    cities = fetch_location()

    for city in cities:
        # print(city)
        data = fetch_agency_data('https://www.edvido.com/software-companies/', city)
        if data:
            save_data_to_file(data, city,False)


def main():
    generate_cities_excel()

if __name__ == "__main__":
    main()

