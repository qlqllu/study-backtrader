import backtrader as bt

class HighPriceIndicator(bt.Indicator):
    lines = ('high',)

    params = (
      ('period', 20),
    )

    def __init__(self):
      self.addminperiod(self.p.period)

    def next(self):
      if len(self.data.datetime.array) < self.p.period:
        return

      self.dt = self.data.datetime.date(0).isoformat()

      p_data = self.data.high.get(size=self.p.period)

      self.highest = max(p_data)
      self.lines.high[0] = self.highest
