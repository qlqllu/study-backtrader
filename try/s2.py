# Strategy supports buy and sell, with param

import backtrader as bt
import datetime

class TestStrategy(bt.Strategy):
  params = (
    ('exitbars', 5),
  )

  def log(self, txt, dt=None):
    ''' Logging function for this strategy'''
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    # Keep a reference to the "close" line in the data[0] dataseries
    self.dataclose = self.datas[0].close
    self.order = None

  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return

    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        self.log('BUY EXECUTED, %.2f' % order.executed.price)
      elif order.issell():
        self.log('SELL EXECUTED, %.2f' % order.executed.price)

      self.bar_executed = len(self)

    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')

    # Write down: no pending order
    self.order = None

  def notify_trade(self, trade):
    if not trade.isclosed:
      return

    self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
             (trade.pnl, trade.pnlcomm))

  def next(self):
    # Simply log the closing price of the series from the reference
    # self.log('Close, %.2f' % self.dataclose[0])

    if self.order:
      return

    # Check if we are in the market
    if not self.position:
      if self.dataclose[0] < self.dataclose[-1]:
        # current close less than previous close

        if self.dataclose[-1] < self.dataclose[-2]:
          # previous close less than the previous close

          # BUY, BUY, BUY!!! (with all possible default parameters)
          self.log('BUY CREATE, %.2f' % self.dataclose[0])
          self.order = self.buy()
    else:
      # Already in the market ... we might sell
      if len(self) >= (self.bar_executed + self.params.exitbars):
        # SELL, SELL, SELL!!! (with all possible default parameters)
        self.log('SELL CREATE, %.2f' % self.dataclose[0])

        # Keep track of the created order to avoid a 2nd order
        self.order = self.sell()


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
  strats = cerebro.addstrategy(TestStrategy, exitbars=10)

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
