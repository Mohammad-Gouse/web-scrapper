# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
#
#
# def get_page_response():
#     # Set up Selenium WebDriver with Chrome
#     chrome_options = Options()
#     # chrome_options.add_argument("--headless")  # Run without GUI
#     driver = webdriver.Chrome(options=chrome_options)  # Assuming Chromedriver is in PATH
#
#     try:
#         url = "https://www.sortlist.com/software-development"  # The target URL
#         driver.get(url)
#
#         # Allow some time for the page to load (or use WebDriverWait for precision)
#         driver.implicitly_wait(10)
#
#         # Retrieve the full page source
#         page_source = driver.page_source
#         return page_source
#
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return None
#
#     finally:
#         # Quit the WebDriver session
#         driver.quit()
#
#
# # Example Usage
# if __name__ == "__main__":
#     response = get_page_response()
#     if response:
#         print("\nEntire HTML Response Retrieved:\n", response)  # Truncate to avoid overload


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def get_page_response():
    # Set up Selenium WebDriver with Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment this to run without a GUI
    driver = webdriver.Chrome(options=chrome_options)  # Assumes Chromedriver is in PATH

    try:
        url = "https://www.sortlist.com/software-development"  # The target URL
        driver.get(url)

        # Allow some time for the page to load (or use WebDriverWait for precision)
        driver.implicitly_wait(10)

        # Retrieve the full page source
        page_source = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, "lxml")

        # Example: Find a specific element (for instance, an <h1> tag)
        # class ="text-secondary-900 layout-row gap-x-8 cursor-pointer"
        h1_element = soup.find("h1", class_="hero-title text-neutral-100 bold pt-xs-64")
        title = soup.find_all("a",class_="text-secondary-900 layout-row gap-x-8 cursor-pointer")
        if title:
            for item in title:
                print(item.text)
        if h1_element:
            print(f"H1 Text: {h1_element.text}")
        else:
            print("H1 tag not found")
        return page_source

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    finally:
        # Quit the WebDriver session
        driver.quit()


# Example Usage
if __name__ == "__main__":
    response = get_page_response()
    # if response:
        # print("\nEntire HTML Response Retrieved:\n", response)  # Truncate to avoid overload
