import backtrader as bt
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('box_period', 20),
    ('rise_persent', 0.2),
  )

  observer_subplot = False

  def __init__(self):
    super().__init__()
    self.ob_sl = 0
    self.ob_box_high = 0
    self.ob_box_low = 0

  def next(self):
    d = self.data

    if not self.should_continue_next():
      return

    self.dt = d.datetime.date(0).isoformat()
    box_period = self.params.box_period

    if not self.position:
      self.ob_sl = 0

      if len(d.close.get(ago=-1, size=box_period)) < box_period:
        return

      box_max = max(d.high.get(ago=-1, size=box_period))
      box_min = min(d.low.get(ago=-1, size=box_period))

      if self.is_low_price(len(self), d.close[0]):
        self.ob_box_high = box_max
        self.ob_box_low = box_min

        if d.close[0] > box_max:
          self.buy()
          self.ob_sl = max(box_min, box_max * (1 - self.p.rise_persent / 2))

          self.ob_box_high = 0
          self.ob_box_low = 0

          if self.p.last_bar:
            self.buy_last_bar = True
      else:
        self.ob_box_high = 0
        self.ob_box_low = 0

    else:
      if d.close[0] < self.ob_sl:
        self.sell()
        return

      if d.close[0] > self.ob_sl * (1 + self.p.rise_persent / 2):
        self.ob_sl = self.ob_sl * (1 + self.p.rise_persent / 4)

  def is_low_price(self, n, price):
    if n < self.p.box_period * 3:
      return False

    for i in range(n):
      d = self.data.close
      if d[0 - i] > price * (1 + self.params.rise_persent):
        return True
      if i > self.p.box_period * 3:
        return False
    return False








