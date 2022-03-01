# use MA cross to buy/sell
import datetime
import backtrader as bt
from matplotlib.pyplot import subplot
import pandas as pd

from rise_rate import FindRiseRateStrategy

if __name__ == '__main__':
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  strats = cerebro.addstrategy(FindRiseRateStrategy)

  data_folder = 'E:\\github\\C3-Data-Science\\backtest\\datas\\stock\\zh_a\\'

  data = bt.feeds.GenericCSVData(
      dataname=f'{data_folder}002625.csv',
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2010, 1, 1),
      # todate=datetime.datetime(2020, 1, 1)
  )
  # cerebro.adddata(data)
  # cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
  cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)

  # 策略执行前的资金
  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  result = cerebro.run()

  r1 = result[0].crosses

  resultData = pd.DataFrame(r1)
  resultData.to_csv('./rise_rate.csv')

  # 策略执行后的资金
  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.plot(style='candle', barup='red', barupfill=False, bardown='green', plotdist=1, volume=False)