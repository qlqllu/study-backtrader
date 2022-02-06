# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import os
import seaborn as sns
import matplotlib.pyplot as plt
from ma.ma import MAStrategy
import pandas as pd
import numpy as np

def test_one_stock(file):
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  cerebro.addstrategy(MAStrategy)

  stock_id = file.split('.')[1]

  data = bt.feeds.GenericCSVData(
      dataname=f'./stock_data/{file}',
      name=stock_id,
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2010, 1, 1),
      todate=datetime.datetime(2020, 1, 1)
  )
  cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  start_value = cerebro.broker.getvalue()
  result = cerebro.run()
  return result[0].trades

hs300 = [
  '688981', '688599', '688561', '688396', '688363', '688169', '688126', '688111', '688036', '688012', '688009', '688008', '605499', '603993', '603986', '603939', '603899', '603882', '603833', '603806', '603799', '603659', '603658', '603517', '603501', '603486', '603392', '603369', '603338', '603288', '603260', '603259', '603233', '603195', '603160', '603087', '603019', '601998', '601995', '601990', '601989', '601988', '601985', '601966', '601939', '601933', '601919', '601916', '601901', '601899',
  '601898', '601888', '601881', '601878', '601877', '601868', '601865', '601857', '601838', '601818', '601816', '601808', '601800', '601799', '601788', '601766', '601728', '601698', '601696', '601688', '601669', '601668', '601658', '601633', '601628', '601618', '601607', '601601', '601600', '601398', '601390', '601377', '601360', '601336', '601328', '601319', '601318', '601288', '601238', '601236', '601231', '601229', '601225', '601216', '601211', '601186', '601169', '601166', '601162', '601155',
  '601138', '601111', '601108', '601100', '601088', '601066', '601021', '601012', '601009', '601006', '600999', '600989', '600958', '600926', '600919', '600918', '600905', '600900', '600893', '600887', '600886', '600872', '600848', '600845', '600837', '600809', '600795', '600763', '600760', '600745', '600741', '600690', '600660', '600655', '600606', '600600', '600588', '600585', '600584', '600570', '600547', '600519', '600489', '600438', '600436', '600426', '600406', '600383', '600362', '600352',
  '600346', '600332', '600309', '600276', '600196', '600183', '600176', '600161', '600150', '600143', '600132', '600115', '600111', '600109', '600104', '600085', '600079', '600061', '600050', '600048', '600036', '600031', '600030', '600029', '600028', '600025', '600019', '600018', '600016', '600015', '600011', '600010', '600009', '600000', '300999', '300896', '300888', '300866', '300782', '300760', '300759', '300750', '300677', '300676', '300628', '300601', '300595', '300558', '300529', '300498',
  '300450', '300433', '300413', '300408', '300347', '300316', '300274', '300144', '300142', '300124', '300122', '300059', '300033', '300015', '300014', '300003', '003816', '002938', '002916', '002841', '002821', '002812', '002791', '002736', '002714', '002709', '002624', '002607', '002602', '002601', '002600', '002594', '002568', '002555', '002493', '002475', '002466', '002460', '002459', '002415', '002414', '002410', '002371', '002352', '002311', '002304', '002271', '002252', '002241', '002236',
  '002230', '002202', '002179', '002157', '002142', '002129', '002120', '002064', '002050', '002049', '002044', '002032', '002027', '002024', '002008', '002007', '002001', '001979', '000977', '000963', '000938', '000895', '000876', '000858', '000800', '000786', '000783', '000776', '000768', '000725', '000708', '000703', '000661', '000651', '000625', '000596', '000568', '000538', '000425', '000338', '000333', '000301', '000166', '000157', '000100', '000069', '000066', '000063', '000002', '000001'
]
if __name__ == '__main__':
  files = os.listdir('./stock_data')
  i = 0
  result = dict(id=[], profit=[], weeks=[], profit_per_week=[])
  stock_count = 0
  for file in files:
    stock_id = file.split('.')[1]
    if stock_id.startswith('3') or stock_id.startswith('4') or stock_id.startswith('8'):
      continue

    i += 1
    # if i > 10:
    #   continue

    if not stock_id in hs300:
      continue

    print(f'Test {i}, {stock_id}')
    stock_count = i
    trades = test_one_stock(file)

    for t in trades:
      result['id'].append(f'{stock_id}-{t.ref}')
      result['profit'].append(round(t.pnlcomm, 2))
      result['weeks'].append(t.barlen)
      result['profit_per_week'].append(round(t.pnlcomm/t.barlen, 2))

  resultData = pd.DataFrame(result)
  resultData.to_csv('./ma_test_result_trades_hs300.csv')

  # summary
  profit_sum = np.sum(resultData['profit'])
  profit_avg = np.average(resultData['profit'])
  profit_per_week_avg = np.average(resultData['profit_per_week'])
  trade_count = len(resultData['profit'])
  earn_trade_count = len(np.extract(resultData['profit'] > 0, resultData['profit']))
  loss_trade_count = len(np.extract(resultData['profit'] < 0, resultData['profit']))
  max_earn = np.max(resultData['profit'])
  max_loss = np.min(resultData['profit'])
  total_cache_use = np.sum(resultData['weeks'])

  print('---------------------')
  print(f'{stock_count} stocks, {trade_count} trades. {earn_trade_count} earns, {loss_trade_count} losses')
  print(f'profit_sum: {profit_sum}')
  print(f'profit_avg: {profit_avg}')
  print(f'profit_per_week_avg: {profit_per_week_avg}')
  print(f'max_earn: {max_earn}')
  print(f'max_loss: {max_loss}')
  print(f'total_cache_use(weeks): {total_cache_use}')
  sns.relplot(data=resultData, x='id', y='profit')
  plt.show()