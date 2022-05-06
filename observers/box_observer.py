import backtrader as bt

class BoxObserver(bt.Observer):
  lines = ('high', 'low')

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  def next(self):
    if self._owner.box_high > 0:
      p = self._owner.params.box_p
      for i in range(p):
        self.lines.high[0 - i] = self._owner.box_high
        self.lines.low[0 - i] = self._owner.box_low