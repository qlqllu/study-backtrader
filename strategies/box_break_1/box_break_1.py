from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np

class Strategy(bt.Strategy):
  params = (
    ('box_h', 0.20),
    ('box_p', 60),
    ('log', False),
    ('last_bar', False),
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
    self.buy_last_bar = False
    self.box_high = 0
    self.box_low = 0


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

    if self.p.last_bar and len(self) < d.close.buflen():
      return

    self.box_high = 0
    self.box_low = 0

    self.dt = d.datetime.date(0).isoformat()
    box_h = self.params.box_h
    box_p = self.params.box_p

    if not self.position:
      self.sl = 0

      if len(d.close.get(ago=-1, size=box_p)) < box_p:
        return

      box_max = max(d.high.get(ago=-1, size=box_p))
      box_min = min(d.low.get(ago=-1, size=box_p))
      if box_max <= box_min * (1 + box_h) and d.close[0] > box_max:
        self.buy()
        self.sl = box_min
        self.box_high = box_max
        self.box_low = box_min

        if self.p.last_bar:
          self.buy_last_bar = True

    else:
      if d.low[0] < self.sl:
        self.sell()
        return

      # Move SL
      if d.close[0] > self.sl * 1.1:
        self.sl = self.sl * 1.1





