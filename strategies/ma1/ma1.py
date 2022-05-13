import backtrader as bt
from strategies.base_strategy import BaseStrategy
from indicators.high_price_indicator import HighPriceIndicator

class Strategy(BaseStrategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    self.ma1 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.data, period=self.params.ma_period2)
    self.isCrossUp = bt.indicators.CrossUp(self.ma1, self.ma2)
    self.isCrossDown = bt.indicators.CrossDown(self.ma1, self.ma2)

  def next(self):
    d = self.data

    if not self.should_continue_next():
      return

    if not self.position:
      if self.isCrossUp[0] > 0:
        self.buy()
    else:
      if self.isCrossDown[0] > 0:
        self.sell()

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #

  def is_cross_up(self):
    return self.isCrossUp[0] > 0 or self.isCrossUp[-1] > 0


