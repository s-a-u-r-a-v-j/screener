import streamlit as st
import os, json, datetime
from fyers_apiv3 import fyersModel

# Load or get Fyers login details
CREDENTIALS_FILE = "fyers_login_details.json"
ACCESS_TOKEN_FILE = f"AccessToken/{datetime.datetime.now().date()}.json"

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return None

def save_access_token(token):
    os.makedirs("AccessToken", exist_ok=True)
    with open(ACCESS_TOKEN_FILE, "w") as f:
        json.dump(token, f)

def get_access_token():
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def is_token_valid(token, api_key):
    fyers = fyersModel.FyersModel(client_id=api_key, token=token, log_path="")
    response = fyers.get_profile()
    return response.get("s") == "ok"

def authenticate_fyers():
    credentials = load_credentials()
    if not credentials:
        st.error("Fyers login credentials not found. Please add them to fyers_login_details.json.")
        return None
    
    access_token = get_access_token()
    if access_token and is_token_valid(access_token, credentials["api_key"]):
        return access_token
    
    st.warning("Your session has expired. Please log in again.")
    session = fyersModel.SessionModel(
        client_id=credentials["api_key"],
        secret_key=credentials["api_secret"],
        redirect_uri=credentials["redirect_url"],
        response_type="code",
        grant_type="authorization_code"
    )
    login_url = session.generate_authcode()
    st.write("[Click here to Login with Fyers]({})".format(login_url))
    
    auth_code = st.text_input("Enter Auth Code from Fyers Login Page:")
    if st.button("Submit Auth Code"):
        session.set_token(auth_code)
        access_token = session.generate_token().get("access_token")
        if access_token:
            save_access_token(access_token)
            st.success("Login successful! Please reload the app.")
            return access_token
        else:
            st.error("Failed to get access token. Try again.")
    return None

st.title("Stock Screener with Fyers API")
access_token = authenticate_fyers()

if access_token:
    st.success("Logged in successfully!")
    st.write("You can now use the stock screener.")
    # Placeholder for screener functionality
