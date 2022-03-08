import pandas as pd
import backtrader as bt
import numpy as np

class TrendNIndicator(bt.Indicator):

  lines = ('high', 'low')

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  plotlines = dict(
    high=dict(marker='o', markersize=4.0, color='lime',
              fillstyle='full', ls=''),
    low=dict(marker='o', markersize=4.0, color='red',
              fillstyle='full', ls='')
  )

  def __init__(self):
    self.dt = None
    self.status = None
    self.high = 0
    self.low = 0

  def next(self):
    self.dt = self.data.datetime.date(0).isoformat()

    d = self.data

    if not self.status == 'up' and d.low[0] > d.low[-1] > d.low[-2]:
      self.status = 'up'
      self.lines.low[-2] = d.low[-2]
    elif not self.status == 'down' and d.low[0] < d.low[-1] < d.low[-2]:
      self.status = 'down'
      self.lines.high[-2] = d.high[-2]



