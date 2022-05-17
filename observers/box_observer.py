import backtrader as bt

class BoxObserver(bt.Observer):
  lines = ('high', 'low', 'moving_high', 'moving_low')

  plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)

  def next(self):
    if hasattr(self._owner, 'box_high') and self._owner.box_high > 0:
      if hasattr(self._owner.params, 'box_p'):
        p = self._owner.params.box_p
        for i in range(p):
          self.lines.high[0 - i] = self._owner.box_high
          self.lines.low[0 - i] = self._owner.box_low
      else:
        self.lines.high[0] = self._owner.box_high
        self.lines.low[0] = self._owner.box_low

    if hasattr(self._owner, 'moving_box_high') and self._owner.moving_box_high > 0:
      self.lines.moving_high[0] = self._owner.moving_box_high
      self.lines.moving_low[0] = self._owner.moving_box_low