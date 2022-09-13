import backtrader as bt
from strategies.base_strategy import BaseStrategy
import numpy as np
from sklearn import linear_model
import pandas as pd

reg = linear_model.LinearRegression()

class Strategy(BaseStrategy):
  params = (
  )

  def __init__(self):
    super().__init__()
    min, max = np.min(self.data.close), np.max(self.data.close)
    self.df = pd.DataFrame({'price_normal': (self.data.close.array - min) / (max - min)})
    # self.data['price_normal'] = (self.data.close - min) / (max - min)
    self.sl = 0
    self.s = 0
    self.is_falling = False

  def next(self):
    d = self.data
    self.dt = d.datetime.date(0).isoformat()

    if not self.should_continue_next():
      return

    if not self.position:
      if self.check_is_falling():
        self.is_falling = True
      else:
        if self.is_falling:
          self.buy()
          self.sl = d.low[-1]
          self.is_falling = False
    else:
      if d.close[0] < self.sl:
        self.sell()
        self.sl = 0
        self.s = len(self)
        return

      if d.close[0] > self.sl * 1.05:
        self.sl = self.sl * 1.05

  def check_is_falling(self):
    s = self.s
    e = len(self)
    p = e - s
    if p < 10:
      return False

    if not self.is_falling:
      self.s = self.s + 1

    data = self.df.iloc[s: e]

    train_X = np.array(range(p))
    train_Y = np.array(data.price_normal)
    reg.fit(train_X.reshape(-1, 1), train_Y)
    predict_Y = reg.predict(train_X.reshape(-1, 1))

    k = reg.coef_[0]
    model = f'model:{k}x+{reg.intercept_}'
    score = reg.score(train_X.reshape(-1, 1), train_Y)

    if k >= 0:
      return False

    if score > 0.9:
      return True





