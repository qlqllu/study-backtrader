from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np
from high_price_indicator import HighPriceIndicator

class MyStrategy(bt.Strategy):
  params = (
    ('break_period', 60),
    ('ma_period', 60),
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

    self.high_price = HighPriceIndicator(self.data, subplot=False, period=self.params.break_period)

    # if len(self.data.datetime.array) > self.params.ma_period:
    #   self.ma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period)
    # else:
    #   self.ma = None

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


  def next(self):
    d = self.data

    self.dt = d.datetime.date(0).isoformat()

    if not self.position:
      self.sl = 0

      if d.close[0] > self.high_price[-1] * 1.01 and d.close[0] > d.open[0]:
        self.buy()
        self.sl = d.open[-1]
    else:
      if d.low[0] < self.sl:
        self.sell()
        return

      # Move SL
      if not self.is_rising and \
        d.close[0] > d.close[-1] > d.close[-2]:
        self.sl = d.close[-1]
        self.is_rising = True
      else:
        self.is_rising = False

      if d.close[0] > self.sl * 1.05:
        self.sl = d.close[0]

      # if d.close[0] > self.buy_price * 3 and \
      #    d.close[0] >= self.ma1[0] * 1.2 and \
      #    d.close[0] < d.open[0]:
      #     # sell 1
      #     # self.log('SELL CREATE1, %.2f' % self.data.close[0])
      #     self.sell()
      #     self.sell_dt = d.datetime.date(0)
      #     self.sell_reason = 'S1'
      # else:
      #   if d.close[0] < self.ma2[0]:
      #     self.sell_reason = 'S2'
      #     self.sell()
      #     self.sell_dt = d.datetime.date(0)
      #   elif d.close[0] < self.sl:
      #     self.sell_reason = 'SL'
      #     self.sell()
      #     self.sell_dt = d.datetime.date(0)

        # self.log('--Sell 2, %.2f' % d.close[0])

  def check_direction(self, line):
    if not line:
      return 0

    if line[0] > line[-1] > line[-2] > line[-3] > line[-4]:
      return 1 # up
    elif line[0] < line[-1] < line[-2] < line[-3] < line[-4]:
      return -1 # down
    else:
      return 0 #



