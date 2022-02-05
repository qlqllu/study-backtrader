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
  cerebro.run()
  return {
    'start_value': start_value,
    'final_value': int(cerebro.broker.getvalue()),
    'return_percent': round((cerebro.broker.getvalue() - start_value) / start_value * 100, 2)
  }

if __name__ == '__main__':
  files = os.listdir('./stock_data')
  i = 0
  result = dict(stock_id=[], start_value=[], final_value=[], return_percent=[])
  count = 0
  for file in files:
    stock_id = file.split('.')[1]
    if stock_id.startswith('3') or stock_id.startswith('4') or stock_id.startswith('8'):
      continue

    i += 1
    # if i > 200:
    #   continue

    print(f'Test {i}, {stock_id}')
    count = i
    one_result = test_one_stock(file)

    result['stock_id'].append(stock_id)
    result['start_value'].append(one_result['start_value'])
    result['final_value'].append(one_result['final_value'])
    result['return_percent'].append(one_result['return_percent'])

  resultData = pd.DataFrame(result)
  resultData.to_csv('./ma_test_result.csv')

  # summary
  sum = np.sum(resultData['return_percent'])
  earn = round(len(np.extract(resultData['return_percent'] > 0, resultData['return_percent']))/count*100, 2)
  loss = round(len(np.extract(resultData['return_percent'] < 0, resultData['return_percent']))/count*100, 2)

  print('---------------------')
  print(f'Sum return_percent: {sum}')
  print(f'Earn: {earn}')
  print(f'Loss: {loss}')
  sns.relplot(data=resultData, x='stock_id', y='return_percent')
  plt.show()