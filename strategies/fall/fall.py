import backtrader as bt
from strategies.base_strategy import BaseStrategy
import numpy as np
from sklearn import linear_model
import pandas as pd
from indicators.fall_indicator import FallIndicator

reg = linear_model.LinearRegression()

class Strategy(BaseStrategy):
  params = (
    ('fall_period', 10),
    ('fall_k', 0),
    ('os_period', 10),
  )

  observer_subplot = False

  def __init__(self):
    super().__init__()
    self.ob_sl = 0
    self.ob_box_high = 0
    self.ob_box_low = 0

    self.fall = FallIndicator(self.data, period=self.p.fall_period, k=self.p.fall_k)
    self.fall_done_index = 0
    self.fall_done_price_index = 0
    self.is_os_ok = False

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if not self.position:
      if not self.fall.falling[0] and self.fall.falling[-1]:
        self.fall_done_index = len(self)
        self.fall_done_price_index = len(self)

      if self.fall_done_index > 0 and len(self) >= self.fall_done_index + self.p.os_period:
        self.fall_done_index = 0

        self.ob_box_high = max(d.high.get(self.p.os_period))
        self.ob_box_low = min(d.low.get(self.p.os_period))
        if self.ob_box_high <= d.high[self.fall_done_price_index - len(self)] * 1.1 and self.ob_box_low > d.low[self.fall_done_price_index - len(self)] * 0.9:
          self.is_os_ok = True

      if self.is_os_ok and d.close[0] > d.close[self.fall_done_price_index - len(self)]:
        self.buy()
        self.ob_sl = d.low[-1]
        self.is_falling = False
    else:
      if d.close[0] < self.ob_sl:
        self.sell()
        self.ob_sl = 0
        self.s = len(self)
        return

      if d.close[0] > self.ob_sl * 1.05:
        self.ob_sl = self.ob_sl * 1.05





