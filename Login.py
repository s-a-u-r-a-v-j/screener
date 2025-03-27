import streamlit as st
from fyers_apiv3 import fyersModel
import json
import os

# Define the access token file path
access_token_file = "access_token.json"

# Load login credentials from Streamlit Secrets
login_credential = st.secrets["fyers"]

st.title("🔐 Fyers API Login")

# Check if Access Token Already Exists
if os.path.exists(access_token_file):
    with open(access_token_file, "r") as f:
        access_token = json.load(f)
    st.success("✅ Access token already exists!")
    st.write(f"📄 Access token is stored at: `{os.path.abspath(access_token_file)}`")
else:
    st.warning("❌ No access token found. Please log in.")

    try:
        # Create session
        session = fyersModel.SessionModel(
            client_id=login_credential["api_key"],
            secret_key=login_credential["api_secret"],
            redirect_uri=login_credential["redirect_url"],
            response_type="code",
            grant_type="authorization_code",
        )

        # Generate and display login URL
        login_url = session.generate_authcode()
        st.write("🔗 **Login URL:**", login_url)

        # Get Authorization Code from User
        auth_url = st.text_input("Paste the full redirected URL here:")
        
        if st.button("Submit"):
            if "auth_code=" in auth_url:
                auth_code = auth_url.split("auth_code=")[1].split("&")[0]
                st.write(f"✅ Extracted Authorization Code: `{auth_code}`")

                # Exchange Auth Code for Access Token
                session.set_token(auth_code)
                token_response = session.generate_token()
                
                if "access_token" in token_response:
                    access_token = token_response["access_token"]
                    
                    # Save the access token to a file
                    with open(access_token_file, "w") as f:
                        json.dump(access_token, f)
                    
                    st.success("✅ Logged in successfully!")
                    st.write(f"📄 Access token saved at: `{os.path.abspath(access_token_file)}`")
                else:
                    st.error("❌ Failed to obtain access token. Check credentials and try again.")
            else:
                st.error("❌ Invalid URL. Please enter the full redirected URL after login.")

    except Exception as e:
        st.error(f"⚠️ Login Failed: {e}")

# Show API Key (for verification)
st.write(f"🔑 **API Key:** {login_credential['api_key']}")
