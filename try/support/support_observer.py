import backtrader as bt

class SupportObserver(bt.Observer):
  lines = ('support',)

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  def next(self):
    if self._owner.support > 0:
      self.lines.support[0] = self._owner.support