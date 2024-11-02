import requests
from datetime import datetime

#Step 1

#To check the number of crypto pairs supported
#endpoint -> exchangeInfo
data = requests.get("https://api.binance.com/api/v3/exchangeInfo").json()
print(len(data['symbols']))

#To confirm that daily, hourly, and/or weekly timeframes are supported.
#endpoint -> klines
#Parameters
params = {
    "symbol": "BTCUSDT",  
    "interval": "1d",     # "1h" for hourly, "1w" for weekly
    "limit": 5            # Number of candlesticks to retrieve
}
response = requests.get("https://api.binance.com/api/v3/klines", params=params)
time_frame_data = response.json()
if response.status_code == 200:
    print(f"Data for {params['interval']} timeframe is available.")
    print(time_frame_data)
else:
    print("Error:", time_frame_data)

#To get the earliest available date and most recent date for data retrieval.
def data_retrieval(symbol,interval, start_time=None,limit=1):
    #Parameters
    params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    if start_time is not None:
        params['startTime'] = start_time
    response = requests.get("https://api.binance.com/api/v3/klines",params=params)
    retrieve = response.json()
    return retrieve

#For earliest date
earliest = data_retrieval("BTCUSDT","1d",start_time = 0)
earliest_timestamp = int(earliest[0][0])
earliest_date = datetime.fromtimestamp(earliest_timestamp / 1000)

#For latest date
latest = data_retrieval("BTCUSDT","1d")
latest_timestamp = int(latest[0][0])
latest_date = datetime.fromtimestamp(latest_timestamp / 1000)

print("Earliest Available Date:", earliest_date)
print("Most Recent Date:", latest_date)

#Difference
range_diff = latest_date - earliest_date
print(range_diff)
