import backtrader as bt
import datetime

class TestStrategy(bt.Strategy):
    """
    继承并构建自己的bt策略
    """

    def next(self):
      # 记录收盘价
      print('Close, %.2f' % self.datas[0].Close)

      # 是否正在下单，如果是的话不能提交第二次订单
      if self.order:
        return

      # 是否已经买入
      if not self.position:
        # 还没买，如果 MA5 > MA10 说明涨势，买入
        if self.sma5[0] > self.sma10[0]:
          print('BUY CREATE, %.2f' % self.datas[0].Close)
          self.order = self.buy()
      else:
        # 已经买了，如果 MA5 < MA10 ，说明跌势，卖出
        if self.sma5[0] < self.sma10[0]:
          print('SELL CREATE, %.2f' % self.datas[0].Close)
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
      fromdate=datetime.datetime(2010, 1, 1),
      todate=datetime.datetime(2020, 4, 12)
  )
  cerebro.adddata(data)

  # 策略执行前的资金
  print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

  cerebro.run()

  # 策略执行后的资金
  print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

  