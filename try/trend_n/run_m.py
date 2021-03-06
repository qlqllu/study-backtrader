# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import os
import seaborn as sns
import matplotlib.pyplot as plt
from ma import MAStrategy
import pandas as pd
import numpy as np

data_folder = 'F:\\DS\\C3-Data-Science\\backtest\\datas\\stock\\'

def test_one_stock(stock_id):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  cerebro.addstrategy(MAStrategy)

  data = bt.feeds.GenericCSVData(
      dataname=f'{data_folder}zh_a\\{stock_id}.csv',
      name=stock_id,
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2015, 1, 1),
      # todate=datetime.datetime(2020, 1, 1)
  )
  cerebro.adddata(data)
  cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  start_value = cerebro.broker.getvalue()
  result = cerebro.run()
  return result[0].trades

if __name__ == '__main__':

  files = os.listdir(f'{data_folder}zh_a\\')
  i = 0
  result = dict(id=[], profit=[], weeks=[], profit_per_week=[])
  stock_count = 0

  stock_list = pd.read_csv(data_folder + 'zh_a_stock_list.csv', index_col=2, dtype={'代码': str})

  for file in files:
    stock_id = file.split('.')[0]

    if not stock_id in stock_list.index.values:
      continue

    if stock_id.startswith('3') or stock_id.startswith('4') or stock_id.startswith('8'):
      continue

    i += 1
    if i > 50:
      continue

    print(f'Test {i}, {stock_id}')
    stock_count = i
    trades = test_one_stock(stock_id)

    for t in trades:
      result['id'].append(f'{stock_id}-{t.ref}')
      result['profit'].append(round(t.pnlcomm, 2))
      result['weeks'].append(t.barlen if t.barlen > 0 else 1)
      result['profit_per_week'].append(round(t.pnlcomm/(t.barlen if t.barlen > 0 else 1), 2))

  resultData = pd.DataFrame(result)
  resultData.to_csv('./ma_test_result_trades-3.csv')

  # summary
  profit_sum = np.sum(resultData['profit'])
  profit_avg = np.average(resultData['profit'])
  profit_per_week_avg = np.average(resultData['profit_per_week'])
  trade_week_avg = np.average(resultData['weeks'])
  profit_per_week_avg_2 = round(profit_avg/trade_week_avg, 2)
  trade_count = len(resultData['profit'])
  earn_trade_count = len(np.extract(resultData['profit'] > 0, resultData['profit']))
  loss_trade_count = len(np.extract(resultData['profit'] < 0, resultData['profit']))
  max_earn = np.max(resultData['profit'])
  max_loss = np.min(resultData['profit'])
  total_cache_use = np.sum(resultData['weeks'])

  print('---------------------')
  print(f'{stock_count} stocks, {trade_count} trades. {earn_trade_count} earns, {loss_trade_count} losses')
  print(f'profit_sum: {profit_sum}')
  print(f'profit_avg: {profit_avg}')
  print(f'trade_week_avg: {trade_week_avg}')
  print(f'profit_per_week_avg: {profit_per_week_avg}')
  print(f'profit_per_week_avg_2: {profit_per_week_avg_2}')
  print(f'max_earn: {max_earn}')
  print(f'max_loss: {max_loss}')
  print(f'total_cache_use(weeks): {total_cache_use}')
  sns.relplot(data=resultData, x='id', y='profit')
  plt.show()