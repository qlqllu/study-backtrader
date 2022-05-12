from re import S
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('box_os', 0.20),
    ('before_zt_p', 20),
    ('before_zt_high', 1),
    ('before_zt_high_p', 120),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    # self.buy_index = None
    # self.box_high = 0
    # self.box_low = 0
    self.zt_index = 0
    self.box_high = 0
    self.box_low = 0

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if not self.position:
      if self.zt_index > 0:
        if d.close[0] < self.box_low:
          self.zt_index = 0
          self.box_low = 0
          self.box_high = 0
        else:
          if d.low[0] > self.box_high and len(self) < self.zt_index + 5:
            self.zt_index = 0
            self.box_low = 0
            self.box_high = 0
          elif d.close[0] > self.box_high and d.open[0] < self.box_high and len(self) >= self.zt_index + 5:
            self.buy()
            self.sl = self.box_low
            self.zt_index = 0
            self.box_low = 0
            self.box_high = 0
      else:
        if d.close[0] >= d.open[0] * 1.098:
          box_p = self.params.before_zt_p
          box_os = self.params.box_os
          before_zt_high = self.params.before_zt_high
          before_zt_high_p = self.params.before_zt_high_p

          if len(d.close.get(ago=-1, size=box_p)) < box_p or len(d.close.get(ago=-1, size=before_zt_high_p)) < before_zt_high_p:
            return

          box_max = max(d.high.get(ago=-1, size=box_p))
          box_min = min(d.low.get(ago=-1, size=box_p))
          if max(d.high.get(ago=-1, size=before_zt_high_p)) > d.close[0] * (1 + before_zt_high) and box_max <= box_min * (1 + box_os): # down and oscillation
            self.zt_index = len(self)
            self.box_low = d.open[0]
            self.box_high = d.close[0]
    else:
      if d.low[0] < self.sl:
        self.sell()
        self.sl = 0
      else:
        # Move SL
        if d.close[0] > self.sl * 1.1:
          self.sl = self.sl * 1.05





