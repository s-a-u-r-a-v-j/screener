import streamlit as st
from fyers_apiv3 import fyersModel
import os
import json
import re

# Load login credentials from Streamlit Secrets
login_credential = st.secrets["fyers"]

# Check if Access Token Exists
access_token_file = "access_token.json"
access_token = None

if os.path.exists(access_token_file):
    with open(access_token_file, "r") as f:
        access_token = json.load(f)

# Authenticate if no valid token
if not access_token:
    st.write("🔐 Logging in to Fyers...")
    try:
        session = fyersModel.SessionModel(
            client_id=login_credential["api_key"],
            secret_key=login_credential["api_secret"],
            redirect_uri=login_credential["redirect_url"],
            response_type="code",
            grant_type="authorization_code",
        )

        st.write("Login URL:", session.generate_authcode())

        # User enters the full URL received after login
        full_url = st.text_input("Paste the full redirected URL here:")
        
        # Extract authorization code from the URL
        auth_code_match = re.search(r"auth_code=([^&]+)", full_url)
        auth_code = auth_code_match.group(1) if auth_code_match else None

        if auth_code:
            st.success(f"✅ Extracted Authorization Code: {auth_code}")
        
        if st.button("Submit") and auth_code:
            session.set_token(auth_code)
            access_token = session.generate_token().get("access_token", None)

            if access_token:
                with open(access_token_file, "w") as f:
                    json.dump(access_token, f)
                st.success("✅ Logged in successfully!")
            else:
                st.error("❌ Failed to obtain access token.")

    except Exception as e:
        st.error(f"Login Failed: {e}")

st.write(f"**API Key:** {login_credential['api_key']}")
st.write(f"**Access Token:** {access_token}")
