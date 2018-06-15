import sys
import csv
from dotenv import load_dotenv
import json
import os
# import pdb
import requests
from datetime import datetime

def format_date(d):
    mon_day = d.day
    if mon_day < 4 or mon_day > 20:
        rem = mon_day % 10
        if rem == 1:
            mon_day = str(mon_day) + 'st'
        elif rem == 2:
            mon_day = str(mon_day) + 'nd'
        elif rem == 3:
            mon_day = str(mon_day) + 'rd'
        else:
            mon_day = str(mon_day) + 'th'
    else:
        mon_day = str(mon_day) + 'th'
    return d.strftime("%B " + mon_day + ", %Y")

def parse_response(response_text):

    # pdb.set_trace()
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": float(prices["1. open"]),
            "high": float(prices["2. high"]),
            "low": float(prices["3. low"]),
            "close": float(prices["4. close"]),
            "volume": int(prices["5. volume"])
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="db/prices.csv"):
    with open(filename, "w") as of:
        print("\t".join(["Date", "Open", "High", "Low", "Close", "Volume"]), file=of)
        for l in prices:
            print("\t".join([l["date"], str(l["open"]), str(l["high"]), str(l["low"]), str(l["close"]), str(l["volume"])]), file=of)






if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    load_dotenv('.env') # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."
    #print(api_key)
    # CAPTURE USER INPUTS (SYMBOL)



    symbols = input("Please input a stock symbols separated with commas (,) (e.g. 'NFLX'): ") # input("Please input a stock symbol (e.g. 'NFLX'): ")
    sym_list = []
    for s in symbols.split(','):
        s = s.strip()
        if s.isnumeric() or len(s) < 1 or len(s) > 5:
            print(s, "is incorrect symbol, check your stock symbol.")
            sys.exit(0)
        else:
            sym_list.append(s)

    ts = datetime.now()
    cur_time = ts.strftime("%I:%M%p ").lower() + format_date(ts)
    print("Run at:", cur_time)
    print("-----------------")

    for symbol in sym_list:

        # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS
        # ... todo

        # ASSEMBLE REQUEST URL
        # ... see: https://www.alphavantage.co/support/#api-key

        request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        # print(request_url)

        #print(request_url)
        # ISSUE "GET" REQUEST

        response = requests.get(request_url)


        # VALIDATE RESPONSE AND HANDLE ERRORS
        # ... todo

        # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)
        daily_prices = parse_response(response.text)
        print("Stock: ", symbol)
        last_date = format_date(datetime.strptime(daily_prices[0]["date"], "%Y-%m-%d"))
        print("Latest Data from:", last_date)

        print("Latest Closing: ${:,.2f}".format(daily_prices[0]["close"]))
        avg_low = sum([p["low"] for p in daily_prices]) / len(daily_prices)
        avg_high = sum([p["high"] for p in daily_prices]) / len(daily_prices)
        print("Recent Average High: ${:,.2f}".format(avg_high))
        print("RRecent Average Low: ${:,.2f}".format(avg_low))

        #June 4th, 2018
        #date_upper_range = datetime.strptime(max_date, "%Y-%m-%d")
        #date_lower_range = date_upper_range - timedelta(weeks=52)
        #print(request_url)
        #print(response.text)

        #print(daily_prices)

        # WRITE TO CSV

        write_prices_to_file(prices=daily_prices, filename=f"db/{symbol}.csv")

        # print(symbol, "Last close:", daily_prices[0]["close"], "Average Low:", low_avg, "Average high:", high_avg)

        if daily_prices[0]["close"] < 0.9 * avg_low:
            print(symbol, "Buy")
        elif daily_prices[0]["close"] > avg_high * 1.1:
            print(symbol, "Sell")
        else:
            print(symbol, "Don't buy")

        

        print("-------------")

