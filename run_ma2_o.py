import datetime
import backtrader as bt
from matplotlib.pyplot import draw, subplot
import importlib
import pathlib
import argparse
import os
import numpy as np
import pandas as pd
from utils import test_multiple_stocks, analyze_trade_result, get_test_stocks

strategy_name = 'ma2'
begin_date = datetime.datetime(2000, 1, 1)
end_date = None
time_frame = 'w'
start_index = 0
end_index = 50
result_index = 1

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
result_file = pathlib.Path(result_folder, f'opt-{result_index}.csv')

if __name__ == '__main__':
  files = os.listdir(f'{data_folder}')

  stock_list = list(map(lambda file: file.split('.')[0], files))
  end_index = end_index if end_index > 0 else len(stock_list)

  test_stocks = get_test_stocks(stock_list, end_index - start_index - 1)

  opt_stats = dict(
    id=[], profit_percent_per_year=[], max_loss_percent=[], max_drawdown_len=[], avg_drawdown_len=[], earn_percent=[],

    ma_period1=[],
    ma_period2=[],
    ma1_ma2_diff_percent=[],
    cross_up_high_percent=[],
    start_move_sl_percent=[],
    move_sl_step=[]
  )

  def run(id):
    print(f'---Test param {strategeParams}')
    trade_result, continue_drawdown_len, buy_last_bars = test_multiple_stocks(test_stocks, Strategy, begin_date, end_date, time_frame, False, **strategeParams)
    resultStats, resultDf = analyze_trade_result(trade_result, time_frame, continue_drawdown_len)

    opt_stats['id'].append(id)
    opt_stats['profit_percent_per_year'].append(resultStats.profit_percent_per_year)
    opt_stats['max_loss_percent'].append(resultStats.max_loss_percent)
    opt_stats['max_drawdown_len'].append(resultStats.max_drawdown_len)
    opt_stats['avg_drawdown_len'].append(resultStats.avg_drawdown_len)
    opt_stats['earn_percent'].append(resultStats.earn_percent)

    opt_stats['ma_period1'].append(strategeParams['ma_period1'])
    opt_stats['ma_period2'].append(strategeParams['ma_period2'])
    opt_stats['ma1_ma2_diff_percent'].append(strategeParams['ma1_ma2_diff_percent'])
    opt_stats['cross_up_high_percent'].append(strategeParams['cross_up_high_percent'])
    opt_stats['start_move_sl_percent'].append(strategeParams['start_move_sl_percent'])
    opt_stats['move_sl_step'].append(strategeParams['move_sl_step'])

  strategeParams = {'ma_period1': 10, 'ma_period2': 60, 'ma1_ma2_diff_percent': 0, 'cross_up_high_percent': 0, 'start_move_sl_percent': 0, 'move_sl_step': 0}

  count = 0
  for ma1_ma2_diff_percent in range(1, 2, 1):
    for cross_up_high_percent in range(40, 51, 5):
      for start_move_sl_percent in range(50, 101, 20):
        for move_sl_step in range(10, 50, 10):
          strategeParams['ma1_ma2_diff_percent'] = ma1_ma2_diff_percent / 100
          strategeParams['cross_up_high_percent'] = cross_up_high_percent / 100
          strategeParams['start_move_sl_percent'] = start_move_sl_percent / 100
          strategeParams['move_sl_step'] = move_sl_step
          count += 1
          run(count)

  optDf = pd.DataFrame(opt_stats)
  print_data = optDf.sort_values(['profit_percent_per_year'], ascending=[False]).head(5)
  print(f'Top profite {print_data}')
  optDf.to_csv(result_file)

