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


strategy_name = 'box_break_1'
begin_date = datetime.datetime(2010, 1, 1)
end_date = None
time_frame = 'w'
start_index = 0
end_index = 50
result_index = 2

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
  stock_list = stock_list[start_index:end_index]

  strategeParams = {'box_p': 0, 'box_os': 0}

  opt_stats = dict(id=[], box_p=[], box_os=[], profit_percent_per_year=[], max_loss_percent=[], max_drawdown_len=[], avg_drawdown_len=[])

  for box_p in range(4, 6, 1):
    for box_os in range(10, 100, 10):
      strategeParams['box_p'] = box_p
      strategeParams['box_os'] = box_os / 100
      print(f'---Test param {box_p}, {box_os}')
      trade_result, continue_drawdown_len, buy_last_bars = test_multiple_stocks(stock_list, Strategy, begin_date, end_date, time_frame, False, **strategeParams)
      resultStats, resultDf = analyze_trade_result(trade_result, time_frame, continue_drawdown_len)

      opt_stats['id'].append(f'{box_p}-{box_os}')
      opt_stats['box_p'].append(box_p)
      opt_stats['box_os'].append(box_os)
      opt_stats['profit_percent_per_year'].append(resultStats.profit_percent_per_year)
      opt_stats['max_loss_percent'].append(resultStats.max_loss_percent)
      opt_stats['max_drawdown_len'].append(resultStats.max_drawdown_len)
      opt_stats['avg_drawdown_len'].append(resultStats.avg_drawdown_len)

  optDf = pd.DataFrame(opt_stats)
  print_data = optDf.sort_values(['profit_percent_per_year'], ascending=[False]).head(5)
  print(f'Top profite {print_data}')
  optDf.to_csv(result_file)
