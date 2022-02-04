# Try indicators

import backtrader as bt
import datetime

from matplotlib.pyplot import subplot

class TestStrategy(bt.Strategy):
  def log(self, txt, dt=None):
    ''' Logging function for this strategy'''
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    self.highest = bt.indicators.Highest(self.data, period=10, subplot=False)

if __name__ == '__main__':
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(100)

  data = bt.feeds.GenericCSVData(
      dataname='./stock_data/0.000001.csv',
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2019, 1, 1),
      todate=datetime.datetime(2020, 4, 12)
  )
  cerebro.adddata(data)

  # Add a strategy
  cerebro.addstrategy(TestStrategy)

  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.plot(style='candle', barup='red', barupfill=False, bardown='green', plotdist=1, volume=False)
