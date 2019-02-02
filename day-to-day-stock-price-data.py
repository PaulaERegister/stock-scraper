"""
A simple set of functions to scrape stock prices from a given URL within a specified timeframe and
download the stock price data for each symbol given. After this, the data is cleaned and individual
stocks can be viewed and plotted.

Source: Code modified from
    https://medium.com/@rohanjoseph_91119/stock-analysis-in-python-4e7b7884517a
"""
import pandas as pd
from datetime import date, timedelta
import requests
import csv
import quandl
import matplotlib.pyplot as plt

default_url = "https://www.nseindia.com/products/content/sec_bhavdata_full.csv"
api_key = "itSiso5s5gexytWVr4Aw"

def get_start_and_end_dates():
    """
    Get the start and end dates from the user. If the user enters 0, they have default fallback values.
        Start defaults to a month from the current day.
        End defaults to current day.
    :return: a datetime object in the format yyyy-mm-dd
    """
    input_start = input("Enter start date in yyyy/m/dd format. (Enter 0 to default to a month from today.)\n")
    input_end = input("Enter end date in yyyy/m/dd format: (Enter 0 to default to today.)\n")

    start_split = input_start.split("/")
    end_split = input_end.split("/")
    today = date.today().strftime("%Y-%m-%d")
    last_month = (date.today() - timedelta(31)).strftime("%Y-%m-%d")

    if len(start_split) == 1 and int(start_split[0]) == 0:
        start = last_month
    else:
        start = date(int(start_split[0]), int(start_split[1]), int(start_split[2]))
    if len(end_split) == 1 and int(end_split[0]) == 0:
        end = today
    else:
        end = date(int(end_split[0]), int(end_split[1]), int(end_split[2]))

    return start, end


def get_stocks():
    """
    Accepts a URL from user. Uses this URL to download a CSV file of stock symbols. If no URL is specified or an
    error is encountered, then it uses the default_url.
    :return: a dataframe containing the symbols of the stocks from the source URL
    """
    with requests.Session() as s:
        file = input("Type the URL of site to pull stocks from. If an error is encountered, "
                     "it will default to " + default_url + ".\n")
        try:
            download = s.get(file)
        except:
            download = s.get(default_url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(),delimiter=",")
        return pd.DataFrame(list(cr))


def clean_data(my_list):
    """
    Cleans up the data to prepare for adding stock data to analyze.
    :param my_list: A dataframe containing a list of information for stock symbols
    :return: A cleaned up list with the headers rewritten for clarity
    """
    new_header = my_list.iloc[0]
    my_list = my_list[1:]
    my_list = my_list.rename(columns=new_header)
    my_list['stock_name'] = "NSE/" + my_list["SYMBOL"]

    stock_list = my_list['stock_name'].tolist()
    stock_list = list(set(stock_list))

    view = input("View stock data?: (Y to view, enter to ignore)\n")
    if view.lower() == "y":
        print(stock_list)

    return stock_list


def scape_stock_prices(stock_list, stock_final, start, end, number_of_stocks):
    """
    Scrapes the stock prices from info available through quandl by looping through each of them and trying to add them
    to the dataframe. If an error is encountered, it skips over the stock and notifies the user.
    :param stock_list: A list of symbols from which to add stocks
    :param stock_final: The dataframe that the stock info is added to
    :param start: The starting date from which to pull info
    :param end: The ending date from which to pull info
    :param number_of_stocks: The number of stocks to add to stock_final
    :return:
        stock_final: a dataframe to which stock info has been added
    """
    for i in range(number_of_stocks):
        try:
            stock = quandl.get(stock_list[i], start_date=start, end_date=end,authtoken=api_key)
            stock['Name'] = stock_list[i]
            stock_final = pd.DataFrame.append(stock_final, stock)
        except:
            print("Error encountered with adding " + stock_list[i] + ". Skipping this value.")
    return stock_final


def view_stocks(stock_final):
    """
    A loop where the user can enter the name of the stock that they wish to view from the stocks generated previously.
    Prints the stock's info and plots it via matplotlib.
    :param stock_final: A dataframe of stock information
    :return: none
    """
    while True:
        stock_to_view = input("Enter a stock to view: (Ex: NSE/SUTLEJTEX). Enter 0 to exit. "
                              "Enter 1 to view available stocks.\n")
        if stock_to_view.isdigit():
            if int(stock_to_view) == 0:
                print("Exiting.")
                break
            if int(stock_to_view) == 1:
                print(stock_final)
        try:
            stock_view = stock_final[stock_final['Name'] == stock_to_view]
            print(stock_view)
            stock_view.plot(y="High")

            # Display chart
            plt.show()
        except:
            if stock_to_view.isdigit() and int(stock_to_view)!= 1:
                print("Encountered an error trying to view " + stock_to_view)


def main():
    """
    Requests input from user to look at stock's historical performance over a period of time.
    """
    start, end = get_start_and_end_dates()
    my_list = get_stocks()

    view = input("View first five stocks: Y to view, enter to ignore")
    if view.lower() == "y":
        print(my_list.head())

    # clean data up
    stock_list = clean_data(my_list)
    stock_final = pd.DataFrame()

    # Ask user for the number of stocks to add from the list. 0 defaults to all stocks
    number_of_stocks = int(input("Enter the number of stocks to add: (Enter 0 for all stocks)\n"))
    if number_of_stocks == 0:
        number_of_stocks = len(stock_list)
    print("Processing...")

    # Scrape the stock prices from quandl
    stock_final = scape_stock_prices(stock_list, stock_final, start, end, number_of_stocks)

    view = input("View all stocks?: Y to view, enter to ignore")
    if view.lower() == "y":
        print(stock_final)

    # Ask user for a particular stock to view and plot
    view_stocks(stock_final)


main()
