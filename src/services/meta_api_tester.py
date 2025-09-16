# src/services/meta_api_tester.py (NEW, SAFE TEST FILE)

import os
import requests
from dotenv import load_dotenv

# Load the environment variables we will set in Render
load_dotenv()

def run_test():
    """
    A simple, safe test to check if a Meta access token is valid.
    """
    print("--- Starting Meta API Connection Test ---")

    # 1. Get the User Access Token from environment variables
    user_access_token = os.getenv("META_USER_ACCESS_TOKEN")

    if not user_access_token:
        print("ERROR: META_USER_ACCESS_TOKEN is not set in your Render Environment Variables.")
        print("--- Test Finished ---")
        return

    print("Successfully found the access token.")

    # 2. Define the API endpoint to get basic profile info
    # This is a simple and safe endpoint to test the connection.
    url = f"https://graph.facebook.com/v18.0/me?fields=id,name&access_token={user_access_token}"

    print(f"Attempting to connect to URL: {url[:60]}..." ) # Print only the start of the URL for security

    try:
        # 3. Make the API request
        response = requests.get(url)
        response_data = response.json()

        # 4. Check the result
        if response.status_code == 200:
            print("\nSUCCESS! Connection to Meta API is working.")
            print("API Response:")
            print(response_data)
        else:
            print("\nERROR: Failed to connect to Meta API.")
            print(f"Status Code: {response.status_code}")
            print("API Error Response:")
            print(response_data)

    except Exception as e:
        print(f"\nCRITICAL ERROR: An exception occurred during the request: {e}")

    print("--- Test Finished ---")


# This allows the file to be run directly from the command line
if __name__ == "__main__":
    run_test()
