import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import importlib
import pathlib
import argparse
from observers.sl_observer import SLObserver
from observers.box_observer import BoxObserver

parser = argparse.ArgumentParser(prog = 'Strategy Runner', description = 'Run a strategy for back testing.')
parser.add_argument('-t', '--strategy', type=str, required=True)
parser.add_argument('-s', '--stock', type=str, required=True)
parser.add_argument('-b', '--bdate', type=str, required=False)
parser.add_argument('-e', '--edate', type=str, required=False)
parser.add_argument('-f', '--time_frame', type=str, required=False, help='d,w,m')
parser.add_argument('-m', '--mode', type=str, required=False, help='b,l. b means back test, l means run last bar only.')
args = parser.parse_args()

strategy_name = args.strategy
stock_id = args.stock
begin_date = datetime.datetime.fromisoformat(args.bdate) if args.bdate else datetime.datetime(2010, 1, 1)
end_date = datetime.datetime.fromisoformat(args.edate) if args.edate else None
time_frame = args.time_frame if args.time_frame else 'd'
last_bar = True if args.mode == 'l' else False

root_path = pathlib.PurePath(__file__).parent
strategy_path = pathlib.Path(root_path, f'strategies/{strategy_name}/{strategy_name}.py')
if not strategy_path.exists():
  print(f'Strategy does not exist.{strategy_path}')
  exit()

data_folder = pathlib.Path(root_path, f'data_ln/zh_a')
stock_path = pathlib.Path(data_folder, f'{stock_id}.csv')
if not stock_path.exists():
  print(f'Stock does not exist.{stock_path}')
  exit()

Strategy = importlib.import_module(f'strategies.{strategy_name}.{strategy_name}').Strategy

if __name__ == '__main__':
  cerebro = bt.Cerebro(preload=True)
  cerebro.broker.setcash(10000.0)
  cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
  strats = cerebro.addstrategy(Strategy, log=True, last_bar=last_bar)
  cerebro.addobserver(SLObserver)
  cerebro.addobserver(BoxObserver)

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
      todate=end_date,
  )
  if time_frame == 'd':
    cerebro.adddata(data)
  elif time_frame == 'w':
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)
  elif time_frame == 'm':
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)

  # 策略执行前的资金
  print('Starting Value: %.2f' % cerebro.broker.getvalue())
  result = cerebro.run()

  trades = result[0].trades
  sum_p = 0
  for t in trades:
    if not t.open_trade:
      print('Not find open trade.')
      continue

    sum_p += t.profit_percent

  # 策略执行后的资金
  print(f'Final Value: {round(cerebro.broker.getvalue(), 2)}, percent%: {round(sum_p, 2)}')

  cerebro.plot(style='candle', barup='red', barupfill=False, bardown='green', plotdist=1, volume=True)