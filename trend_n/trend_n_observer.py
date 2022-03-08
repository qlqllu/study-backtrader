import backtrader as bt

class TrendNObserver(bt.Observer):
  lines = ('high', 'low')

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  plotlines = dict(
    high=dict(marker='^', markersize=8.0, color='lime',
              fillstyle='full', ls=''),
    low=dict(marker='v', markersize=8.0, color='red',
              fillstyle='full', ls='')
  )

  def next(self):
    if self._owner.high > 0:
      self.lines.high[0] = self._owner.high

    if self._owner.low > 0:
      self.lines.low[0] = self._owner.low