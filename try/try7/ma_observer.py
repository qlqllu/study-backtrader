import backtrader as bt

class MAObserver(bt.Observer):
  lines = ('ma',)

  plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)

  def next(self):
    self.lines.ma[0] = self._owner.ma2_direction