import alpaca_trade_api as tradeapi
from datetime import datetime,date
import requests
import json
import time

# alpaca trading login information
base_url = "https://paper-api.alpaca.markets"
alpaca_key_id = "PKK6709WT6GNND7XGUR4"
alpaca_secret_key = "ecS0gCN5qGlv0sGlbGN27zdPaueSgURdRVcekA5e"
api = tradeapi.REST(key_id=alpaca_key_id, secret_key=alpaca_secret_key,
                    base_url=base_url,api_version='v2')
tickers = ['MSFT', 'AAPL']#, 'GOOG', 'ADBE', 'AMZN', 'COST', 'DKNG', 'MRNA', 'TSLA', 'Z']


# DATA FUNCTIONS
# creates data, only used the first time the program is run
def create_data():
    for ticker in tickers:
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+ticker+"&outputsize=full&apikey=NG9C9EPVYBMQT0C8"
        req = requests.get(url)
        time.sleep(12)
        req_dct = json.loads(req.text)
        # creating keys to loop through the dictionary
        key1 = "Time Series (Daily)"
        key_date = "2022-12-01"
        keyO = "1. open"
        keyH = "2. high"
        keyL = "3. low"
        keyC = "4. close"
        # creating csv file
        stocks_csv = open("/home/ubuntu/environment/final_project/data/"+ ticker + ".csv", "w")
        stocks_csv.write("date, open, high, low, close\n")
        # creating new list called prices to append desired values in for loop
        prices = []
        for date in req_dct[key1]:
            prices.append(date + ", "+\
                req_dct[key1][date][keyO] +", "+\
                req_dct[key1][date][keyH] +", "+\
                req_dct[key1][date][keyL] +", "+\
                req_dct[key1][date][keyC] +"\n")
        prices.reverse()
        for price in prices:
            stocks_csv.write(price)
        stocks_csv.close()
        
        
# function to append data
def append_data():
    for ticker in tickers:
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+ticker+"&outputsize=full&apikey=NG9C9EPVYBMQT0C8"
        req = requests.get(url)
        time.sleep(12)
        req_dct = json.loads(req.text)
        # creating key to loop through the dictionary
        key1 = "Time Series (Daily)"
        key_date = "2021-11-26"
        keyO = "1. open"
        keyH = "2. high"
        keyL = "3. low"
        keyC = "4. close"
        stocks_csv = open("/home/ubuntu/environment/final_project/data/" + ticker + ".csv", "a")
        # opening the created file and reading the last line and splitting it to read only the date
        appended = open("/home/ubuntu/environment/final_project/data/" + ticker + ".csv")
        last_date = appended.readlines()[-1].split(',')[0]
        # create if statement to compare last date to current date
        prices = []
        for date in req_dct[key1]:
            if date > last_date:
                prices.append(date + ", " +\
                    req_dct[key1][date][keyO] + ", " +\
                    req_dct[key1][date][keyH] + ", " +\
                    req_dct[key1][date][keyL] + ", " +\
                    req_dct[key1][date][keyC] + "\n")
        prices.reverse()
        for price in prices:
            stocks_csv.write(price)
        stocks_csv.close()
        

# STRATEGIES
# defining function for the mean reversion strategy
def meanReversionStrategy(prices, ticker):
# creating variables needed to calculate buying, shorting, and profit
    count = 0
    buy = 0
    short = 0
    total_profit = 0
    MR_today = "Change me" # used to track what action to take today
    # for loop to loop through list of all prices then calculate moving average mean reversion
    for p in prices:
        if count >= 5:
            moving_average = (prices[count - 1] + prices[count - 2] + prices[count - 3] + prices[count - 4] + prices[count - 5]) / 5
            if p < moving_average * 0.95 and buy == 0: #if statement to calculate moving average
                buy = p  # setting buy equal to p, which is current price
                print("\tBuy at:", buy)
                MR_today = "Buy"
                # submitting a buy to alpaca
                # if dates[count] == str(date.today()):
                api.submit_order(symbol=ticker, qty=1, side='buy', type='market', time_in_force='day')
                if short != 0 and buy != 0:
                    total_profit += short - buy
                    print("\ttrade profit", round(short - buy, 2))
                    print("\ttrade profit", round(total_profit, 2))
                short = 0
            elif p > moving_average * 1.05 and short == 0:  # shorting portion of the if statement
                short = p
                print("\tShorting at:", p)
                MR_today = "Short"
                # submitting a short/sell to alpaca
                if dates[count] == str(date.today()):
                    api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="day")
                if short != 0 and buy != 0:
                    total_profit += short - buy # total profit is running total of all profits added up
                    print("\ttrade profit", round(short - buy, 2))
                    print("\ttrade profit", round(total_profit, 2))
                buy = 0 # resetting buy back to zero so if statement works properly
            else:
                MR_today = "Do Nothing"
        count += 1 # count of running total of days
    #calculate final profit percentage
    final_percentage = (total_profit / prices[0]) * 100
    print("\t---------------")
    print("\ttotal profit: ", round(total_profit, 2))
    print("\tfinal percentage: ", round(final_percentage, 2), "%")
    # printing what action to take today
    print("\t", MR_today, "today")
    print("\t----------------")
    return total_profit, final_percentage, MR_today
    
    
