from tokenize import cookie_re

from dotenv import load_dotenv
import os

# Load environment variables from config.env file
load_dotenv()
load_dotenv("config.env")
load_dotenv("auth.env", override=True)

# Access them using os.getenv
username = os.getenv("BNI_USERNAME")
password = os.getenv("BNI_PASSWORD")
cookie = os.getenv("COOKIE")

print(f"Username: {username}, Password: {password}, Cookie: {cookie}")
