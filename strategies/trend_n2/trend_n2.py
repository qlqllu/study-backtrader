from re import S
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('n_p', 3),
  )

  observer_subplot = False

  def __init__(self):
    super().__init__()
    self.ob_sl = 0
    self.low_price = 0
    self.last_low_price = 0

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    p = self.p.n_p
    low_data_p = d.low.get(ago=-1, size=p * 2 + 1)

    if len(low_data_p) < p * 2 + 1:
      return

    middle_is_low = min(low_data_p) == low_data_p[p]

    # for i in range(p, p*2):

    l = last_l = 0

    for i in range(len(self) - 1, 0, -1):
      if l > 0 and last_l > 0:
        break
      if self.low_price[i] > 0:
        if l == 0:
          l = self.low_price[i]
        elif last_l == 0:
          last_l = self.low_price[i]

    if not self.position:
      if l > last_l > 0:
        self.buy()
        self.ob_sl = l
        for i in range(len(self.low_price)):
          self.low_price[i] = 0
    else:
      if d.low[0] < self.ob_sl:
        self.sell()
        self.ob_sl = 0
      else:
        # Move SL
        if l > last_l > 0:
          self.ob_sl = l





