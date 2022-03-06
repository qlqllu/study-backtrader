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

    # Add a MovingAverageSimple indicator
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)

  def next(self):
    self.dt = self.data.datetime.date(0).isoformat()

    if self.sl == 0:
      self.sl = self.data.low[0]

    if self.data.low[0] > self.data.low[-1] >= self.data.low[-2]:
      self.sl = self.data.low[-2]

    self.ma2_direction = self.check_direction(self.ma2)

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3] > line[-4]:
      return 1 # up
    elif line[0] < line[-1] < line[-2] < line[-3] < line[-4]:
      return -1 # down
    else:
      return 0 #


