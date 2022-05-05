import backtrader as bt

class SLObserver(bt.Observer):
  lines = ('sl',)

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  def next(self):
    if self._owner.sl > 0:
      self.lines.sl[0] = self._owner.sl