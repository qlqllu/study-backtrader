import backtrader as bt
import datetime

class HighPriceIndicator(bt.Indicator):
    lines = ('high',)

    params = (
      ('period', 10),
    )

    def __init__(self):
      self.addminperiod(self.p.period)

    def next(self):
      self.dt = self.data.datetime.date(0).isoformat()

      p_data = self.data.close.get(size=self.p.period)

      self.highest = max(p_data)
      self.lines.high[0] = self.highest
