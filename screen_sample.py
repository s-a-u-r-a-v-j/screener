import streamlit as st
from fyers_apiv3 import fyersModel
import json
import os

# File where the access token is stored
access_token_file = "access_token.json"

# Check if access token file exists
if not os.path.exists(access_token_file):
    st.error("❌ Access token file NOT found! Please log in using `Login.py` first.")
    st.stop()

# Load the access token
with open(access_token_file, "r") as f:
    access_token = json.load(f)

if not access_token:
    st.error("❌ Access token is empty! Please re-run `Login.py`.")
    st.stop()

# Initialize Fyers API
fyers = fyersModel.FyersModel(client_id="your_api_key_here", token=access_token, log_path="")

# Hardcoded stock symbols for testing
stock_symbols = ["NSE:INFY", "NSE:TCS", "NSE:HDFCBANK", "NSE:RELIANCE", "NSE:ITC"]

# Streamlit UI
st.title("📊 Live Stock Prices - Fyers API")

if st.button("Fetch Live Prices"):
    try:
        data = fyers.quotes({'symbols': ",".join(stock_symbols)})
        
        if data.get("s") == "ok":
            results = data["d"]
            table_data = [[stock["n"], stock["v"]["lp"]] for stock in results]  # Extract symbol & price
            
            # Display in Streamlit
            st.table(table_data)
        else:
            st.error("❌ Error fetching data from Fyers API.")
    
    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")
