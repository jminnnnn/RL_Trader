
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
from mysql_config import DT_ENGINE, MY_SQL


class Dataloader:

    def __init__(self):
        self.data_df = None
        self.dt_sql = DT_ENGINE
        self.my_sql = MY_SQL

        self.today = None
        self._1y_from_today = None
        self._3y_from_today = None
        self._5y_from_today = None

    def update_database(self):
        print('Update starting..')

        #always start by updating time period
        years = 5
        self._define_time_period()
        self._load_price_from_dt(length=years)
        self._insert_data_to_mysql()

        print('Successfully updated data from DT')

    def _define_time_period(self):
        self.today = datetime.today()
        self._1y_from_today = self.today - timedelta(weeks=52)
        self._3y_from_today = self.today - timedelta(weeks=156)
        self._5y_from_today = self.today - timedelta(weeks=260)

    def _load_price_from_dt(self, length):
        DT_TABLE = 'stocks_us'
        if length == 1:
            start_date = self._1y_from_today
        elif length == 3:
            start_date = self._3y_from_today
        elif length == 5:
            start_date = self._5y_from_today

        start_date = self._make_date_to_str(start_date)
        today = self._make_date_to_str(self.today)

        query = (
            f"SELECT * FROM {DT_TABLE} "
            f"WHERE date BETWEEN '{start_date}' AND '{today}';"
        )

        df = pd.read_sql(query, self.dt_sql)
        self.data_df = df

    def _insert_data_to_mysql(self):
        MYSQL_TABLE = 'chart_data'
        self.data_df.to_sql(MYSQL_TABLE, self.my_sql, if_exists='append', index=False)

    def _make_date_to_str(self, date):
        str_date = date.strftime("%Y-%m-%d")
        return str_date



dl = Dataloader()
if __name__ == '__main__':
    dl.update_database()

