# Plot
# Backtrader plot has bug, see: https://github.com/mementum/backtrader/pull/418/files

import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
  params = (
      ('maperiod', 5),
  )

  def log(self, txt, dt=None):
    ''' Logging function fot this strategy'''
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    # Keep a reference to the "close" line in the data[0] dataseries
    self.dataclose = self.datas[0].close

    # To keep track of pending orders and buy price/commission
    self.order = None
    self.buyprice = None
    self.buycomm = None

    # Add a MovingAverageSimple indicator
    self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
    # Indicators for the plotting show
    bt.indicators.ExponentialMovingAverage(self.datas[0], period=5)
    # bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
    # bt.indicators.MACDHisto(self.datas[0])
    # rsi = bt.indicators.RSI(self.datas[0])
    # bt.indicators.SmoothedMovingAverage(rsi, period=10)
    # bt.indicators.ATR(self.datas[0], plot=False)
    
  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return

    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        self.log(
            'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
            (order.executed.price,
             order.executed.value,
             order.executed.comm))

        self.buyprice = order.executed.price
        self.buycomm = order.executed.comm
      else:  # Sell
        self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                 (order.executed.price,
                  order.executed.value,
                  order.executed.comm))

      self.bar_executed = len(self)

    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')

    self.order = None

  def notify_trade(self, trade):
    if not trade.isclosed:
      return

    self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
             (trade.pnl, trade.pnlcomm))

  def next(self):
    # Simply log the closing price of the series from the reference
    self.log('Close, %.2f' % self.dataclose[0])

    # Check if an order is pending ... if yes, we cannot send a 2nd one
    if self.order:
      return

    # Check if we are in the market
    if not self.position:

      # Not yet ... we MIGHT BUY if ...
      if self.dataclose[0] > self.sma[0]:

        # BUY, BUY, BUY!!! (with all possible default parameters)
        # self.log('BUY CREATE, %.2f' % self.dataclose[0])

        # Keep track of the created order to avoid a 2nd order
        self.order = self.buy()

    else:

      if self.dataclose[0] < self.sma[0]:
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

  cerebro.plot(style='candle', barup='red', bardown='green', plotdist=1, volume=False)