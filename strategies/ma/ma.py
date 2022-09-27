import pandas as pd
import backtrader as bt
import numpy as np
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  observer_subplot = False

  def __init__(self):
    super().__init__()

    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.is_cross_up = bt.indicators.CrossUp(self.ma1, self.ma2)
    self.is_cross_down = bt.indicators.CrossDown(self.ma1, self.ma2)
    self.ob_sl = 0
    self.buy_price = 0
    self.cross_up_price = 0

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if self.is_cross_up[0] > 0:
      self.cross_up_price = d.close[0]

    if self.is_cross_down[0] > 0:
      self.cross_up_price = 0

    if not self.position:
      if self.cross_up_price > 0 and \
        d.low[0] > self.ma2[0] and \
        d.close[0] < self.cross_up_price * 1.2 and \
        d.close[0] > d.open[0] and d.close[0] > d.close[-1]:
          self.buy()
          self.ob_sl = d.low[0]
          self.cross_up_price = 0
    else:
      if d.close[0] < self.ma2[0]:
        self.sell()
        self.ob_sl = 0
        return

      if d.close[0] > self.buy_price * 1.2:
        if d.close[0] < self.ob_sl:
          self.sell()
          self.ob_sl = 0
          return

      if d.close[0] > self.ob_sl * 1.1:
        self.ob_sl = self.ob_sl * 1.05

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #


