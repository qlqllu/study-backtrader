from gc import is_finalized
import backtrader as bt
import numpy as np
from sklearn import linear_model
import pandas as pd

reg = linear_model.LinearRegression()

class FallIndicator(bt.Indicator):
    lines = ('falling', 'price')

    params = (
      ('period', 10),
      ('k', 0)
    )

    def __init__(self):
      self.addminperiod(self.p.period)

      # price = np.array(self.data.open + self.data.close + self.data.high + self.data.low)/4
      min, max = np.min(self.data.close), np.max(self.data.close)
      self.df = pd.DataFrame({'price_normal': (self.data.close.array - min) / (max - min)})

      self.s = 0
      self.is_falling = False

    def next(self):
      if len(self.data.datetime.array) < self.p.period:
        return

      self.dt = self.data.datetime.date(0).isoformat()

      s = self.s
      e = len(self)
      p = e - s
      if p < self.p.period:
        return

      data = self.df.iloc[s: e]

      train_X = np.array(range(p))
      train_Y = np.array(data.price_normal)
      reg.fit(train_X.reshape(-1, 1), train_Y)
      predict_Y = reg.predict(train_X.reshape(-1, 1))

      k = reg.coef_[0]
      model = f'model:{k}x+{reg.intercept_}'
      score = reg.score(train_X.reshape(-1, 1), train_Y)

      if score < 0.8 or k > self.p.k: # not falling
        if self.is_falling:
          self.s = self.s + p
        else:
          self.s = self.s + 1

        self.lines.falling[0 - p] = self.is_falling
        self.is_falling = False
      else:
        self.is_falling = True
        # print(f'k: {k}')
        for i, v in enumerate(predict_Y):
          self.lines.price[0 - (p - i - 1)] = v
          self.lines.falling[0 - (p - i - 1)] = self.is_falling
