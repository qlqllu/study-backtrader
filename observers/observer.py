import backtrader as bt

class MyObserver(bt.Observer):
  lines = ('a', 'b', 'c', 'd', 'e',)


  def _plotlabel(self):
    return list(map(lambda x: x['p'][3:], self.ob_props))

  def __init__(self) -> None:
    super().__init__()
    self.ob_props = []
    i = 0
    for p in dir(self._owner):
      if p.startswith('ob_'):
        line_name = self.lines._getlinealias(i)
        self.ob_props.append(dict(p = p, line=line_name))
        i += 1

  def next(self):
    for p in self.ob_props:
      if hasattr(self._owner, p['p']) and getattr(self._owner, p['p']) > 0:
        getattr(self.lines, p['line'])[0] = getattr(self._owner, p['p'])