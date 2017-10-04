import pandas as pd
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
import matplotlib.pyplot as plt
import os

def fill_missing_values(df):
    """Fill missing values in data frame, in place."""
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

class stocks(object):
    def __init__(self):
        self.cache = {}

    def get_data(self, symbol,start_date = '2000-01-01',end_date = '2017-09-08',data_source = 'yahoo'):
        """
        #usage example
        s = stocks()
        spydata = s.get_data('SPY')
        :param symbol: str
        :param start: datetime
        :param end: datetime
        :return: pandas.DataFrame
        """
        if symbol in self.cache:
            return self.cache[symbol]
        try:
            # User pandas_reader.data.DataReader to load the desired data. As simple as that.
            panel_data = data.DataReader(symbol, data_source, start_date, end_date);
            fill_missing_values(panel_data)
            self.cache[symbol] = panel_data
            return self.cache[symbol]
        except RemoteDataError:
            print('Failed when read {}'.format(symbol))
        return None

    def get_data_to_csv(self, symbol, start= '2000-01-01', end='2017-09-08'):
        """
        get data and store to csv
        :param symbol:
        :param start:
        :param end:
        :return:
        """
        data = self.get_data(symbol, start, end)
        if not data.empty:
            data.to_csv(self.symbol_to_path(symbol))
        return data

    def get_datas(self, symbols, dates):
        """
        Read stock data (adjusted close) for given symbols from CSV files.
        #usage example:
        allocations = {'SPY':0.4, 'XOM':0.4, 'MSFT':0.1, 'IBM':0.1}
        s = stocks()
        dates = pd.date_range('2012-01-01', '2012-12-20')
        df = s.get_datas(allocations.keys(), dates)
        :param symbols: list(str)
        :param dates: pandas.date_range
        :return: pandas.DataFrame
        """

        df = pd.DataFrame(index=dates)
        if 'SPY' not in symbols:  # add SPY for reference, if absent
            symbols.insert(0, 'SPY')

        for symbol in symbols:
            if not os.path.isfile(self.symbol_to_path(symbol)):
                self.get_data_to_csv(symbol, dates[0], dates[-1])
            df_temp = pd.read_csv(self.symbol_to_path(symbol), index_col='Date',
                    parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
            df_temp = df_temp.rename(columns={'Adj Close': symbol})
            df = df.join(df_temp)
            if symbol == 'SPY':  # drop dates SPY did not trade
                df = df.dropna(subset=["SPY"])
        return df


    def symbol_to_path(self, symbol, base_dir="data"):
        """Return CSV file path given ticker symbol."""
        return os.path.join(base_dir, "{}.csv".format(str(symbol)))


    def plot_data(self, df, title="Stock prices", ylabel="Price"):
        """Plot stock prices with a custom title and meaningful axis labels."""
        ax = df.plot(title=title, fontsize=12)
        ax.set_xlabel("Date")
        ax.set_ylabel(ylabel)
        plt.show()

    def is_cached(self, symbol):
        return symbol in self.cache

    def compute_daily_returns(self, df):
        """
        compute daily returns
        :param df:
        :return:
        """
        daily_returns = df.copy()
        daily_returns[1:] = (df[1:] / df[:-1].values) - 1
        daily_returns.ix[0, :] = 0 # set daily returns for row 0 to 0
        return daily_returns


