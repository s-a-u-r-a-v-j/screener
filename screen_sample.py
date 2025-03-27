import streamlit as st
from fyers_apiv3 import fyersModel
import json
import os

# Load access token from file
access_token_file = "access_token.json"

if not os.path.exists(access_token_file):
    st.error("❌ Access token file not found! Please log in to Fyers first.")
else:
    with open(access_token_file, "r") as f:
        access_token = json.load(f)

    if not access_token:
        st.error("❌ Access token is empty! Please log in to Fyers first.")
    else:
        st.success("✅ Access token loaded successfully!")
        st.write(f"🔑 Access Token: {access_token}")

        # Initialize Fyers API
        fyers = fyersModel.FyersModel(client_id="your_api_key_here", token=access_token, log_path="")

        # Hardcoded stock symbols for testing
        stock_symbols = ["NSE:INFY", "NSE:TCS", "NSE:HDFCBANK", "NSE:RELIANCE", "NSE:ITC"]

        # Fetch real-time data
        st.title("📊 Live Stock Prices - Fyers API")
        if st.button("Fetch Live Prices"):
            try:
                data = fyers.quotes({'symbols': ",".join(stock_symbols)})
                if data["s"] == "ok":
                    results = data["d"]
                    table_data = []
                    for stock in results:
                        symbol = stock["n"]
                        price = stock["v"]["lp"]  # Last traded price
                        table_data.append([symbol, price])

                    # Display in Streamlit
                    st.table(table_data)
                else:
                    st.error("Error fetching data")
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")
