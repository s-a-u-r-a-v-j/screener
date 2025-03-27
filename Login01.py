import os
import time
import json
import datetime
import sys
import re
from fyers_apiv3 import fyersModel

# Load login credentials
CREDENTIALS_FILE = "fyers_login_details.json"

if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "r") as f:
        login_credential = json.load(f)
else:
    print("---- Enter your Fyers Login Credentials ----")
    login_credential = {
        "api_key": str(input("Enter API Key : ").strip()),
        "api_secret": str(input("Enter API Secret : ").strip()),
        "redirect_url": str(input("Enter Redirect URL : ").strip()),
    }
    if input("Press Y to save login credentials and any key to bypass: ").upper() == "Y":
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(login_credential, f)
        print("'fyers_login_details.json' saved.")
    else:
        print("'fyers_login_details.json' not saved!")
        sys.exit()

# Path to store the access token
access_token_file = f"AccessToken/{datetime.datetime.now().date()}.json"
access_token = None

# Check if access token exists
if os.path.exists(access_token_file):
    with open(access_token_file, "r") as f:
        access_token = json.load(f)

    # Test if the token is still valid
    fyers = fyersModel.FyersModel(client_id=login_credential["api_key"], token=access_token, log_path="")
    response = fyers.get_profile()

    if response.get("s") == "ok":
        print("✅ Valid access token found, using existing login.")
    else:
        print("⚠️ Access token expired, re-authenticating...")
        access_token = None

# If no valid token, generate a new one
if not access_token:
    print("🔐 Logging in to Fyers...")
    
    # Generate Auth URL
    app_session = fyersModel.SessionModel(
        client_id=login_credential["api_key"],
        secret_key=login_credential["api_secret"],
        redirect_uri=login_credential["redirect_url"],
        response_type="code",
        grant_type="authorization_code",
    )
    
    login_url = app_session.generate_authcode()
    print(f"🔗 Login URL: {login_url}")
    
    # User pastes the redirected URL
    auth_url = input("Paste the full redirect URL here after logging in: ").strip()
    
    # Extract auth_code using regex
    match = re.search(r"auth_code=([^&]+)", auth_url)
    if match:
        auth_code = match.group(1)
        print(f"✅ Extracted Auth Code: {auth_code}")
    else:
        print("❌ Error: Auth Code not found in the URL!")
        sys.exit()

    try:
        # Exchange auth_code for access token
        app_session.set_token(auth_code)
        access_token = app_session.generate_token().get("access_token", None)

        if access_token:
            os.makedirs("AccessToken", exist_ok=True)
            with open(access_token_file, "w") as f:
                json.dump(access_token, f)
            print("✅ Access token saved.")

        else:
            print("❌ Failed to obtain access token.")
            sys.exit()

    except Exception as e:
        print(f"❌ Login Failed: {e}")
        sys.exit()

print(f"🔑 API Key: {login_credential['api_key']}")
print(f"🆔 Access Token: {access_token}")
