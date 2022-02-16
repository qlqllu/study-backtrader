# Stats up/down percentage

import datetime
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == '__main__':

  result = dict(id=[])

  files = os.listdir('./stock_data')
  for file in files:
    stockId = file.split('.')[1]
    if stockId.startswith('3') or stockId.startswith('4') or stockId.startswith('8'):
      continue

    print('Load data ' + stockId)

    data = pd.read_csv('./stock_data/' + file, parse_dates=[1])

    date_3y_before = datetime.datetime.now() - datetime.timedelta(365*3)
    data = data[data['dt'] > date_3y_before]

    close = np.array(data.Close)
    low_price = np.max(close) * 0.2
    if low_price >= close[-1]:
      result['id'].append(stockId)

  resultData = pd.DataFrame(result)
  resultData.to_csv('./low_price.csv')
  plt.show()

