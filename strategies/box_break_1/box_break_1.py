import backtrader as bt
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('box_os', 0.30),
    ('box_p', 60),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    self.box_high = 0
    self.box_low = 0
    self.moving_box_high = 0
    self.moving_box_low = 0

  def next(self):
    d = self.data

    if not self.should_continue_next():
      return

    self.box_high = 0
    self.box_low = 0

    self.dt = d.datetime.date(0).isoformat()
    box_os = self.params.box_os
    box_p = self.params.box_p

    if not self.position:
      self.sl = 0

      if len(d.close.get(ago=-1, size=box_p)) < box_p:
        return

      box_max = max(d.high.get(ago=-1, size=box_p))
      box_min = min(d.low.get(ago=-1, size=box_p))
      if box_max <= box_min * (1 + box_os) and d.close[0] > box_max:
        self.buy()
        self.sl = box_min + (box_max - box_min) / 2
        self.box_high = box_max
        self.box_low = box_min
        self.moving_box_high = box_max
        self.moving_box_low = box_min

        if self.p.last_bar:
          self.buy_last_bar = True

    else:
      if d.low[0] < self.sl:
        self.sell()
        self.moving_box_high = 0
        self.moving_box_low = 0
        return

      # Move SL
      if d.low[0] > self.moving_box_high * (1 + box_os):
        self.moving_box_high = self.moving_box_high * (1 + box_os)
        self.moving_box_low = self.moving_box_low * (1 + box_os)
        self.sl = self.moving_box_low + (self.moving_box_high - self.moving_box_low) / 2





