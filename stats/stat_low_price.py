# Stats up/down percentage

import datetime
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == '__main__':

  result = dict(id=[], name=[])
  data_folder = 'F:\\DS\\C3-Data-Science\\backtest\\datas\\stock\\'

  stock_list = pd.read_csv(data_folder + 'zh_a_stock_list.csv', index_col=2, dtype={'代码': str})

  files = os.listdir(f'{data_folder}zh_a\\')
  i = 0
  for file in files:
    stock_id = file.split('.')[0]
    if not stock_id in stock_list.index.values:
      continue
    stock_name = stock_list.loc[stock_id, '名称']
    # if stockId.startswith('3') or stockId.startswith('4') or stockId.startswith('8'):
    #   continue

    i += 1
    print(f'Load data {i}: {stock_id}, {stock_name}')

    data = pd.read_csv(f'{data_folder}zh_a\\{file}', parse_dates=[1])

    date_3y_before = datetime.datetime.now() - datetime.timedelta(365*3)
    data = data[data['datetime'] > date_3y_before]

    if len(data) == 0:
      continue

    close = np.array(data.close)
    low_price = np.max(close) * 0.2
    if low_price >= close[-1]:
      result['id'].append(stock_id)
      result['name'].append(stock_name)

  resultData = pd.DataFrame(result)
  resultData.to_csv('./low_price.csv')
  plt.show()

