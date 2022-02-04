# use MA cross to buy/sell
import datetime
import backtrader as bt

class MA1Strategy(bt.Strategy):
  params = (
    ('ma_period1', 10),
    ('ma_period2', 60),
  )

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))

  def __init__(self):
    # To keep track of pending orders and buy price/commission
    self.order = None

    # Add a MovingAverageSimple indicator
    self.ma1 = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_period1)
    self.ma2 = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_period2)

  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return

    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        # self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
        #     (order.executed.price,
        #      order.executed.value,
        #      order.executed.comm))

        self.buyprice = order.executed.price
        self.buycomm = order.executed.comm
      else:  # Sell
        pass
        # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
        #          (order.executed.price,
        #           order.executed.value,
        #           order.executed.comm))
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')

    self.order = None

  def notify_trade(self, trade):
    if not trade.isclosed:
      return

    self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
             (trade.pnl, trade.pnlcomm))

  def next(self):
    # Check if an order is pending ... if yes, we cannot send a 2nd one
    if self.order:
      return

    close = self.datas[0].close
    # Check if we are in the market
    if not self.position:
      if self.check_ma2_direction() > 0 and self.ma1[-1] < self.ma2[-1] and self.ma1[0] >= self.ma2[0]:
        # self.log('BUY CREATE, %.2f' % close[0])
        self.order = self.buy()
    else:
      if self.ma1[-1] > self.ma2[-1] and self.ma1[0] <= self.ma2[0]:
        # self.log('SELL CREATE, %.2f' % close[0])
        self.order = self.sell()

  def check_ma2_direction(self):
    if self.ma2[0] > self.ma2[-1] * 1.001 or self.ma2[0] > self.ma2[-1] > self.ma2[-2]:
      return 1 # up
    elif self.ma2[0] * 1.001  < self.ma2[-1] or self.ma2[0]  < self.ma2[-1]  < self.ma2[-2]:
      return -1 # down
    else:
      return 0 #

if __name__ == '__main__':
  cerebro = bt.Cerebro()
  cerebro.broker.setcash(10000.0)
  cerebro.broker.set_coc(True)
  # cerebro.broker.setcommission(0.0005)
  cerebro.addsizer(bt.sizers.AllInSizer)
  strats = cerebro.addstrategy(MA1Strategy)

  data = bt.feeds.GenericCSVData(
      dataname='./stock_data/0.000001.csv',
      name='000001',
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
  cerebro.adddata(data)
  # cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
  # cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)

  # 策略执行前的资金
  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  # 策略执行后的资金
  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.plot(style='candle', barup='red', barupfill=False, bardown='green', plotdist=1, volume=False)