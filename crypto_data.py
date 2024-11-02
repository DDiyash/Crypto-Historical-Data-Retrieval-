import requests
import pandas as pd
from datetime import datetime

#Step 2

# Function to retrieve historical crypto data from Binance API
def fetch_crypto_data(crypto_pair, start_date):
    try:
        # Convert the start date to timestamp (in milliseconds)
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        
        # Format the crypto pair symbol for Binance (e.g., "BTC/USDT" -> "BTCUSDT")
        symbol = crypto_pair.replace("/", "")
        
        # Set up parameters for API call
        params = {
            "symbol": symbol,
            "interval": "1d",      # 1-day intervals for daily data
            "startTime": start_timestamp,
            "limit": 1000          # Maximum number of records per request
        }
        all_data = []

        # Loop to retrieve data in batches if needed
        while True:
            response = requests.get("https://api.binance.com/api/v3/klines", params=params)
            if response.status_code != 200:      # Error handling for failed requests
                print(f"Error: {response.status_code}")
                return None
            
            data = response.json()
            if not data:                         # Stop loop if no more data
                break
            
            all_data.extend(data)                # Add retrieved data to list
            params["startTime"] = data[-1][0] + 86400000  # Update start time for next batch

        # Create DataFrame with selected columns for relevant data
        df = pd.DataFrame(all_data, columns=[
            "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
            "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume",
            "Taker Buy Quote Asset Volume", "Ignore"
        ])
        
        # Select only relevant columns and rename 'Open Time' to 'Date'
        final_df = df.loc[:, ["Open Time", "Open", "High", "Low", "Close"]].copy()
        final_df.rename(columns={"Open Time": "Date"}, inplace=True)
        
        # Convert data to numeric and format 'Date' column to datetime
        final_df[["Open", "High", "Low", "Close"]] = final_df[["Open", "High", "Low", "Close"]].apply(pd.to_numeric, errors='coerce')
        final_df["Date"] = pd.to_datetime(final_df["Date"], unit='ms')
        
        return final_df
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to calculate metrics based on historical and future price data
def calculate_metrics(df, look_back, look_forward):
    # Sort DataFrame by date
    df = df.sort_values(by='Date')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Ensure numeric values for calculations
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')

    # Calculate metrics based on a look-back period (e.g., 7 days)
    df[f'High_Last_{look_back}_Days'] = df['Close'].rolling(window=look_back).max().bfill()
    df[f'%_Diff_From_High_Last_{look_back}_Days'] = ((df['Close'] - df[f'High_Last_{look_back}_Days']) / df[f'High_Last_{look_back}_Days']) * 100

    df[f'Low_Last_{look_back}_Days'] = df['Close'].rolling(window=look_back).min().bfill()
    df[f'%_Diff_From_Low_Last_{look_back}_Days'] = ((df['Close'] - df[f'Low_Last_{look_back}_Days']) / df[f'Low_Last_{look_back}_Days']) * 100
    
    # Calculate days since last high and low within the look-back period
    df['Days_Since_High'] = df['Date'].apply(lambda x: (x - df.loc[df[f'High_Last_{look_back}_Days'] == df['Close'], 'Date'].max()).days)
    df['Days_Since_Low'] = df['Date'].apply(lambda x: (x - df.loc[df[f'Low_Last_{look_back}_Days'] == df['Close'], 'Date'].max()).days)

    # Calculate metrics based on a look-forward period (e.g., next 5 days)
    for i in range(look_forward, len(df)):
        df.at[i, f'High_Next_{look_forward}_Days'] = df['Close'][i-look_forward:i].max()
        df.at[i, f'Low_Next_{look_forward}_Days'] = df['Close'][i-look_forward:i].min()

    # Fill forward-looking metrics and calculate % difference
    df[f'High_Next_{look_forward}_Days'] = df[f'High_Next_{look_forward}_Days'].bfill()
    df[f'Low_Next_{look_forward}_Days'] = df[f'Low_Next_{look_forward}_Days'].bfill()
    df[f'%_Diff_From_High_Next_{look_forward}_Days'] = ((df['Close'] - df[f'High_Next_{look_forward}_Days']) / df[f'High_Next_{look_forward}_Days']) * 100
    df[f'%_Diff_From_Low_Next_{look_forward}_Days'] = ((df['Close'] - df[f'Low_Next_{look_forward}_Days']) / df[f'Low_Next_{look_forward}_Days']) * 100

    return df

# Fetch and calculate metrics, then save to Excel if data retrieval is successful
crypto_data = fetch_crypto_data("BTC/USDT", "2024-01-01")
if crypto_data is not None:
    metrics_data = calculate_metrics(crypto_data, look_back=7, look_forward=5)
    print(metrics_data)
    metrics_data.to_excel("Output_crypto.xlsx", index=False)
else:
    print("Failed to fetch crypto data.")
