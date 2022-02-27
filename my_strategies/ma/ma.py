import pandas as pd
import backtrader as bt
import numpy as np
import math
import datetime

class MAStrategy(bt.Strategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
    ('price_period', 30)
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.buy_order = None
    self.sell_order = None
    self.trades = []
    self.dt = None
    self.buy_price = None
    self.from_date = datetime.date.today() - datetime.timedelta(1)

    # Add a MovingAverageSimple indicator
    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.highest = bt.indicators.Highest(self.data, period=self.params.price_period, subplot=False)
    self.isCrossUp = bt.indicators.CrossUp(self.ma1, self.ma2)

    data = pd.read_csv(f'./up_stat_week.csv', index_col='id', dtype={'id': np.character})
    self.stat = {
      'low': data.low['000001'],
      'middle': data.middle['000001'],
      'high': data.high['000001']
    }

  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return

    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        # self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
        #     (order.executed.price,
        #      order.executed.value,
        #      order.executed.comm))
        self.buy_price = order.executed.price
        self.buy_order = None
        pass
      else:  # Sell
        self.sell_order = None
        pass
        # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
        #          (order.executed.price,
        #           order.executed.value,
        #           order.executed.comm))
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')

  def notify_trade(self, trade):
    if not trade.isclosed:
      return

    self.trades.append(trade)
    self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
             (trade.pnl, trade.pnlcomm))

  def next(self):
    self.dt = self.data.datetime.date(0).isoformat()

    if self.data.datetime.date(0) < self.from_date:
      return

    if not self.position:
      if self.check_direction(self.ma2) > 0:
        if self.is_cross_up() and \
          self.data.close[0] >= self.highest[0] and \
          self.data.close[0] > self.data.open[0] and \
          self.get_percentage(self.data.close[0], self.data.open[0]) < self.stat['high'] and \
          self.get_percentage(self.data.close[-1], self.data.open[-1]) < self.stat['high'] and \
          self.get_percentage(self.data.close[-2], self.data.open[-2]) < self.stat['high']:
          # buy 1
          # self.log('BUY CREATE, %.2f, Find high price at: %s, %.2f' % (self.data.close[0], self.data.datetime.date(0 - i).isoformat(), self.data.close[0 - i]))
          self.log('BUY CREATE1, %.2f' % (self.data.close[0]))
          self.buy_order = self.buy()
        # elif self.ma1[0] >= self.ma2[0] and \
        #   self.data.close[0] > self.data.open[0] and \
        #   self.data.close[0] > self.ma2[0] and self.data.low < self.ma2[0] and self.data.high[0] > self.ma1[0]:
        #   # buy 2
        #   self.log('BUY CREATE2, %.2f' % (self.data.close[0]))
        #   self.buy_order = self.buy()
    else:
      if self.data.close[0] > self.buy_price * 2: # rise more then ..
        if self.data.close[0] >= self.ma1[0] * (1 + self.stat['high'] / 100): # rise too fast
          if self.data.close[0] < self.data.open[0] and \
            (self.get_percentage(self.data.close[-1], self.data.open[-1]) > self.stat['high'] or \
            (self.get_percentage(self.data.close[-1], self.data.open[-1]) > self.stat['middle'] and self.get_percentage(self.data.close[-2], self.data.open[-2]) > self.stat['middle']) or \
            (self.get_percentage(self.data.close[-1], self.data.open[-1]) < self.stat['low'] and self.get_percentage(self.data.close[-2], self.data.open[-2]) > self.stat['middle'] and self.get_percentage(self.data.close[-3], self.data.open[-3]) > self.stat['middle'])):
            # sell 1
            self.log('SELL CREATE1, %.2f' % self.data.close[0])
            self.sell_order = self.sell()
            self.buy_price = None
      elif self.is_dead_cross():
        # sell 2
        self.log('SELL CREATE2, %.2f' % self.data.close[0])
        self.sell_order = self.sell()
        self.buy_price = None

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #

  def is_cross_up(self):
    return self.isCrossUp[0] > 0 or self.isCrossUp[-1] > 0

  def get_percentage(self, val_h, val_l):
    return (val_h - val_l)/val_l * 100

  def is_golden_cross(self):
    return self.ma1[0] >= self.ma2[0] and self.ma1[-1] < self.ma2[-1]

  def is_dead_cross(self):
    return self.ma1[0] < self.ma2[0] and self.ma1[-1] > self.ma2[-1]

  def check_low_price(self):
    close = self.data.close[0]
    i = 0
    while self.data.datetime.date(0 - i) > self.startDate and self.data.close[0 - i] < close * self.params.price_times:
      i = i + 1

    if self.data.datetime.date(0 - i) > self.startDate:
      return True, i
    else:
      return False, 0
