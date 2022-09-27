import backtrader as bt
from strategies.base_strategy import BaseStrategy
import numpy as np
from sklearn import linear_model
import pandas as pd
from indicators.fall_indicator import FallIndicator

reg = linear_model.LinearRegression()

class Strategy(BaseStrategy):
  params = (
    ('fall_period', 20),
    ('fall_k', -0.01),
    ('os_period', 5),
  )

  observer_subplot = False

  def __init__(self):
    super().__init__()
    self.ob_sl = 0
    self.ob_box_high = 0
    self.ob_box_low = 0

    self.fall = FallIndicator(self.data, period=self.p.fall_period, k=self.p.fall_k)
    self.fall_done_index = 0
    self.is_os_ok = False

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if not self.position:
      if not self.fall.falling[0] and self.fall.falling[-1]:
        self.fall_done_index = len(self)
        self.ob_box_high = d.high[0] * 1.03
        self.ob_box_low = min(d.low.get(size=self.p.fall_period)) if len(d.low.get(size=self.p.fall_period)) > 0 else d.low[0]
        self.log(f'Fall done. {self.dt}')

      if self.fall_done_index > 0 and len(self) >= self.fall_done_index + self.p.os_period:
        self.fall_done_index = 0

        # if len(d.high.get(self.p.os_period)) == 0:
        #   self.log(f'No data. {self.dt}')
        #   return

        p_high = max(d.high.get(ago=-1, size=self.p.os_period))
        p_low = min(d.low.get(ago=-1, size=self.p.os_period))

        if p_high >= self.ob_box_high:
          self.is_os_ok = True
          self.log(f'Box ok. {self.dt}')
        else:
          self.fall_done_index = 0
          self.ob_box_high = 0
          self.ob_box_low = 0
          self.log(f'No box. {self.dt}')

      if self.is_os_ok:
        if d.close[0] < self.ob_box_low:
          self.ob_box_high = 0
          self.ob_box_low = 0
          self.is_falling = False
          self.is_os_ok = False
          self.log(f'Fall down box. {self.dt}')
          return

        if d.close[0] > self.ob_box_high:
          self.buy()
          self.ob_sl = d.low[-1]

          self.ob_box_high = 0
          self.ob_box_low = 0
          self.is_falling = False
          self.is_os_ok = False
          self.log(f'Buy. {self.dt}')
    else:
      if d.close[0] < self.ob_sl:
        self.sell()
        self.ob_sl = 0
        self.s = len(self)
        return

      if d.close[0] > self.ob_sl * 1.05:
        self.ob_sl = self.ob_sl * 1.05





