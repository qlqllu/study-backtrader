from re import S
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
  params = (
    # ('box_os', 0.20),
    # ('before_zt_p', 20),
    # ('before_zt_high', 1),
    # ('before_zt_high_p', 120),
  )

  def __init__(self):
    super().__init__()
    self.sl = 0
    # self.buy_index = None
    # self.box_high = 0
    # self.box_low = 0

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if not self.position:
      if d.close[0] > d.open[0] and \
        d.close[-1] < d.open[-1] and \
        d.close[-2] > d.open[-2] and \
        d.close[-3] > d.open[-3] and \
        d.close[-4] < d.open[-4] and \
        d.close[-5] < d.open[-5] and \
        d.close[-6] < d.open[-6]:

        self.buy()
        self.sl = d.open[0]
    else:
      if d.low[0] < self.sl:
        self.sell()
        self.sl = 0
      else:
        # Move SL
        if d.close[0] > self.sl * 1.1:
          self.sl = self.sl * 1.05





