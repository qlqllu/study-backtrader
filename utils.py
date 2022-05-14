import datetime
import backtrader as bt
from matplotlib.pyplot import draw, subplot
import importlib
import pathlib
import argparse
import os
import numpy as np
import pandas as pd

root_path = pathlib.PurePath(__file__).parent
data_folder = pathlib.Path(root_path, f'data_ln/zh_a')
if not data_folder.exists():
  print(f'Data folder not exist.{data_folder}')
  exit()

def test_one_stock(stock_id, Strategy, begin_date, end_date, time_frame, last_bar, log, observers, **strategeParams):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
  strategeParams['log'] = log
  strategeParams['last_bar'] = last_bar
  cerebro.addstrategy(Strategy, **strategeParams)
  if observers:
    for observer in observers:
      cerebro.addobserver(observer)

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

  result = cerebro.run()
  return result[0].trades, result[0].buy_last_bar, cerebro

def test_multiple_stocks(stock_list, Strategy, begin_date, end_date, time_frame, last_bar, **strategeParams):
  trade_result = dict(id=[], profit=[], profit_percent=[], bars=[], profit_percent_per_bar=[], stock_id=[], sell_reason=[])
  continue_drawdown_len = [] # {stock_id, len}
  buy_last_bars = []

  i = 0
  for stock_id in stock_list:

    # start with 3: 创业板
    # start with 8：新三板
    # start with 4: 三板
    if stock_id == '' or stock_id.startswith('sz3') or stock_id.startswith('bj4') or stock_id.startswith('bj8') or stock_id.startswith('qfq'):
      continue

    i += 1
    print(f'Test {i}, {stock_id}')

    trades, buy_last_bar, cerebro = test_one_stock(stock_id, Strategy, begin_date, end_date, time_frame, last_bar, False, None, **strategeParams)

    if buy_last_bar:
      buy_last_bars.append(stock_id)

    is_drawdown = False
    drawdown_len = 0
    for t in trades:
      trade_result['id'].append(f'{stock_id}-{t.ref}')
      trade_result['profit'].append(round(t.pnlcomm, 2))
      trade_result['profit_percent'].append(round(t.profit_percent, 2))
      trade_result['bars'].append(t.barlen if t.barlen > 0 else 1)
      trade_result['profit_percent_per_bar'].append(round(t.profit_percent/(t.barlen if t.barlen > 0 else 1), 2))
      trade_result['stock_id'].append(stock_id)
      trade_result['sell_reason'].append(t.sell_reason)

      if t.profit_percent < 0:
        if is_drawdown:
          drawdown_len += 1
        else:
          is_drawdown = True
          drawdown_len = 1
      else:
        if is_drawdown:
          continue_drawdown_len.append({'stock_id': stock_id, 'len': drawdown_len})
          drawdown_len = 0

  return trade_result, continue_drawdown_len, buy_last_bars

def analyze_trade_result(trade_result, time_frame, continue_drawdown_len):
  resultDf = pd.DataFrame(trade_result)

  resultStats = TradesStats()

  if len(resultDf) == 0:
    print('No trade.')
    return resultStats, resultDf

  resultStats.trade_count = len(resultDf['profit'])
  resultStats.earn_trade_count = len(np.extract(resultDf['profit'] > 0, resultDf['profit']))
  resultStats.loss_trade_count = len(np.extract(resultDf['profit'] < 0, resultDf['profit']))
  resultStats.earn_percent = round(resultStats.earn_trade_count / (resultStats.earn_trade_count + resultStats.loss_trade_count) * 100, 2)

  resultStats.total_profit_percent = round(np.sum(resultDf['profit_percent']), 2)
  resultStats.total_cache_use = np.sum(resultDf['bars'])
  resultStats.profit_percent_per_bar = round(resultStats.total_profit_percent/resultStats.total_cache_use, 2)
  bar_size = 0
  if time_frame == 'd':
    bar_size = 250
  elif time_frame == 'w':
    bar_size = 50
  elif time_frame == 'm':
    bar_size = 12
  resultStats.profit_percent_per_year = resultStats.profit_percent_per_bar * bar_size

  resultStats.max_earn_percent = np.max(resultDf['profit_percent'])
  resultStats.max_loss_percent = np.min(resultDf['profit_percent'])


  resultStats.Profit_percent_per_trade = round(resultStats.total_profit_percent/resultStats.trade_count, 2)
  resultStats.earn_percent_per_trade = round(np.average(np.extract(resultDf['profit_percent'] > 0, resultDf['profit_percent'])), 2)
  resultStats.loss_percent_per_trade = round(np.average(np.extract(resultDf['profit_percent'] < 0, resultDf['profit_percent'])), 2)

  if len(continue_drawdown_len) > 0:
    max_drawdown_len = 0
    max_drawdown_stock = None
    for dd in continue_drawdown_len:
      if dd['len'] > max_drawdown_len:
        max_drawdown_len = dd['len']
        max_drawdown_stock = dd['stock_id']

    resultStats.avg_drawdown_len = round(np.average(list(map(lambda dd: dd['len'], continue_drawdown_len))), 2)
    resultStats.max_drawdown_len = max_drawdown_len
    resultStats.max_drawdown_stock = max_drawdown_stock

  resultStats.profit_distribution = np.quantile(resultDf['profit_percent'], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
  resultStats.profit_distribution = list(map(lambda x: round(x, 2), resultStats.profit_distribution))

  data_group = resultDf.groupby('stock_id', as_index=False).sum('profit_percent').sort_values(['profit_percent'], ascending=[False])
  resultStats.top5_profit_stocks = data_group.loc[:, ['stock_id', 'profit_percent']].head(5)
  resultStats.bottom5_profit_stocks = data_group.loc[:, ['stock_id', 'profit_percent']].tail(5)

  return resultStats, resultDf

class TradesStats:
  stock_count = 0

  trade_count = 0
  earn_trade_count = 0
  loss_trade_count = 0
  earn_percent = 0

  total_profit_percent = 0
  total_cache_use = 0
  max_earn_percent = 0
  max_loss_percent = 0

  profit_percent_per_bar = 0
  profit_percent_per_year = 0
  Profit_percent_per_trade = 0

  earn_percent_per_trade = 0
  loss_percent_per_trade = 0

  max_drawdown_len = 0
  max_drawdown_stock = ''
  avg_drawdown_len = 0

  profit_distribution = []
  top5_profit_stocks = None
  bottom5_profit_stocks = None


