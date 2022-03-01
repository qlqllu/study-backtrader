# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from rise_rate import FindRiseRateStrategy

# data_folder = 'F:\\DS\\C3-Data-Science\\backtest\\datas\\stock\\zh_a\\'
data_folder = 'E:\\github\\C3-Data-Science\\backtest\\datas\\stock\\zh_a\\'


def test_one_stock(stock_id):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  cerebro.addstrategy(FindRiseRateStrategy)

  data = bt.feeds.GenericCSVData(
      dataname=f'{data_folder}{stock_id}.csv',
      name=stock_id,
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2010, 1, 1),
      # todate=datetime.datetime(2020, 1, 1)
  )
  cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  start_value = cerebro.broker.getvalue()
  crosses = cerebro.run()[0].crosses
  for c in crosses:
    c['id'] = stock_id
  return crosses

if __name__ == '__main__':

  files = os.listdir(data_folder)
  i = 0
  stock_count = 0
  all_crosses = []
  for file in files:
    stock_id = file.split('.')[0]
    if stock_id.startswith('3') or stock_id.startswith('4') or stock_id.startswith('8'):
      continue

    i += 1
    # if i > 100:
    #   continue

    print(f'Test {i}, {stock_id}')
    stock_count = i
    crosses = test_one_stock(stock_id)
    all_crosses += crosses

  resultData = pd.DataFrame(all_crosses)
  resultData.to_csv('./rise_rate_all.csv')

  print('----------------')
  rise_avg = round(np.average(resultData['rise_rate%']), 2)
  rise_q258 = np.quantile(resultData['rise_rate%'], [0.2, 0.5, 0.8])
  rise_q258 = list(map(lambda x: round(x, 2), rise_q258))
  rise_data = sorted(list(map(lambda x: round(x, 2), resultData['rise_rate%'])))

  print(f'Rise rate avg: {rise_avg}')
  print(f'Rise rate 258: {rise_q258[0]}, {rise_q258[1]}, {rise_q258[2]}')
  # print(f'Rise rate:{rise_data}')

  print('----------------')
  down_up_avg = round(np.average(resultData['down_up%']), 2)
  down_up_q258 = np.quantile(resultData['down_up%'], [0.2, 0.5, 0.8])
  down_up_q258 = list(map(lambda x: round(x, 2), down_up_q258))
  down_up_data = sorted(list(map(lambda x: round(x, 2), resultData['down_up%'])))
  print(f'Down up avg: {down_up_avg}')
  print(f'Down up 258: {down_up_q258[0]}, {down_up_q258[1]}, {down_up_q258[2]}')
  # print(f'Down up:{down_up_data}')
  # sns.relplot(data=resultData, x='id', y='rise_rate%')
  # plt.show()