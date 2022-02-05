# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import os
import seaborn as sns
import matplotlib.pyplot as plt
from ma.ma import MAStrategy
import pandas as pd
import numpy as np

def test_one_stock(file):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  cerebro.addstrategy(MAStrategy)

  stock_id = file.split('.')[1]

  data = bt.feeds.GenericCSVData(
      dataname=f'./stock_data/{file}',
      name=stock_id,
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2010, 1, 1),
      todate=datetime.datetime(2020, 1, 1)
  )
  cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  start_value = cerebro.broker.getvalue()
  result = cerebro.run()
  return result[0].trades

if __name__ == '__main__':
  files = os.listdir('./stock_data')
  i = 0
  result = dict(id=[], profit=[], weeks=[], profit_per_week=[])
  stock_count = 0
  for file in files:
    stock_id = file.split('.')[1]
    if stock_id.startswith('3') or stock_id.startswith('4') or stock_id.startswith('8'):
      continue

    i += 1
    if i > 100:
      continue

    print(f'Test {i}, {stock_id}')
    stock_count = i
    trades = test_one_stock(file)

    for t in trades:
      result['id'].append(f'{stock_id}-{t.ref}')
      result['profit'].append(round(t.pnlcomm, 2))
      result['weeks'].append(t.barlen)
      result['profit_per_week'].append(round(t.pnlcomm/t.barlen, 2))

  resultData = pd.DataFrame(result)
  resultData.to_csv('./ma_test_result_trades.csv')

  # summary
  profit_sum = np.sum(resultData['profit'])
  profit_avg = np.average(resultData['profit'])
  profit_per_week_avg = np.average(resultData['profit_per_week'])
  trade_count = len(resultData['profit'])
  max_earn = np.max(resultData['profit'])
  max_loss = np.min(resultData['profit'])
  total_cache_use = np.sum(resultData['weeks'])

  print('---------------------')
  print(f'{stock_count} stocks, {trade_count} trades.')
  print(f'profit_sum: {profit_sum}')
  print(f'profit_avg: {profit_avg}')
  print(f'profit_per_week_avg: {profit_per_week_avg}')
  print(f'max_earn: {max_earn}')
  print(f'max_loss: {max_loss}')
  print(f'total_cache_use(weeks): {total_cache_use}')
  sns.relplot(data=resultData, x='id', y='profit')
  plt.show()