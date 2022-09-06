import backtrader as bt
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    self.sell_i = 0
    self.ma = bt.indicators.SimpleMovingAverage(self.data, period=60)

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if len(d.high.get(size=6)) < 6:
      return
    if self.sell_i + 8 >= len(self):
      return

    if not self.position:
      if self.check_direction(self.ma) > 0 and \
        d.high[-5] > d.high[-4] > d.high[-3] and \
        max(d.close[-1], d.close[-2]) < d.high[-3] and \
        d.low[-2] < d.close[-1] < d.high[-2] and \
        d.close[0] > max(d.low[-1], d.low[-2]) and \
        d.close[0] > d.open[0]:
        self.buy()
        self.sl = max(d.low[-1], d.low[-2])
    else:
      if d.close[0] < self.sl:
        self.sell()
        self.sell_i = len(self)
        return

      if d.close[0] > self.sl * 1.05:
        self.sl = self.sl * 1.05

  def check_direction(self, line):
    if line[0] > line[-1] > line[-2] > line[-3]:
      return 1 # up
    elif line[0]  < line[-1] < line[-2] < line[-3]:
      return -1 # down
    else:
      return 0 #





