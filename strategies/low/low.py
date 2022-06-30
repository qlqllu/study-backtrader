from re import S
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('low_p', 250),
    ('low1', 0.3),
    ('low2', 0.7),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    # self.buy_index = None
    # self.box_high = 0
    # self.box_low = 0
    # self.zt_index = 0
    # self.box_high = 0
    # self.box_low = 0

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    low_p = self.params.low_p
    low1 = self.params.low1
    low2 = self.params.low2
    if len(d.close.get(ago=-1, size=low_p)) < low_p:
      return

    box_max = max(d.high.get(ago=-1, size=low_p))
    if d.close[0] < box_max * low1:
      self.buy_last_bar = True





