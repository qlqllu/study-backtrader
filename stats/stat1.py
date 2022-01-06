# Stats up/down percentage

import backtrader as bt
import datetime
import os.path as path
import numpy as np


class TestStrategy(bt.Strategy):
  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.pUp = []
    self.pDown = []

  def next(self):
    data = self.datas[0]
    if data.close[0] > data.open[0]:
      p = round((data.close[0] - data.open[0]) / data.open[0] * 100, 2)
      self.pUp.append(p)
    elif data.close[0] < data.open[0]:
      p = round((data.open[0] - data.close[0]) / data.open[0] * 100, 2)
      self.pDown.append(p)

  def stop(self):
    up = sorted(self.pUp)
    up_len = len(up)

    down = sorted(self.pDown)
    down_len = len(down)

    up_steps = list(map(lambda x: round(x), [up_len*.2, up_len*.4, up_len*.6, up_len*.8, up_len]))
    up_avg = []
    for i in range(len(up_steps)):
      if i == 0:
        s = np.mean(up[:up_steps[0]])
      else:
        s = np.mean(up[up_steps[i - 1]:up_steps[i]])
      up_avg.append(s)

    down_steps = list(map(lambda x: round(x), [down_len*.2, down_len*.4, down_len*.6, down_len*.8, down_len]))
    down_avg = []
    for i in range(len(down_steps)):
      if i == 0:
        s = np.mean(down[:down_steps[0]])
      else:
        s = np.mean(down[down_steps[i - 1]:down_steps[i]])
      down_avg.append(s)

    print(f'Up   avg: {list(map(lambda x: round(x, 2), up_avg))}')
    print(f'Down avg: {list(map(lambda x: round(x, 2), down_avg))}')
    print('-------------')
    print(f'Up max: {up[len(up) - 1]}')
    print(f'Down max: {down[len(down) -1]}')



if __name__ == '__main__':
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(100)

  for i in range(1, 2):
    fname = f'./stock_data/0.0000{i:0=2}.csv'
    if path.isfile(fname):
      data = bt.feeds.GenericCSVData(
        dataname=fname,
        datetime=1,
        open=2,
        close=3,
        high=4,
        low=5,
        volume=6,
        dtformat=('%Y-%m-%d'),
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2020, 4, 12)
      )
      # cerebro.adddata(data)
      cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)


  # Add a strategy
  cerebro.addstrategy(TestStrategy)

  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
