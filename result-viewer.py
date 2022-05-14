from matplotlib.pyplot import subplot
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == '__main__':
  data = pd.read_csv('./results/box_break_1/opt.csv')

  data = data.sort_values(['profit_percent_per_year'], ascending=[False])
  print(data.loc[:, ['id', 'profit_percent_per_year']].head(20))
  sns.relplot(data=data.head(20), x='id', y='profit_percent_per_year')
  plt.show()

