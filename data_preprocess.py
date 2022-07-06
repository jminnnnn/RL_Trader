import pandas as pd

from data_loader import Dataloader



class Preprocess:
    def __init__(self):
        self.total_data = None
        self.single_stock_data = None
        self.new_df = None

    def preprocess(self):
        self._get_total_data()
        self._get_certain_stock_data()


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

    def _get_certain_stock_data(self, stock_symbol):
        dataloader = Dataloader()
        # initialize first
        self.single_stock_data = None

        print('Calling {0} price data from DB...'.format(stock_symbol))
        df = dataloader._get_certain_stock_from_mysql(stock_symbol)
        self.single_stock_data = df

        if self.total_data.empty:
            print('Failed to call data from DB. pls check DB')
        else:
            print('Successfully called data from DB')

    def _create_new_df(self):
        columns = ['close_ma5','close_ma10', 'close_ma20', 'close_ma60','close_ma120',
                   'volume_ma5', 'volume_ma10', 'volume_ma20', 'volume_ma60', 'volume_ma120',
                   'open_close_ratio','high_close_ratio','low_close_ratio',
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

            self.new_df['close_ma%d_ratio' % window] = \
                (self.single_stock_data['adj_closing_price'] - self.new_df['close_ma{}'.format(window)])/self.new_df[
                    'close_ma{}'.format(window)]

            self.new_df['volume_ma%d_ratio' % window] = \
                (self.single_stock_data['trading_volume'] - self.new_df['volume_ma{}'.format(window)]) / self.new_df[
                    'volume_ma{}'.format(window)]

    def _create_price_ratios(self):
        'open_close_ratio', 'high_close_ratio', 'low_close_ratio',
        'close_last_close_ratio', 'volume_last_volume_ratio',
        self.new_df['open_close_ratio'] = (self.single_stock_data['opening_price'] -
                                           self.single_stock_data['adj_closing_price']) / \
                                          self.single_stock_data['adj_closing_price']
        self.new_df['high_close_ratio'] = (self.single_stock_data['highest_price'] -
                                           self.single_stock_data['adj_closing_price']) / \
                                          self.single_stock_data['adj_closing_price']
        self.new_df['low_close_ratio'] = (self.single_stock_data['lowest_price'] -
                                           self.single_stock_data['adj_closing_price']) / \
                                          self.single_stock_data['adj_closing_price']
