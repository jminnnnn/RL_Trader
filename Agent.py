import numpy as np
import utils

class Agent:
    STATE_DIM =2 #Stock holding ratio, PV ratio
    TRADING_CHARGE = 0.00015
    TRADING_TAX = 0.0025

    #actions
    ACTION_BUY = 0
    ACTION_SELL = 1
    ACTION_HOLD = 2

    #actions to consider from neural net
    ACTIONS = [ACTION_BUY, ACTION_SELL]
    NUM_ACTIONS = len(ACTIONS)

    def __init__(self, environment, min_trading_unit = 1, max_trading_unit=2, delayed_reward_threshold=0.05):
        self.environment = environment

        #min, max trading unit and reward for delayed
        self.min_trading_unit = min_trading_unit
        self.max_trading_unit = max_trading_unit
        self.delayed_reward_threshold = delayed_reward_threshold

        #features of agent class
        #init bal shows investment amount
        self.initial_balance = 0
        self.balance = 0
        self.num_stocks = 0
        self.portfolio_value = 0 #will be balance + num_stocks * stock price
        self.base_portfolio_value = 0
        self.num_buy = 0
        self.num_sell = 0
        self.num_hold = 0
        self.immediate_reward = 0
        self.profitloss = 0
        self.base_profit_loss = 0
        self.exploration_base = 0

        self.ratio_hold = 0
        self.ratio_portfolio_value = 0

    def reset(self):
        self.balance = self.initial_balance
        self.num_stocks = 0
        self.portfolio_value = self.initial_balance
        self.base_portfolio_value = self.initial_balance
        self.num_buy = 0
        self.num_sell = 0
        self.num_hold = 0
        self.immediate_reward = 0
        self.ratio_hold = 0
        self.ratio_portfolio_value = 0

    def reset_exploration(self):
        self.exploration_base = 0.5 + np.random.rand() / 2

    def set_balance(self, balance):
        self.initial_balance = balance

    def get_states(self):
        #stock holding ratio & PV ratio
        self.ratio_hold = self._get_ratio_hold()
        self.ratio_portfolio_value = self._get_pv_ratio()
        return self.ratio_hold, self.ratio_portfolio_value

    def _get_ratio_hold(self):
        # ratio of number of stocks holding compared to total num of stocks holdable
        # if the ratio is too low, agetn will try to purchase more
        ratio = self.num_stocks / int(self.portfolio_value / self.environment.get_price())
        return ratio

    def _get_pv_ratio(self):
        #curren pv / base pv --> near 0 indicates loss and 1 indicates profit
        ratio = self.portfolio_value / self.base_portfolio_value
        return ratio

    def decide_action(self, pred_value, pred_policy, epsilon):
        confidence = 0

        pred = pred_policy
        if pred is None:
            pred = pred_value

        if pred is None:
            #if there is no pred val, then explore!
            epsilon = 1
        else:
            maxpred = np.max(pred)
            if (pred == maxpred).all():
                epsilon = 1

        #decide wheter to explore or not
        rand = np.random.rand()
        if rand < epsilon:
            exploration = True
            #if exp base claose to 1, will explore with buy
            # if  exp base close to 0, will explore with sell
            if rand < self.exploration_base:
                action = self.ACTION_BUY
            else:
                action = np.random.randint(self.NUM_ACTIONS - 1) + 1
        else:
            exploration = False
            action = np.argmax(pred)

        confidence = 0.5
        if pred_policy is not None:
            confidence = pred[action]
        elif pred_value is not None:
            confidence = utils.sigmoid(pred[action])

        return action, confidence, exploration

    #Check is action is doable
    def validate_action(self,action):
        if action == Agent.ACTION_BUY:
            if self.balance < self.environment.get_price() * (1 + self.TRADING_CHARGE) * self.min_trading_unit:
                return False
        #check if have any stocks in balance for selling
        elif action == Agent.ACTION_SELL:
            if self.num_stocks < 0:
                return False
        return True

    def decide_trading_unit(self, confidence):
        # buy more share if predicted with higher confidence score!
        if np.isnan(confidence):
            return self.min_trading_unit
        
        #(max-min)에 confi score을 곱한 것과, 곱하지 않은 것 중 min 값을 가져오고
        # 해당 min 값과 0 중에 max를 added으로 사용함

        added_trading = max(min(int(confidence * (self.max_trading_unit - self.min_trading_unit)),
                                self.max_trading_unit-self.min_trading_unit), 0)

        return self.min_trading_unit + added_trading

    def act(self, action, confidence):
        if not self.validate_action(action):
            action = Agent.ACTION_HOLD

        curr_price = self.environment.get_price()

        self.immediate_reward = 0

        if action == Agent.ACTION_BUY:
            self._action_buy(confidence, curr_price)
        if action == Agent.ACTION_SELL:
            self._action_sell(confidence, curr_price)
        if action ==Agent.ACTION_HOLD:
            self._action_hold()

        delayed_reward = self._update_pv()

        return self.immediate_reward, delayed_reward

    def _action_buy(self, confidence, curr_price):
        trading_unit = self.decide_trading_unit(confidence)
        balance = (
            self.balance - curr_price * (1 + self.TRADING_CHARGE) * trading_unit
        )
        if balance < 0:
            trading_unit = max(
                min(
                    int(self.balance / (curr_price * (1 + self.TRADING_CHARGE))),
                    self.max_trading_unit
                ),
                self.min_trading_unit
            )
        invest_amount = curr_price * (1 + self.TRADING_CHARGE) * trading_unit

        if invest_amount > 0:
            self.balance -= invest_amount
            self.num_stocks += trading_unit
            self.num_buy += 1

    def _action_sell(self, confidence, curr_price):
        trading_unit = self.decide_trading_unit(confidence)
        # check if amount holding is not enout for trading
        trading_unit = min(trading_unit, self.num_stocks)
        #sell
        invest_amount = curr_price * (1-(self.TRADING_TAX + self.TRADING_CHARGE)) * trading_unit

        if invest_amount > 0:
            self.balance += invest_amount
            self.num_stocks -= trading_unit
            self.num_sell += 1

    def _action_hold(self):
        self.num_hold += 1

    def _update_pv(self, curr_price):
        self.portfolio_value = self.balance + curr_price * self.num_stocks
        self.profitloss = ((self.portfolio_value - self.initial_balance)/self.initial_balance)

        self.immediate_reward = self.profitloss
        delayed_reward = 0

        self.base_profit_loss = (
            (self.portfolio_value - self.base_portfolio_value / self.base_portfolio_value)
        )

        if self.base_profit_loss > self.delayed_reward_threshold or self.base_profit_loss < -self.delayed_reward_threshold:
            #if reached target proift -> update pv or reached max loss
            self.base_portfolio_value = self.portfolio_value
            delayed_reward = self.immediate_reward
        else:
            delayed_reward = 0
        return delayed_reward

    