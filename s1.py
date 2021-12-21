# from __future__ import (absolute_import, division, print_function,
#                         unicode_literals)

import backtrader as bt
import datetime

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
      fromdate=datetime.datetime(2010, 1, 1),
      todate=datetime.datetime(2020, 4, 12)
  )
  cerebro.adddata(data)

  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
