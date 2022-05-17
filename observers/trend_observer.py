import backtrader as bt

class TrendObserver(bt.Observer):
  lines = ('high', 'low', 'trend')

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  plotlines = dict(
    high=dict(marker='v', markersize=8.0, color='lime',
              fillstyle='full', ls=''),
    low=dict(marker='^', markersize=8.0, color='red',
              fillstyle='full', ls=''),
    trend=dict(ls='-', color='red')
  )

  def next(self):
    if hasattr(self._owner, 'trend') and hasattr(self._owner.p, 'n_p'):
      trend = self._owner.trend
      np = self._owner.p.n_p

      if self._owner.high_price[len(self) - 1] > 0:
        self.lines.high[0 - np - 1] = self._owner.high_price[len(self) - 1]

      if self._owner.low_price[len(self) - 1] > 0:
        self.lines.low[0 - np - 1] = self._owner.low_price[len(self) - 1]

      if trend == 0:
        pass
      elif trend > 0:
        self.lines.trend[0] = self._owner.data.high[0]
      elif trend < 0:
        self.lines.trend[0] = self._owner.data.low[0]
