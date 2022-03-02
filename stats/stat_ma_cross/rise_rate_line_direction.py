import pandas as pd
import backtrader as bt
import numpy as np
import math
import datetime

class FindRiseRateStrategy(bt.Strategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.is_cross_up = bt.indicators.CrossUp(self.ma1, self.ma2)
    self.is_cross_down = bt.indicators.CrossDown(self.ma1, self.ma2)

    self.crosses = []
    self.cross = None
    self.prices = []

  def next(self):
    self.dt = self.data.datetime.date(0).isoformat()

    if self.cross:
      self.prices.append(self.data.close[0])

    if self.check_direction(self.ma2) > 0 and self.is_cross_up[0] > 0:
      self.cross = dict(
        up_dt = self.data.datetime.date(0),
        up_price = self.data.close[0]
      )
      # self.prices.append(self.data.close[0])
    elif self.check_direction(self.ma2) < 0 or self.is_cross_down[0] > 0:
      if self.cross == None:
        return
      
      self.cross['down_dt'] = self.data.datetime.date(0)
      self.cross['down_price'] = self.data.close[0]
      arr = np.array(self.prices)
      self.cross['highest'] = np.max(arr)
      self.cross['weeks'] = len(arr)
      self.cross['rise_rate%'] = round((self.cross['highest'] - arr[0]) / arr[0] * 100, 2)
      self.cross['down_up%'] = round((self.cross['down_price'] - self.cross['up_price']) / self.cross['up_price'] * 100, 2)

      self.crosses.append(self.cross)

      self.cross = None
      self.prices = []
      

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #

  def get_percentage(self, val_h, val_l):
    return (val_h - val_l)/val_l * 100
