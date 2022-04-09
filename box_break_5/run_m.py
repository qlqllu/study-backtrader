# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import os
import seaborn as sns
import matplotlib.pyplot as plt
from strategy import MyStrategy
import pandas as pd
import numpy as np

# data_folder = 'F:\\DS\\C3-Data-Science\\backtest\\datas\\stock\\'
# data_folder = 'E:\\github\\C3-Data-Science\\backtest\\datas\\stock\\'
data_folder = '/Users/juns6831/DS/zh_a/hfq/'


def test_one_stock(stock_id):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  cerebro.addstrategy(MyStrategy)

  data = bt.feeds.GenericCSVData(
      dataname=f'{data_folder}{stock_id}.csv',
      name=stock_id,
      datetime=0,
      open=1,
      high=2,
      low=3,
      close=4,
      volume=5,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2018, 1, 1),
      # todate=datetime.datetime(2020, 1, 1)
  )
  cerebro.adddata(data)
  # cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  start_value = cerebro.broker.getvalue()
  result = cerebro.run()
  return result[0].trades

if __name__ == '__main__':

  files = os.listdir(f'{data_folder}')
  i = 0
  result = dict(id=[], profit=[], profit_percent=[], days=[], profit_p_per_day=[], sell_reason=[])
  stock_count = 0

  for file in files:
    stock_id = file.split('.')[0]

    # start with 3: 创业板
    # start with 8：新三板
    # start with 4: 三板
    if stock_id.startswith('sz3') or stock_id.startswith('bj4') or stock_id.startswith('bj8'):
      continue

    i += 1
    # if i > 100:
    #   continue

    print(f'Test {i}, {stock_id}')
    stock_count = i
    trades = test_one_stock(stock_id)

    for t in trades:
      result['id'].append(f'{stock_id}-{t.ref}')
      result['profit'].append(round(t.pnlcomm, 2))
      result['profit_percent'].append(round(t.profit_percent, 2))
      result['days'].append(t.barlen if t.barlen > 0 else 1)
      result['profit_p_per_day'].append(round(t.profit_percent/(t.barlen if t.barlen > 0 else 1), 2))
      result['sell_reason'].append(t.sell_reason)

  resultData = pd.DataFrame(result)

  # summary
  print('---------------------')
  trade_count = len(resultData['profit'])
  earn_trade_count = len(np.extract(resultData['profit'] > 0, resultData['profit']))
  loss_trade_count = len(np.extract(resultData['profit'] < 0, resultData['profit']))
  earn_loss_rate = round(earn_trade_count / (earn_trade_count + loss_trade_count) * 100, 2)
  print(f'{stock_count} stocks, {trade_count} trades. {earn_trade_count} earns, {loss_trade_count} losses, {earn_loss_rate}% Eean/Loss')

  profit_sum = round(np.sum(resultData['profit_percent']), 2)
  max_earn = np.max(resultData['profit_percent'])
  max_loss = np.min(resultData['profit_percent'])
  print(f'Total profit%: {profit_sum}, max_earn%: {max_earn}, max_loss%: {max_loss}')

  total_cache_use = np.sum(resultData['days'])
  profit_per_day = round(profit_sum/total_cache_use, 2)
  print(f'Profit per day%: {profit_per_day}')

  profit_p_per_day = round(np.average(resultData['profit_p_per_day']), 2)
  print(f'profit_per_day_avg%: {profit_p_per_day}')

  profit_per_trade = round(profit_sum/trade_count, 2)
  earn_per_trade = round(np.average(np.extract(resultData['profit_percent'] > 0, resultData['profit_percent'])), 2)
  loss_per_trade = round(np.average(np.extract(resultData['profit_percent'] < 0, resultData['profit_percent'])), 2)
  print(f'Profit per trade%: {profit_per_trade}, Earn per trade%: {earn_per_trade}, Loss per trade%:{loss_per_trade}')

  # s1_sell = len(np.extract(resultData['sell_reason'] == 'S1', resultData['sell_reason']))
  # s2_sell = len(np.extract(resultData['sell_reason'] == 'S2', resultData['sell_reason']))
  # sl_sell = len(np.extract(resultData['sell_reason'] == 'SL', resultData['sell_reason']))
  # print(f'S1 sells: {s1_sell}, S2 sells: {s2_sell}, SL sells: {sl_sell}')

  profit_dist = np.quantile(resultData['profit_percent'], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
  profit_dist = list(map(lambda x: round(x, 2), profit_dist))
  print(f'Profit distribute: {profit_dist}')

  resultData.to_csv('./box_break_test_result_trades-5.csv')

  sns.relplot(data=resultData, x='id', y='profit_percent')
  plt.show()