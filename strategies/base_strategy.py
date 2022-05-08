from datetime import datetime
import pandas as pd
import backtrader as bt
import numpy as np

class BaseStrategy(bt.Strategy):
  params = (
    ('log', False), # whether print log
    ('last_bar', False), # if true, will run the strategy with the last bar only
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)

    if self.params.log:
      print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.dt = None
    self.trades = []

    self.buy_last_bar = False # whether the last bar is a buy point

    # the current trade's buy and sell reason
    self.buy_reason = None
    self.sell_reason = None
    self.buy_price = 0


  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return

    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        self.buy_price = order.executed.price
        # self.log(f'BUY EXECUTED, Price: {order.executed.price}')
        pass
      else:  # Sell
        # self.log(f'SELL EXECUTED, Price: {order.executed.price}')
        pass
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')
      pass

  def notify_trade(self, trade):
    if not trade.isclosed:
      self.open_trade = trade
      trade.buy_reason = self.buy_reason
      return

    trade.open_trade = self.open_trade
    trade.sell_reason = self.sell_reason

    init_value = self.open_trade.price * self.open_trade.size
    profit_percent = round(trade.pnlcomm / init_value * 100, 2)
    trade.profit_percent = profit_percent
    self.trades.append(trade)
    self.log(f'pnlPercent: {profit_percent}')

  def should_continue_next(self):
    d = self.data
    return not (self.p.last_bar and len(self) < d.close.buflen())
