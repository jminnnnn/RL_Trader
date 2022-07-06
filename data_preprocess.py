import pandas as pd
import numpy as np
from data_loader import Dataloader
from mysql_config import DT_ENGINE, MY_SQL



class FeatureCreator:
    def __init__(self):
        self.total_data = None
        self.single_stock_data = None
        self.new_df = None
        self.columns = ['id', 'date', 'symbol', 'pair_id',
                   'close_ma5','close_ma10', 'close_ma20', 'close_ma60','close_ma120',
                   'volume_ma5', 'volume_ma10', 'volume_ma20', 'volume_ma60', 'volume_ma120',
                   'open_close_ratio','high_close_ratio','low_close_ratio',
                   'close_last_close_ratio', 'volume_last_volume_ratio',
                   'close_ma5_ratio','volume_ma5_ratio',
                   'close_ma10_ratio','volume_ma10_ratio',
                   'close_ma20_ratio','volume_ma20_ratio',
                   'close_ma60_ratio','volume_ma60_ratio',
                   'close_ma120_ratio','volume_ma120_ratio']
        self.final_df = None
        self.MYSQL_TABLE_NEW = 'stocks_us_new_features'
        self.my_sql = MY_SQL
        self.failed_list=[]

    #####################################   MAIN FUNCTION ######################################
    def create_features(self):
        # self._get_total_data()
        self.final_df = pd.DataFrame(columns=self.columns)
        ticker_list = self._read_snp_500_list()
        # ticker_list = ['ARKO', 'AAPL', 'AMZN','TSLA', '']
        for ticker in ticker_list:
            self._add_single_stock_data_to_final_df(ticker)
            print('succesfully added new data to self.final_df')
            print('-----'*50)
            print('\n')

        self._save_final_df_to_my_sql()
        print('THESE ARE THE TICKERS THAT HAD ERRORS...')
        print(self.failed_list)

    ###############################################################################################
    
    def _read_snp_500_list(self):
        f = open('snp500_list.txt', 'r', encoding='UTF-8')
        list = []
        for line in f:
            n = line.split(',')
            list.append(n[0])
        return list[1:]


    def _save_final_df_to_my_sql(self):
        self.final_df.to_sql(self.MYSQL_TABLE_NEW, self.my_sql, if_exists='append', index=False)

    def _add_single_stock_data_to_final_df(self, ticker):
        self.new_df = None
        self._create_new_single_stock_db(ticker)
        self.final_df = pd.concat([self.final_df, self.new_df], axis=0)

    def _get_total_data(self):
        dataloader = Dataloader()
        #initialize First
        self.total_data = None

        print('Calling total data from DB...')
        df = dataloader._get_total_data_from_mysql_()
        self.total_data = df
        if self.total_data.empty:
            print('Failed to call data from DB. pls check DB')
        else:
            print('Successfully called data from DB')


    def _get_certain_stock_data(self, stock_symbol):
        dataloader = Dataloader()
        # initialize first
        self.single_stock_data = None

        print('Calling {0} price data from DB...'.format(stock_symbol))
        df = dataloader._get_certain_stock_from_mysql(stock_symbol)
        self.single_stock_data = df

        if self.single_stock_data.empty:
            print('Failed to call data from DB. pls check DB')
        else:
            print('Successfully called data from DB')

    def _create_new_df(self):
        self.new_df = pd.DataFrame(columns=self.columns)
        self.new_df['id'] = self.single_stock_data['id']
        self.new_df['date'] = self.single_stock_data['date']
        self.new_df['symbol'] = self.single_stock_data['symbol']
        self.new_df['pair_id'] = self.single_stock_data['pair_id']


    def _create_new_single_stock_db(self, ticker):
        self._get_certain_stock_data(ticker)
        self._create_new_df()
        try:
            self._create_ma_ratios()
            self._create_price_ratios()
        except:
            print('Error getting data from {0}'.format(ticker))
            self.failed_list.append(ticker)
        # TODO!!
        #생성된 df는 new_df에 저장되며, 이는 결과적으로 final_df에 concat하여 만들어준다.

    def _create_ma_ratios(self):
        windows = [5, 10, 20, 60, 120]
        for window in windows:
            self.new_df['close_ma{}'.format(window)] = self.single_stock_data['adj_closing_price'].rolling(window).mean()
            self.new_df['volume_ma{}'.format(window)] = self.single_stock_data['trading_volume'].rolling(window).mean()

            self.new_df['close_ma%d_ratio' % window] = \
                (self.single_stock_data['adj_closing_price'] - self.new_df['close_ma{}'.format(window)])/self.new_df[
                    'close_ma{}'.format(window)]

            self.new_df['volume_ma%d_ratio' % window] = \
                (self.single_stock_data['trading_volume'] - self.new_df['volume_ma{}'.format(window)]) / self.new_df[
                    'volume_ma{}'.format(window)]

    def _create_price_ratios(self):
        # 'open_close_ratio', 'high_close_ratio', 'low_close_ratio',
        # 'close_last_close_ratio', 'volume_last_volume_ratio',
        self.new_df['open_close_ratio'] = (self.single_stock_data['opening_price'] -
                                           self.single_stock_data['adj_closing_price']) / \
                                          self.single_stock_data['adj_closing_price']
        self.new_df['high_close_ratio'] = (self.single_stock_data['highest_price'] -
                                           self.single_stock_data['adj_closing_price']) / \
                                          self.single_stock_data['adj_closing_price']
        self.new_df['low_close_ratio'] = (self.single_stock_data['lowest_price'] -
                                           self.single_stock_data['adj_closing_price']) / \
                                          self.single_stock_data['adj_closing_price']

        self.new_df['close_last_close_ratio'] = np.zeros(len(self.single_stock_data))

        self.new_df.loc[1:,'close_last_close_ratio'] = (self.single_stock_data['adj_closing_price'][1:].values -
                                          self.single_stock_data['adj_closing_price'][:-1].values) / \
                                         self.single_stock_data['adj_closing_price'][:-1].values

        self.new_df['volume_last_volume_ratio'] = np.zeros(len(self.single_stock_data))
        self.new_df.loc[1:, 'volume_last_volume_ratio'] = (self.single_stock_data['trading_volume'][1:].values -
                                                        self.single_stock_data['trading_volume'][:-1].values) / \
                                                       self.single_stock_data['trading_volume'][:-1]

pp = FeatureCreator()
pp.create_features()