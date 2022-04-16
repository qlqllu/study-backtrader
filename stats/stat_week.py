# Stats up/down percentage

import datetime
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data_folder = 'data_yw/zh_a/'

def statOneStock(file):
  data = pd.read_csv(f'{data_folder}/{file}', parse_dates=['date'], index_col='date')
  if (datetime.datetime.now() - data.index[0]).days < 365 * 2:
    return None

  weekData = data.resample('W').last()
  weekData.open = data.open.resample('W').first()
  weekData.close = data.close.resample('W').last()
  weekData.high = data.high.resample('W').max()
  weekData.low = data.low.resample('W').min()

  open = np.array(weekData.open)
  close = np.array(weekData.close)
  diff = close - open
  diff = diff / open * 100
  pUp = np.extract(diff > 0, diff)
  stat = np.quantile(pUp, [0.2, 0.6, 0.9])

  return stat


if __name__ == '__main__':

  result = dict(id=[], low=[], middle=[], high=[])

  files = os.listdir(data_folder)
  i = 0
  for file in files:
    stock_id = file.split('.')[0]
    if stock_id.startswith('sz3') or stock_id.startswith('bj4') or stock_id.startswith('bj8'):
      continue

    i += 1
    print(f'Stat {i}, {stock_id}')

    stat = statOneStock(file)

    if stat is None:
      continue

    result['id'].append(stock_id)
    result['low'].append(stat[0])
    result['middle'].append(stat[1])
    result['high'].append(stat[2])

  resultData = pd.DataFrame(result).sort_values(by='high', ascending=False)
  resultData.to_csv('./up_stat_week.csv')
  print(f'Top 5 high: {resultData.head(5)}')
  # sns.relplot(data=resultData, x='id', y='low')
  # sns.relplot(data=resultData, x='id', y='middle')
  # sns.relplot(data=resultData, x='id', y='high')
  # plt.show()
      # sns.lineplot(data=data, x='dt', y='Close')
      # plt.show()

