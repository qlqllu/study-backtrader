import backtrader as bt
import datetime

class LowPriceIndicator(bt.Indicator):
    lines = ('low',)

    params = (
      ('period', 50),
      ('low_check', 0.7)
    )

    def __init__(self):
      self.addminperiod(self.p.period)
    
    def next(self):
      self.dt = self.data.datetime.date(0).isoformat()

      p_data = self.data.high.get(size=self.p.period)
      
      self.highest = max(p_data)
      self.lines.low[0] = self.highest * self.p.low_check
