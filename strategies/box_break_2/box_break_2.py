import backtrader as bt
from strategies.base_strategy import BaseStrategy
from indicators.high_price_indicator import HighPriceIndicator

class Strategy(BaseStrategy):
  params = (
    ('box_p', 250),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    self.high_price = HighPriceIndicator(self.data, subplot=False, period=self.params.box_p)

  def next(self):
    d = self.data

    if not self.should_continue_next():
      return

    if not self.position:
      if d.close[0] > self.high_price[-1] * 1.01 and d.close[0] > d.open[0]:
        self.buy()
        self.sl = d.open[-1]
    else:
      if d.low[0] < self.sl:
        self.sell()
        self.sl = 0
        return

      # Move SL
      if d.close[0] > self.sl * 1.05:
        self.sl = self.sl * 1.05





