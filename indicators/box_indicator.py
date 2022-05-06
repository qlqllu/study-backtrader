import backtrader as bt

class BoxIndicator(bt.Indicator):
    lines = ('high', 'low')

    params = (
      ('period', 20),
      ('oscillation', 0.1)
    )

    def __init__(self):
      self.addminperiod(self.p.period)

    def next(self):
      if len(self.data.datetime.array) < self.p.period:
        return

      self.dt = self.data.datetime.date(0).isoformat()

      p_data = self.data.high.get(size=self.p.period)

      highest = max(p_data)
      lowest = min(p_data)
      if highest <= lowest * (1 + self.p.oscillation):
        self.lines.high[0] = highest
        self.lines.low[0] = lowest
