from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np

class MyStrategy(bt.Strategy):
  params = (
    ('oscillation', 0.2),
    ('oscillation_p', 30),
    ('log', False)
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)

    if self.params.log:
      print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.dt = None
    self.sl = 0
    self.buy_index = None
    self.trades = []
    self.sell_reason = ''

  def next(self):
    d = self.data

    self.dt = d.datetime.date(0).isoformat()

    d = self.data
    os = self.params.oscillation
    os_p = self.params.oscillation_p

    if not self.position:
      if d.close[0] > d.open[0] and d.close[0] > max(d.close[-1], d.open[-1]) and \
        abs(d.close[-1] - d.open[-1])/d.open[-1] < 0.03 and \
        d.volume[-1] > d.volume[-2] * 1.1 and \
        d.low[-1] > d.high[-2] and \
        d.close[-2] >= d.close[-3] * 1.099:

        # self.buy()
        # self.sl = d.close[-2]
        p = min(len(d.close) - 3, os_p)
        p_data = d.close.get(ago=-3, size=p)
        if len(p_data) < 5:
          return

        if max(p_data) <= min(p_data) * (1 + os):
          self.buy()
          self.sl = d.close[-2]
          self.buy_index = len(self) + 1
    else:
      if len(self) - self.buy_index > 2 and d.close[0] < self.buy_price * 1.1:
        self.sell()
        self.sl = 0
      elif (d.low[0] < self.sl):
        self.sell()
        self.sl = 0
      else:
        # Move SL
        if d.close[0] > self.sl * 1.1:
          self.sl = d.close[0] * 0.95

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





