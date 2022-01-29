# Stats up/down percentage

import datetime
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def statOneStock(file):
  data = pd.read_csv(f'./stock_data/{file}', parse_dates=['dt'], index_col='dt')
  if (datetime.datetime.now() - data.index[0]).days < 365 * 2:
    return None

  weekData = data.resample('W').last()
  weekData.Open = data.Open.resample('W').first()
  weekData.Close = data.Close.resample('W').last()
  weekData.High = data.High.resample('W').max()
  weekData.Low = data.Low.resample('W').min()

  open = np.array(weekData.Open)
  close = np.array(weekData.Close)
  diff = close - open
  diff = diff / open * 100
  pUp = np.extract(diff > 0, diff)
  stat = np.quantile(pUp, [0.2, 0.5, 0.8])

  return stat


if __name__ == '__main__':

  result = dict(id=[], low=[], middle=[], high=[])

  files = os.listdir('./stock_data')
  i = 0
  for file in files:
    stockId = file.split('.')[1]
    if stockId.startswith('3') or stockId.startswith('4') or stockId.startswith('8'):
      continue

    print('Stat ' + stockId)

    stat = statOneStock(file)

    if stat is None:
      continue

    result['id'].append(stockId)
    result['low'].append(stat[0])
    result['middle'].append(stat[1])
    result['high'].append(stat[2])

  resultData = pd.DataFrame(result)
  resultData.to_csv('./up_stat_week.csv')
  sns.relplot(data=resultData, x='id', y='low')
  sns.relplot(data=resultData, x='id', y='middle')
  sns.relplot(data=resultData, x='id', y='high')
  plt.show()
      # sns.lineplot(data=data, x='dt', y='Close')
      # plt.show()

