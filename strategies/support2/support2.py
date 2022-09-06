import backtrader as bt
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('fall_p', 3),
    ('support_p', 2),
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

    check_p = self.p.fall_p + self.p.support_p + 1
    if len(d.high.get(size = check_p)) < check_p:
      return

    if self.sell_i + check_p + 2 >= len(self):
      return

    if not self.position:
      is_falling = True
      is_supporting = True

      for i in range(self.p.fall_p):
        if d.high[0 - i - 1 - self.p.support_p] > d.high[0 - i - 2 - self.p.support_p]:
          is_falling = False

      last_fall_i = 0 - self.p.support_p - 1

      for i in range(self.p.support_p):
        j = 0 - i - 1
        if d.low[j] < d.low[j - 1]:
          is_supporting = False
        if not (max(d.close[j], d.open[j]) < max(d.open[last_fall_i], d.close[last_fall_i])):
          is_supporting = False

      if is_falling and is_supporting and \
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





