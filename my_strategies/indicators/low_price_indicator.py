import backtrader as bt
import datetime

class LowPriceIndicator(bt.Indicator):
    lines = ('low',)

    params = (
      ('period', 150),
      ('low_check', 0.5)
    )

    def __init__(self):
      self.addminperiod(self.p.period)
    
    def next(self):
      p_data = self.data.get(size=self.p.period)
      
      self.highest = max(p_data)
      self.lines.low[0] = self.highest * self.p.low_check
