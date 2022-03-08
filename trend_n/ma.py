import pandas as pd
import backtrader as bt
import numpy as np

from trend_n_indicator import TrendNIndicator

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
    self.status = None
    self.high = 0
    self.low = 0

    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.trendN = TrendNIndicator(self.data)

  def next(self):
    self.dt = self.data.datetime.date(0).isoformat()

    # d = self.data

    # self.high = 0
    # self.low = 0

    # if not self.status == 'up' and d.low[0] > d.low[-1] > d.low[-2] and d.high[0] > d.high[-1] > d.high[-2]:
    #   self.status = 'up'
    #   self.low = d.low[-2]
    # elif not self.status == 'down' and d.low[0] < d.low[-1] < d.low[-2] and d.high[0] < d.high[-1] < d.high[-2]:
    #   self.status = 'down'
    #   self.high = d.high[-2]