# defining function for the simple moving average strategy
def simpleMovingAverageStrategy(prices, ticker):
# creating variables needed to calculate buying, selling, and profit
    count = 0
    buy = 0
    total_profit = 0
    first_buy = 0
    SMA_today = "Change me" # used to track what action to take today
    # for loop to loop through list of all prices then calculate first buy
    for p in prices:
        if count >= 5:
            moving_average = (prices[count - 1] + prices[count - 2] + prices[count - 3] + prices[count - 4] + prices[count -5]) / 5
            #simple moving average logic
            if p > moving_average and buy == 0: #buy
                print("\tbuying at: ", p)
                buy = p
                SMA_today = "Buy"
                if dates[count] == str(date.today()):
                    api.submit_order(symbol=ticker, qty=1, side="buy", type="market", time_in_force="day")
                if first_buy == 0: # if statement to calculate first buy
                    first_buy = p
            elif p < moving_average and buy != 0: #sell
                print("\tselling at: ", p)
                print("\ttrade profit: ", round(p - buy, 2))
                total_profit += p - buy # total profit is running total of all profits added up
                buy = 0 # resetting buy back to zero so if statement works properly
                SMA_today = "Sell"
                if dates[count] == str(date.today()):
                    api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="day")
            else:
                SMA_today = "Do Nothing"
        count += 1 # count of running total of days
    # calculate final profit percentage
    final_percentage = (total_profit / first_buy) * 100
    print("\t---------------")
    print("\ttotal profit: ", round(total_profit, 2))
    print("\tfinal percentage: ", round(final_percentage, 2), "%", sep="")
    # printing what action to take today
    print("\t", SMA_today, "today")
    print("\t----------------")
    print()
    return total_profit, final_percentage, SMA_today



# defining function for the bollinger bands strategy
def bollingerBandsStrategy(prices, ticker):
    #creating variables needed to calculate buying, selling, and profit
    count = 0
    buy = 0
    total_profit = 0
    first_buy = 0
    BB_today = "Change me"
    #for loop to loop through list of all prices then calculate moving average
    for p in prices:
        if count >= 5:
            moving_average = (prices[count-1] + prices[count-2] + prices[count-3] + prices[count-4] + prices[count-5]) / 5
            #simple movin average is logic not mean
            if p > moving_average * 1.05 and buy == 0: #buy
                print('\tbuying at: ', p)
                buy = p
                BB_today = "Buy"
                #submitting a buy to alpaca
                if dates[count] == str(date.today()):
                    api.submit_order(symbol=ticker, qty=1, side='buy', type='market', time_in_force='day')
                if first_buy == 0: #if statement to calculate first buy
                    first_buy = p
            elif p < moving_average * .95 and buy != 0: #sell
                print('\tselling at: ', p)
                print('\ttrade profit: ', round(p - buy, 2))
                total_profit += p - buy #total profit is running total of all profits added up
                buy = 0 #resetting buy back to zero so if statement works properly
                BB_today = "Sell"
                #submitting a sell to alpaca
                if dates[count] == str(date.today()):
                    api.submit_order(symbol=ticker, qty=1, side='sell', type='market', time_in_force='day')
            else:
                BB_today = "Do nothing"
        count += 1 #count of running total of days
    #calculate final profit percentage
    final_percentage = (total_profit / first_buy) * 100
    print('\t--------')
    print("\tTotal Profit: ", round(total_profit, 2))
    print("\tFinal Percentage: ", round(final_percentage, 2), '%', sep='')
    #printing what action to take today
    print("\t", BB_today, "today")
    print('\t---------------------------')
    print()
    return total_profit, final_percentage, BB_today
    


#defining function to save results of both function calls
def saveResults(results):
    json.dump(results, open("/home/ubuntu/environment/final_project/results.json", "w"), indent=4)




#create_data(), uncomment if first time running code
append_data()
#main block of code to read csv files and implement all three strategies
results = {}
#for loop to read tickers and open files. Used to add profit and returns to dictionary
for ticker in tickers:
    fil = open("/home/ubuntu/environment/final_project/data/" + ticker + ".csv")
    #read lines from the second line on, skipping header
    lines = fil.readlines()[1:]
    #changing data type to float and splitting the lines to return only the closing price
    prices = [float(line.split(', ')[4]) for line in lines]
    #list of dates so code algorithms can determine if the last date in the csv matches today
    dates = [line.split(', ')[0] for line in lines]
    #creating headers and calling functions to run analysis
    print('')
    print(ticker)
    print("Mean Reversion")
    print('')
    m_profit, m_returns, m_today = meanReversionStrategy(prices,ticker)
    print('')
    print(ticker)
    print("Simple Moving Average")
    print('')
    s_profit, s_returns, s_today = simpleMovingAverageStrategy(prices,ticker)
    print('')
    print(ticker)
    print("Bollenger Bands")
    print('')
    b_profit, b_returns, b_today = bollingerBandsStrategy(prices,ticker)
    #creating key value pairs for dictionary that will be formatted in a json file
    results[ticker + "_SMA_profit"] = s_profit
    results[ticker + "_SMA_returns_%"] = s_returns
    results[ticker + "_SMA_today"] = s_today
    results[ticker + "_MR_profit"] = m_profit
    results[ticker + "_MR_returns_%"] = m_returns
    results[ticker + "_MR_today"] = m_today
    results[ticker + "_BB_profit"] = b_profit
    results[ticker + "_BB_returns_%"] = b_returns
    results[ticker + "_BB_today"] = b_today
#logic to determine which strategy and which stock had the highest return %
high_key = ""
high_returns = 0
for key in results:
    if "returns" in key:
        if results[key] > high_returns:
            high_key = key
            high_returns = results[key]
print("Highest Returns:", high_key, high_returns)
#including highest returning strategy and stock in json
results["Highest Returning Strategy"] = high_key, high_returns
saveResults(results)
print(api.get_account())
input("Press enter to end program")