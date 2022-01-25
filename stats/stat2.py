# Stats up/down percentage

import datetime
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# class TestStrategy(bt.Strategy):
#   def stop(self):
#     diff = np.array(self.data.close) - np.array(self.data.open)
#     self.pUp = np.extract(diff > 0, diff)
#     self.pDown = np.extract(diff < 0, diff)
#     print(f'Up: {np.quantile(self.pUp, [0.2, 0.4, 0.6, 0.8])}')
#     print(f'Down: {np.quantile(self.pDown, [0.2, 0.4, 0.6, 0.8])}')

if __name__ == '__main__':

  result = dict(id=[], low=[], middle=[], high=[])

  files = os.listdir('./stock_data')
  for file in files:
    stockId = file.split('.')[1]
    if stockId.startswith('3') or stockId.startswith('8'):
      continue

    print('Load data ' + stockId)
    data = pd.read_csv('./stock_data/' + file, parse_dates=[1])
    open = np.array(data.Open)
    close = np.array(data.Close)
    diff = close - open
    diff = diff / open * 100
    pUp = np.extract(diff > 0, diff)
    stat = np.quantile(pUp, [0.2, 0.5, 0.8])
    if stat[2] < 10:
      result['id'].append(stockId)
      result['low'].append(stat[0])
      result['middle'].append(stat[1])
      result['high'].append(stat[2])

  resultData = pd.DataFrame(result)
  resultData.to_csv('./up_stat.csv')
  sns.lineplot(data=resultData, x='id', y='low')
  sns.lineplot(data=resultData, x='id', y='middle')
  sns.lineplot(data=resultData, x='id', y='high')
  plt.show()
      # sns.lineplot(data=data, x='dt', y='Close')
      # plt.show()

