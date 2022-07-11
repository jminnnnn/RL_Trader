from mysql_config import MY_SQL
import pandas as pd
import numpy as np
from keyword_extraction import *

class trainloader:

    def __init__(self):
        self.MYSQL_GOOGLE_TRENDS = 'keywords_google_trend_data'
        self.my_sql = MY_SQL
        self.PRICE_FEATURES ='stocks_us_new_features'


    def make_trainset(self):
        pass

    def _call_features_from_db(self):
        pass

    def _get_price_features(self):
        query = (
            f"SELECT * FROM {self.PRICE_FEATURES}"
        )
        df = pd.read_sql((query, self.my_sql))

        return df

    def _get_trend_features(self):
        query = (
            f"SELECT * FROM {self.TREND_FEATURES}"
        )
        df = pd.read_sql((query, self.my_sql))

        return df

    def _get_certain_stock_from_mysql(self, stock_symbol):

        query = (
            f"SELECT * FROM {self.MYSQL_TABLE} "
            f"WHERE symbol='{stock_symbol}'"
        )
        df = pd.read_sql(query, self.my_sql)

        return df