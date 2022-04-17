# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot

from strategy import MyStrategy
from sl_observer import SLObserver

if __name__ == '__main__':
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  # cerebro.broker.set_coo(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
  strats = cerebro.addstrategy(MyStrategy, log=True)
  cerebro.addobserver(SLObserver)

  data_folder = 'data_yw/zh_a/'

  data = bt.feeds.GenericCSVData(
      dataname=f'{data_folder}sz002105.csv',
      datetime=0,
      open=1,
      high=2,
      low=3,
      close=4,
      volume=5,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2015, 1, 1),
      # todate=datetime.datetime(2020, 1, 1)
  )
  cerebro.adddata(data)
  # cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)

  # 策略执行前的资金
  print('Starting Value: %.2f' % cerebro.broker.getvalue())

  result = cerebro.run()

  r1 = result[0]

  sum_p = 0
  for t in r1.trades:
    sum_p += t.profit_percent

  # 策略执行后的资金
  print(f'Final Value: {round(cerebro.broker.getvalue(), 2)}, percent%: {round(sum_p, 2)}')

  cerebro.plot(style='candle', barup='red', barupfill=False, bardown='green', plotdist=1, volume=True)