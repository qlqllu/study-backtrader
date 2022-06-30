import pandas as pd
import backtrader as bt
import numpy as np
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  def __init__(self):
    super().__init__()

    # Add a MovingAverageSimple indicator
    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.isCrossUp = bt.indicators.CrossUp(self.ma1, self.ma2)

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if not self.position:
      if self.check_direction(self.ma2) > 0 and self.is_cross_up():
        # buy 1
        self.buy()
        self.buy_last_bar = True

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #

  def is_cross_up(self):
    return self.isCrossUp[0] > 0 or self.isCrossUp[-1] > 0


