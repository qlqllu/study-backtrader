import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import importlib
import pathlib
import argparse
import os
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(prog = 'Strategy Runner', description = 'Run a strategy for back testing.')
parser.add_argument('-t', '--strategy', type=str, required=True)
parser.add_argument('-b', '--bdate', type=str, required=False)
parser.add_argument('-e', '--edate', type=str, required=False)
parser.add_argument('-f', '--time_frame', type=str, required=False, help='d,w,m')
parser.add_argument('-m', '--mode', type=str, required=False, help='b,l. b means back test, l means run last bar only.')
parser.add_argument('-n', '--num', type=int, required=False, help='Number stocks to test')
parser.add_argument('-r', '--result_num', type=int, required=False, help='Test result number')
args = parser.parse_args()

strategy_name = args.strategy
begin_date = datetime.datetime.fromisoformat(args.bdate) if args.bdate else datetime.datetime(2010, 1, 1)
end_date = datetime.datetime.fromisoformat(args.edate) if args.edate else None
time_frame = args.time_frame if args.time_frame else 'd'
test_num = args.num
result_num = args.result_num if args.result_num else 0
last_bar = True if args.mode == 'l' else False

root_path = pathlib.PurePath(__file__).parent
strategy_path = pathlib.Path(root_path, f'strategies/{strategy_name}/{strategy_name}.py')
if not strategy_path.exists():
  print(f'Strategy does not exist.{strategy_path}')
  exit()

data_folder = pathlib.Path(root_path, f'data_ln/zh_a')
if not data_folder.exists():
  print(f'Data folder not exist.{data_folder}')
  exit()

Strategy = importlib.import_module(f'strategies.{strategy_name}.{strategy_name}').Strategy

result_folder = pathlib.Path(root_path, f'results/{strategy_name}')
if not result_folder.exists():
  os.makedirs(result_folder)

def test_one_stock(stock_id):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
  cerebro.addstrategy(Strategy, last_bar=last_bar)
  stock_path = pathlib.Path(data_folder, f'{stock_id}.csv')

  data = bt.feeds.GenericCSVData(
      dataname=stock_path,
      datetime=0,
      open=1,
      high=2,
      low=3,
      close=4,
      volume=5,
      dtformat=('%Y-%m-%d'),
      fromdate=begin_date,
      todate=end_date
  )

  if time_frame == 'd':
    cerebro.adddata(data)
  elif time_frame == 'w':
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  elif time_frame == 'm':
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)

  start_value = cerebro.broker.getvalue()
  result = cerebro.run()
  return result[0].trades

if __name__ == '__main__':
  files = os.listdir(f'{data_folder}')
  result = dict(id=[], profit=[], profit_percent=[], days=[], profit_p_per_day=[], stock_id=[], sell_reason=[])
  i = 0
  stock_count = 0

  for file in files:
    stock_id = file.split('.')[0]

    # start with 3: 创业板
    # start with 8：新三板
    # start with 4: 三板
    if stock_id == '' or stock_id.startswith('sz3') or stock_id.startswith('bj4') or stock_id.startswith('bj8') or stock_id.startswith('qfq'):
      continue

    i += 1
    if test_num and i > test_num:
      continue

    print(f'Test {i}, {stock_id}')
    stock_count = i
    trades = test_one_stock(stock_id)

    for t in trades:
      result['id'].append(f'{stock_id}-{t.ref}')
      result['profit'].append(round(t.pnlcomm, 2))
      result['profit_percent'].append(round(t.profit_percent, 2))
      result['days'].append(t.barlen if t.barlen > 0 else 1)
      result['profit_p_per_day'].append(round(t.profit_percent/(t.barlen if t.barlen > 0 else 1), 2))
      result['stock_id'].append(stock_id)
      result['sell_reason'].append(t.sell_reason)

  resultData = pd.DataFrame(result)

  if len(resultData) == 0:
    print('No trade.')
    exit()

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

  data_group = resultData.groupby('stock_id', as_index=False).sum('profit_percent').sort_values(['profit_percent'], ascending=[False])
  top_stocks = data_group.loc[:, ['stock_id', 'profit_percent']].head(10)
  bottom_stocks = data_group.loc[:, ['stock_id', 'profit_percent']].tail(10)
  print(f'Top stocks: {top_stocks}')
  print(f'Bottom stocks: {bottom_stocks}')

  result_file = pathlib.Path(result_folder, f'{result_num}.csv')
  resultData.to_csv(result_file)

  # sns.relplot(data=resultData, x='id', y='profit_percent')
  # plt.show()