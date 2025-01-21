from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import scrapingScript
import json

# Initialize WebDriver options
options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start Chrome WebDriver
driver = webdriver.Chrome(options=options)

# Get the access token from scraping_auth
authorization_token = "Bearer " + scrapingScript.access_token  # Replace with the correct token from your auth module

# Enable CDP (Chrome DevTools Protocol)
driver.execute_cdp_cmd("Network.enable", {})

# Set the headers using Chrome DevTools Protocol
driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
    "headers": {
        "Authorization": authorization_token  # Add Authorization header here
    }
})

try:
    # Now, visit the URL which will use the Authorization token in headers
    driver.get("https://bniconnectglobal.com/web/secure/networkHome?userId=197637")

    # Wait for the page to load
    driver.implicitly_wait(10)

    # Capture the response to check if it has loaded properly
    body_content = driver.page_source

    # If page redirects to login or displays an error, check response
    if "login" in body_content.lower():  # Check if login page is shown
        print("Redirected to login page. Please check credentials or token.")
    else:
        print("Page loaded successfully")

    # Print page source for debugging or further scraping
    print("Page Content:", body_content)

except Exception as e:
    print("Error occurred:", e)

finally:
    driver.quit()
