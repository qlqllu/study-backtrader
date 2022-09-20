import datetime
import backtrader as bt
from matplotlib.pyplot import draw, subplot
import importlib
import pathlib
import argparse
import os
import numpy as np
import pandas as pd
from utils import test_multiple_stocks, analyze_trade_result

parser = argparse.ArgumentParser(prog = 'Strategy Runner', description = 'Run a strategy for back testing.')
parser.add_argument('-t', '--strategy', type=str, required=True)
parser.add_argument('-b', '--bdate', type=str, required=False)
parser.add_argument('-e', '--edate', type=str, required=False)
parser.add_argument('-f', '--time_frame', type=str, required=False, help='d,w,m')
parser.add_argument('-m', '--mode', type=str, required=False, help='b,l. b means back test, l means run last bar only.')
parser.add_argument('-i', '--start_index', type=int, required=False, help='Start index')
parser.add_argument('-j', '--end_index', type=int, required=False, help='End index')
parser.add_argument('-r', '--result_num', type=int, required=False, help='Test result number')
args = parser.parse_args()

strategy_name = args.strategy
begin_date = datetime.datetime.fromisoformat(args.bdate) if args.bdate else datetime.datetime(2010, 1, 1)
end_date = datetime.datetime.fromisoformat(args.edate) if args.edate else None
time_frame = args.time_frame if args.time_frame else 'd'
start_index = args.start_index if args.start_index else 0
end_index = args.end_index
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

if __name__ == '__main__':
  files = os.listdir(f'{data_folder}')

  stock_list = list(map(lambda file: file.split('.')[0], files))
  end_index = end_index if end_index else len(stock_list)

  stock_num = end_index - start_index
  test_stocks = []
  for i in range(0, len(stock_list)):
    # start with 3: 创业板
    # start with 8：新三板
    # start with 4: 三板
    stock_id = stock_list[i]
    if stock_id == '' or stock_id.startswith('sz3') or stock_id.startswith('bj4') or stock_id.startswith('bj8') or stock_id.startswith('qfq'):
      continue
    test_stocks.append(stock_id)

    if len(test_stocks) > stock_num:
      break

  trade_result, continue_drawdown_len, buy_last_bars = test_multiple_stocks(test_stocks, Strategy, begin_date, end_date, time_frame, last_bar)

  resultStats, resultDf = analyze_trade_result(trade_result, time_frame, continue_drawdown_len)

  resultStats.stock_count = len(stock_list)
  if len(buy_last_bars) > 0:
    print(f'Find stocks: {buy_last_bars}')
    exit()

  if resultStats.trade_count == 0:
    print('No trade.')
    exit()

  # summary
  print(f'''
  ------------------Trade stats-------------
  {resultStats.stock_count} stocks, {resultStats.trade_count} trades. {resultStats.earn_trade_count} earns, {resultStats.loss_trade_count} losses, {resultStats.earn_percent}% Eean.
  Total profit%: {resultStats.total_profit_percent}, max_earn%: {resultStats.max_earn_percent}, max_loss%: {resultStats.max_loss_percent}
  Profit per bar%: {resultStats.profit_percent_per_bar}, Profit per year%: {resultStats.profit_percent_per_year}
  Profit per trade%: {resultStats.Profit_percent_per_trade}, Earn per trade%: {resultStats.earn_percent_per_trade}, Loss per trade%:{resultStats.loss_percent_per_trade}
  Max drawdown len: {resultStats.max_drawdown_len} on stock {resultStats.max_drawdown_stock}, avg drawdown len: {resultStats.avg_drawdown_len}
  ---- Distribution:
  Profit distribution: {resultStats.profit_distribution}
  Top stocks: {resultStats.top5_profit_stocks}
  Bottom stocks: {resultStats.bottom5_profit_stocks}
  ''')

  result_file = pathlib.Path(result_folder, f'{result_num}.csv')
  resultDf.to_csv(result_file)
