import pandas as pd

from data_loader import Dataloader

dataloader = Dataloader()

class Preprocess:
    def __init__(self):
        self.total_data = None
        self.single_stock_data = None
        self.new_df = None

    def preprocess(self):
        self._get_total_data()


    def _get_total_data(self):
        #initialize First
        self.total_data = None

        print('Calling total data from DB...')
        df = dataloader._get_total_data_from_mysql_()
        self.total_data = df
        if self.total_data.empty:
            print('Failed to call data from DB. pls check DB')
        else:
            print('Successfully called data from DB')

    def _get_symbol_list(self):
        #call tickers for stocks
        pass

    def _get_certain_stock_data(self, stock_code):
        # initialize first
        self.single_stock_data = None

        print('Calling {0} price data from DB...'.format(stock_code))
        df = dataloader._get_certain_stock_from_mysql(stock_code)
        self.single_stock_data = df

        if self.total_data.empty:
            print('Failed to call data from DB. pls check DB')
        else:
            print('Successfully called data from DB')

    def _create_new_df(self):
        columns = ['per','pbr','roe','open_close_ratio','high_close_ratio','low_close_ratio',
                   'close_last_close_ratio', 'volume_last_volume_ratio',
                   'close_ma5_ratio','volume_ma5_ratio',
                   'close_ma10_ratio','volume_ma10_ratio',
                   'close_ma20_ratio','volume_ma20_ratio',
                   'close_ma60_ratio','volume_ma60_ratio',
                   'close_ma120_ratio','volume_ma120_ratio']
        self.new_df = pd.DataFrame(columns=columns)

    def _save_new_df_to_db(self):
        pass

    def _create_new_features(self):
        pass

    def _create_ma_ratios(self):
        windows = [5, 10, 20, 60, 120]
        for window in windows:
            self.new_df['close_ma{}'.format(window)] = self.single_stock_data['adj_closing_price'].mean()
            self.new_df['volume_ma{}'.format(window)] = self.single_stock_data['trading_volume'].mean()
