import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == '__main__':

  data = pd.read_csv('./ma_test_result_trades.csv')
  sns.relplot(data=data, x='id', y='weeks')
  plt.show()

