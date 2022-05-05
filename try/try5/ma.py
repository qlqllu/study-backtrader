from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np

class MAStrategy(bt.Strategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.dt = None
    self.sl = 0
    self.ma2_direction = 0
    self.buy_price = 0
    self.trades = []
    self.is_rising = None
    self.sell_dt = None
    self.trade_init_value = 0

    # Add a MovingAverageSimple indicator
    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)

  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return

    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        self.buy_price = order.executed.price
        # self.log(f'BUY EXECUTED, Price: {order.executed.price}, {order.executed.size}')
        pass
      else:  # Sell
        self.order = None
        # self.log(f'SELL EXECUTED, Price: {order.executed.price}, {order.executed.size}')
        pass
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')
      self.order = None

  def notify_trade(self, trade):
    if not trade.isclosed:
      self.trade_init_value = int(trade.price * trade.size)
      return

    p = round(trade.pnlcomm / self.trade_init_value * 100, 2)

    trade.profit_percent = p

    self.trades.append(trade)
    self.log(f'Trade, Init: {self.trade_init_value}, Profit: {int(trade.pnlcomm)}, Percent: {p}')


  def next(self):
    d = self.data

    self.dt = d.datetime.date(0).isoformat()
    self.ma2_direction = self.check_direction(self.ma2)

    # Move SL
    if not self.is_rising and \
      d.low[0] > d.low[-1] > d.low[-2]:
      self.sl = d.low[-2]
      self.is_rising = True
    else:
      self.is_rising = False

    if d.low[0] > self.sl * 1.5:
      self.sl = d.low[0]

    if not self.position:
      if self.ma2_direction > 0 and \
        d.close[0] > d.open[0] and \
        d.low[0] > self.ma2[0] and d.low[-1] > self.ma2[0] and \
        d.low[0] > d.low[-1]:
        if not self.sell_dt or (self.sell_dt and d.datetime.date(-2) > self.sell_dt):
          self.buy()
          self.sl = d.low[-1]
          self.log('++Buy 1, %.2f' % d.close[0])
    else:
      if d.close[0] < self.ma2[0] or \
        d.close[0] < self.sl:
        self.sell()
        self.sell_dt = d.datetime.date(0)
        self.log('--Sell 2, %.2f' % d.close[0])

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3] > line[-4]:
      return 1 # up
    elif line[0] < line[-1] < line[-2] < line[-3] < line[-4]:
      return -1 # down
    else:
      return 0 #

  def get_p(self, low, high):
    return round((high - low) / low * 100, 2)


