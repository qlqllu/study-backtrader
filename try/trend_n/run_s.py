# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot

from ma import MAStrategy
from trend_n_observer import TrendNObserver

if __name__ == '__main__':
  cerebro = bt.Cerebro(stdstats=False)
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  strats = cerebro.addstrategy(MAStrategy)
  cerebro.addobserver(TrendNObserver)

  # data_folder = 'F:\\DS\\C3-Data-Science\\backtest\\datas\\stock\\zh_a\\'
  data_folder = '/Users/juns6831/DS/zh_a/hfq/'


  data = bt.feeds.GenericCSVData(
      dataname=f'{data_folder}sh600684.csv',
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
  # cerebro.adddata(data)
  cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)

  # 策略执行前的资金
  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  result = cerebro.run()

  r1 = result[0]

  # 策略执行后的资金
  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.plot(style='candle', barup='red', barupfill=False, bardown='green', plotdist=1, volume=False)