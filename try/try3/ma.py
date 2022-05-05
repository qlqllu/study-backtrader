import pandas as pd
import backtrader as bt
import numpy as np
import math
import datetime

class MAStrategy(bt.Strategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.order = None
    self.trades = []
    self.dt = None
    self.buy_price = None
    self.sl = 0
    self.low = 0
    self.is_rising = None

    # Add a MovingAverageSimple indicator
    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.is_cross_up = bt.indicators.CrossUp(self.ma1, self.ma2)
    self.is_cross_down = bt.indicators.CrossDown(self.ma1, self.ma2)

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
        pass
      else:  # Sell
        self.order = None
        pass
        # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
        #          (order.executed.price,
        #           order.executed.value,
        #           order.executed.comm))
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')
      self.order = None

  def notify_trade(self, trade):
    if not trade.isclosed:
      return

    self.trades.append(trade)
    self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
             (trade.pnl, trade.pnlcomm))

  def next(self):
    self.dt = self.data.datetime.date(0).isoformat()

    if self.position:
      if self.data.close[0] < self.sl:
        self.log('--SELL SL, %.2f' % self.data0.close[0])
        self.order = self.sell()
      elif (
          self.data.close[0] > self.sl * 3 or \
          self.data.close[0] >= self.ma1[0] * 1.5
        ):
        # rise too high or too fast
        self.log('--SELL 1, %.2f' % self.data.close[0])
        self.order = self.sell()
      elif self.is_cross_down[0] > 0:
        self.log('--SELL 2, %.2f' % self.data.close[0])
        self.order = self.sell()
      else: # move SL
        # if self.data.close[0] > self.sl * 1.2:
        #   if self.data.close[0] > self.data.close[-1] >= self.data.close[-2] and \
        #     self.data.close[-4] >= self.data.close[-3] >= self.data.close[-2]:
        #     self.sl = self.data.close[-2]
        if self.data.close[0] > self.sl * 1.2 and self.data.close[0] < self.ma2[0] * 1.1:
          self.sl = self.ma2[0]

    if self.is_cross_up[0] > 0:
      # buy 1
      self.log('++ BUY 1, %.2f' % (self.data.close[0]))
      self.order = self.buy()
      self.sl = min(self.data.low[0], self.ma2[-1])
      self.low = self.sl

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #


