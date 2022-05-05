import backtrader as bt

class LowPriceIndicator(bt.Indicator):
    lines = ('low',)

    params = (
      ('period', 20),
    )

    def __init__(self):
      self.addminperiod(self.p.period)

    def next(self):
      if len(self.data.datetime.array) < self.p.period:
        return

      self.dt = self.data.datetime.date(0).isoformat()

      p_data = self.data.low.get(size=self.p.period)

      self.lowest = min(p_data)
      self.lines.low[0] = self.lowest
