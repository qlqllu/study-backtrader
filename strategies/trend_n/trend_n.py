from re import S
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('n_p', 3),
  )

  observer_subplot = True

  def __init__(self):
    super().__init__()
    self.sl = 0
    self.high_price = []
    self.low_price = []
    self.trend = 0

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    self.high_price.append(0)
    self.low_price.append(0)
    # self.high_price = 0
    # self.low_price = 0

    if not self.position:
      high_data_p = d.high.get(ago=-1, size=self.p.n_p * 2 + 1)

      if len(high_data_p) < self.p.n_p * 2 + 1:
        return

      if max(high_data_p) == high_data_p[self.p.n_p]:
        self.high_price[len(self) - 1] = high_data_p[self.p.n_p]

      low_data_p = d.low.get(ago=-1, size=self.p.n_p * 2 + 1)
      if min(low_data_p) == low_data_p[self.p.n_p]:
        self.low_price[len(self) - 1] = low_data_p[self.p.n_p]

      h = l = last_h = last_l = 0
      for i in range(len(self) - 1, 0, -1):
        if h > 0 and last_h > 0:
          break
        if self.high_price[i] > 0:
          if h == 0:
            h = self.high_price[i]
          elif last_h == 0:
            last_h = self.high_price[i]

      for i in range(len(self) - 1, 0, -1):
        if l > 0 and last_l > 0:
          break
        if self.low_price[i] > 0:
          if l == 0:
            l = self.low_price[i]
          elif last_l == 0:
            last_l = self.low_price[i]

      if h > last_h > 0 and l > last_l > 0:
        self.trend = 1
      elif 0 < h < last_h and 0 < l < last_l:
        self.trend = -1
      else:
        self.trend = 0
    else:
      if d.low[0] < self.sl:
        self.sell()
        self.sl = 0
      else:
        # Move SL
        if d.close[0] > self.sl * 1.1:
          self.sl = self.sl * 1.05





