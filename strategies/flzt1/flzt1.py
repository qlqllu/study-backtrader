from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    ('box_os', 0.15),
    ('box_p', 30),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    self.buy_index = None
    self.box_high = 0
    self.box_low = 0

  def next(self):
    d = self.data

    if not self.should_continue_next():
      return

    self.box_high = 0
    self.box_low = 0
    box_os = self.params.box_os
    box_p = self.params.box_p

    if not self.position:
      if abs(d.close[0] - d.open[0])/d.open[0] < 0.03 and \
        d.volume[0] > d.volume[-1] * 1.1 and \
        d.low[0] > d.high[-1] and \
        d.close[-1] >= d.close[-2] * 1.099:

        # self.buy()
        # self.sl = d.close[-1]
        # self.buy_index = len(self) + 1

        if len(d.close.get(ago=-1, size=box_p)) < box_p:
          return

        box_max = max(d.high.get(ago=-1, size=box_p))
        box_min = min(d.low.get(ago=-1, size=box_p))
        if box_max <= box_min * (1 + box_os):
          self.buy()
          self.sl = d.close[-1]
          self.buy_index = len(self) + 1
    else:
      if len(self) - self.buy_index > 2 and d.close[0] < self.buy_price * 1.1:
        self.sell()
        self.sl = 0
        self.log('S1')
      elif (d.low[0] < self.sl):
        self.sell()
        self.sl = 0
        self.log('S2')
      else:
        # Move SL
        if d.close[0] > self.sl * 1.05:
          self.sl = d.close[0] * 0.95





