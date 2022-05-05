from matplotlib.pyplot import subplot
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == '__main__':
  data = pd.read_csv('./support_test_result_trades-1.csv')
  # sns.relplot(data=data, x='id', y='profit_percent')
  # plt.show()

  data_group = data.groupby('stock_id', as_index=False).sum('profit_percent').sort_values(['profit_percent'], ascending=[False])
  print(data_group.loc[:, ['stock_id', 'profit_percent']].head(20))
  print(data_group.loc[:, ['stock_id', 'profit_percent']].tail(20))
  # sns.relplot(data=data_group.head(20), x='stock_id', y='profit_percent')
  # plt.show()

  # sns.relplot(data=data_group.tail(20), x='stock_id', y='profit_percent')
  # plt.show()
