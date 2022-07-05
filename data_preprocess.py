from data_loader import Dataloader

dataloader = Dataloader()

class preprocess:
    def __init__(self):
        self.total_data = None
        self.single_stock_data = None

    def preprocess(self):
        self._get_total_data()
        print(self.total_data.head(3))

    def _get_total_data(self):
        df = dataloader._get_total_data_from_mysql_()

        self.total_data = df

    def _get_certain_stock_data(self, stock_code):
        df = dataloader._get_certain_stock_from_mysql(stock_code)
        self.single_stock_data = df

p = preprocess()
p.preprocess()