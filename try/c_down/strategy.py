from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np
from high_price_indicator import HighPriceIndicator
from low_price_indicator import LowPriceIndicator

class MyStrategy(bt.Strategy):
  params = (
    ('c_down', 4),
    ('break_period', 60),
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

    # self.high_price = HighPriceIndicator(self.data, subplot=False, period=self.params.break_period)
    self.low_price = LowPriceIndicator(self.data, subplot=False, period=self.params.break_period)
    # self.ma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.break_period)

    # if len(self.data.datetime.array) > self.params.ma_period:
    #   self.ma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period)
    # else:
    #   self.ma = None

  def next(self):
    d = self.data

    self.dt = d.datetime.date(0).isoformat()

    if not self.position:
      self.sl = 0

      is_cdown = True
      for i in range(2, self.p.c_down + 2):
        if d.close[0 - i] > d.open[0 - i]:
          is_cdown = False

      if is_cdown and d.close[0] > d.open[0] and d.close[-1] > d.open[-1] and d.close[0] > self.low_price[-1]:
        self.buy()
        self.sl = d.low[0]
    else:
      # Move SL
      if d.close[0] > self.sl * 1.05:
        self.sl = self.sl * 1.02

      if d.low[0] < self.sl:
        self.sell()
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



