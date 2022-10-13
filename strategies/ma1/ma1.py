import pandas as pd
import backtrader as bt
import numpy as np
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
    ('ma1_ma2_diff_percent', 0.02), # diff percent less then this number is considered cross
    ('cross_up_high_percent', 0.5), # we don't buy if the price is two high
    ('start_move_sl_percent', 1), # we start to check SL only when the profit is enough
    ('move_sl_percent', 0.1), # move SL per step
  )

  observer_subplot = False

  def __init__(self):
    super().__init__()

    if self.data.close.buflen() < self.params.ma_period2:
      return

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

    if not self.should_continue_next():
      return

    if self.data.close.buflen() < self.params.ma_period2:
      return

    if self.is_cross_up[0] > 0:
      self.cross_up_price = self.ma2[-1]

    if 0 < self.ma1[0] - self.ma2[0] < self.ma2[0] * self.p.ma1_ma2_diff_percent:
      self.cross_up_price = self.ma2[0]

    if self.is_cross_down[0] > 0:
      self.cross_up_price = 0

    if not self.position:
      if self.cross_up_price > 0 and self.check_direction(self.ma2) > 0 and\
        d.open[0] > self.ma2[0] and \
        d.close[0] < self.cross_up_price * (1 + self.p.cross_up_high_percent) and \
        d.close[0] > d.open[0] and d.close[0] > d.close[-1]:
          self.buy()
          self.ob_sl = self.cross_up_price
          self.cross_up_price = 0
          self.buy_price = d.close[0]

          if self.p.last_bar:
            self.buy_last_bar = True
          return

      # if d.low[0] < self.ma2[0] < min(d.close[0], d.open[0]) * 0.99 and \
      #   min(d.open[-1], d.close[-1]) > self.ma2[-1] and min(d.open[-2], d.close[-2]) > self.ma2[-2] and \
      #   self.ma1[0] > self.ma2[0] and \
      #   d.close[0] > d.close[-1] and d.close[0] > d.open[0] and \
      #   d.close[0] < self.cross_up_price * 1.5:
      #   self.buy()
      #   self.ob_sl = self.ma2[0]
      #   self.cross_up_price = 0
      #   self.buy_price = d.close[0]
      #   return

    else:
      if max(d.close[0], d.open[0]) < self.ma2[0] or d.close[0] < self.ob_sl:
        self.sell()
        self.ob_sl = 0
        return

      if d.close[0] > self.buy_price * (1 + self.p.start_move_sl_percent):
        if d.close[0] < self.ob_sl:
          self.sell()
          self.ob_sl = 0
          return

        if d.close[0] > self.ob_sl * (1 + self.p.start_move_sl_percent):
          self.ob_sl = self.ob_sl * (1 + self.p.start_move_sl_percent)

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #


