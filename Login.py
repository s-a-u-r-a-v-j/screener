import os
import json
import datetime
import re
import streamlit as st
from fyers_apiv3 import fyersModel

# Define file paths
CREDENTIALS_FILE = "fyers_login_details.json"
access_token_file = f"AccessToken/{datetime.datetime.now().date()}.json"

# Streamlit UI Setup
st.title("🔐 Fyers API Login")
st.sidebar.header("Login Details")

# Load credentials if they exist, else initialize empty
login_credential = {}
if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "r") as f:
        login_credential = json.load(f)

# Ensure required keys are present
if not login_credential.get("api_key") or not login_credential.get("api_secret") or not login_credential.get("redirect_url"):
    st.sidebar.warning("⚠️ Fyers login details missing!")
    api_key = st.sidebar.text_input("API Key")
    api_secret = st.sidebar.text_input("API Secret", type="password")
    redirect_url = st.sidebar.text_input("Redirect URL")

    if st.sidebar.button("Save Credentials"):
        login_credential = {
            "api_key": api_key.strip(),
            "api_secret": api_secret.strip(),
            "redirect_url": redirect_url.strip(),
        }
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(login_credential, f)
        st.sidebar.success("✅ Credentials saved! Restart app.")
        st.stop()

# Ensure login credentials are now available
if not login_credential:
    st.error("❌ Login credentials not found. Please enter them in the sidebar.")
    st.stop()

# Generate login URL
st.subheader("🔗 Step 1: Login to Fyers")
app_session = fyersModel.SessionModel(
    client_id=login_credential["api_key"],
    secret_key=login_credential["api_secret"],
    redirect_uri=login_credential["redirect_url"],
    response_type="code",
    grant_type="authorization_code",
)

login_url = app_session.generate_authcode()
st.write(f"➡️ Click to Login: [Login to Fyers]({login_url})")

# User pastes the redirect URL
st.subheader("🔑 Step 2: Enter Redirected URL")
auth_url = st.text_area("Paste the full redirected URL here:")

if st.button("Get Access Token"):
    match = re.search(r"auth_code=([^&]+)", auth_url)
    if match:
        auth_code = match.group(1)
        st.success(f"✅ Extracted Auth Code: `{auth_code}`")

        try:
            app_session.set_token(auth_code)
            access_token = app_session.generate_token().get("access_token", None)

            if access_token:
                os.makedirs("AccessToken", exist_ok=True)
                with open(access_token_file, "w") as f:
                    json.dump(access_token, f)
                st.success("✅ Access token saved successfully!")
                st.write(f"🔑 **Access Token:** {access_token}")

            else:
                st.error("❌ Failed to get access token. Check API credentials.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    else:
        st.error("❌ Invalid URL! Make sure you copied the full redirected URL.")
