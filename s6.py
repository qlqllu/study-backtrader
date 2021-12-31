
import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import backtrader.indicators as btind
# Create a Stratey


class TestStrategy(bt.Strategy):

  def __init__(self):

    self.sma = sma = btind.SimpleMovingAverage(self.data, period=5)

    close_over_sma = self.data.close > sma
    self.sma_dist_to_high = sma_dist_to_high = self.data.high - sma

    sma_dist_small = sma_dist_to_high < 3.5

    # Unfortunately "and" cannot be overridden in Python being
    # a language construct and not an operator and thus a
    # function has to be provided by the platform to emulate it

    self.sell_sig = bt.And(close_over_sma, sma_dist_small)

  def next(self):

    # Although this does not seem like an "operator" it actually is
    # in the sense that the object is being tested for a True/False
    # response

    if self.sma > 30.0:
      print('sma is greater than 30.0')

    if self.sma > self.data.close:
      print('sma is above the close price')

    if self.sell_sig:  # if sell_sig == True: would also be valid
      print('sell sig is True')
    else:
      print('sell sig is False')

    if self.sma_dist_to_high > 5.0:
      print('distance from sma to hig is greater than 5.0')


if __name__ == '__main__':
  # 初始化模型
  cerebro = bt.Cerebro()
  # 设定初始资金
  cerebro.broker.setcash(10000.0)
  # 佣金
  cerebro.broker.setcommission(0.0005)
  # 设定需要设定每次交易买入的股数
  cerebro.addsizer(bt.sizers.FixedSize, stake=100)
  # 构建策略
  strats = cerebro.addstrategy(TestStrategy)

  data = bt.feeds.GenericCSVData(
      dataname='./stock_data/0.000001.csv',
      datetime=1,
      open=2,
      close=3,
      high=4,
      low=5,
      volume=6,
      dtformat=('%Y-%m-%d'),
      fromdate=datetime.datetime(2000, 1, 4),
      todate=datetime.datetime(2000, 1, 30)
  )
  cerebro.adddata(data)

  # 策略执行前的资金
  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  # 策略执行后的资金
  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
