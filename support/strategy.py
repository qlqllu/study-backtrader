from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np
from high_price_indicator import HighPriceIndicator
from low_price_indicator import LowPriceIndicator

class MyStrategy(bt.Strategy):
  params = (
    ('period', 2),
    ('log', False)
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)

    if self.params.log:
      print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.dt = None
    self.sl = 0
    self.is_rising = False
    self.trades = []
    self.buy_reason = ''
    self.sell_reason = ''
    self.support = 0
    self.support_dt = None
    self.last_support = 0

    # self.high_price = HighPriceIndicator(self.data, subplot=False, period=self.params.break_period)
    # self.low_price = LowPriceIndicator(self.data, subplot=False, period=self.params.break_period)
    # self.ma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.break_period)

    # if len(self.data.datetime.array) > self.params.ma_period:
    #   self.ma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period)
    # else:
    #   self.ma = None

  def next(self):
    d = self.data

    self.dt = d.datetime.date(0).isoformat()

    if not self.position:
      l_min = m = r_min = h = d.low[-1]

      for i in range(self.p.period + 2, self.p.period * 2 + 2):
        l_min = min(d.low[0 - i], l_min)
        h = max(d.close[0 - i], h)

      m = d.low[0 - self.p.period - 1]

      for i in range(1, self.p.period + 1):
        r_min = min(d.low[0 - i], r_min)
        h = max(d.close[0 - i], h)

      if m < l_min and m < r_min and h > m * 1.1:
        self.support = m
        self.support_dt = d.datetime.date(0 - self.p.period)

        if self.support > self.last_support > 0: # low low up
          self.buy()
          self.sl = self.support
          self.last_support = 0
        else:
          self.last_support = self.support

      if self.support > 0 and d.close[0] < self.support:
        self.support = 0
        self.last_support = 0

      if self.support > 0 and (d.datetime.date(0) - self.support_dt).days > self.p.period + 1 and \
        d.close[0] > self.support and (d.low[0] < self.support * 1.01) and \
        d.close[0] > d.open[0]:
        self.buy()
        self.sl = self.support

    else:
      # Move SL
      if d.close[0] > self.sl * 1.05:
        self.sl = self.sl * 1.05

      if d.low[0] < self.sl:
        self.sell()
        self.sl = 0
        self.support = 0
        self.last_support = 0
        return

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
    trade.sell_reason = self.sell_reason

    self.trades.append(trade)
    self.log(f'Trade, Init: {self.trade_init_value}, Profit: {int(trade.pnlcomm)}, Percent: {p}')


  def check_direction(self, line):
    if not line:
      return 0

    if line[0] > line[-1] > line[-2] > line[-3] > line[-4]:
      return 1 # up
    elif line[0] < line[-1] < line[-2] < line[-3] < line[-4]:
      return -1 # down
    else:
      return 0 #



