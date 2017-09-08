import pandas as pd
from pandas_datareader import data
import matplotlib.pyplot as plt

def getStock(ticker = 'MSFT',start_date = '2000-01-01',end_date = '2016-12-31',data_source = 'yahoo'):

    # User pandas_reader.data.DataReader to load the desired data. As simple as that.
    panel_data = data.DataReader(ticker, data_source, start_date, end_date);
    
    # Getting all weekdays between 01/01/2000 and 12/31/2016
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B');
    
    # How do we align the existing prices in adj_close with our new set of dates?
    # All we need to do is reindex adj_close using all_weekdays as the new index
    panel_data = panel_data.reindex(all_weekdays);
    
    # Reindexing will insert missing values (NaN) for the dates that were not present
    # in the original set. To cope with this, we can fill the missing by replacing them
    # with the latest available price for each instrument.
    panel_data = panel_data.fillna(method='ffill');

    return panel_data
    
def get_mean_volume(symbol):
    """Return the mean volume for stock indicated by symbol.
    
    Note: Data for a stock is stored in file: data/<symbol>.csv
    """
    df = getStock(ticker = symbol)  # read in data
    # TODO: Compute and return the mean volume for this stock
    return df['Volume'].mean()

def plotStock(price = None, ticker = 'MSFT'):
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_axes([.15, .15, .7, .7])
    ax.plot(price.index, price, label = ticker)
    ax.set_xlabel('Date')
    ax.set_ylabel('price ($)')
    ax.legend()
    return fig
    
def test_run():
    """Function called by Test Run."""
    df = getStock("AAPL")
    # TODO: Print last 5 rows of the data frame
    df['Adj Close'].plot()
    #First 5 rows:
    print df.head()



if __name__ == "__main__":
    test_run()