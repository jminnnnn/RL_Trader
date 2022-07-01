

class Environment:
    PRICE_IDX = 4

    def __init__(self, chart_data=None):

        # chart_data is a 2D df containing dates & OHLCV PRICES
        self.chart_data = chart_data
        self.observation = None
        self.idx = -1

    #initialize idx and observation
    def reset(self):
        self.observation = None
        self.idx = -1

    #move idx to next place and update observation results
    def observe(self):
        if len(self.chart_data) > self.idx + 1:
            # above condition indicates that there is data to load from next index(date)
            self.idx += 1
            # read idx'th row from chart_data
            self.observation = self.chart_data.iloc[self.idx]
            return self.observation
        return None

    # get CLOSE price from the current observation (OHLCV prices from today idx's chart_data
    def get_price(self):
        if self.observation is not None:
            return self.observation[self.PRICE_IDX]
        return None

    def set_chart_data(self, chart_data):
        self.chart_data = chart_data

