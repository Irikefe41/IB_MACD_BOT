import datetime
import backtrader as bt

class MACDstrat(bt.Strategy):

	params = dict(macd1=12,
					macd2=26,
					macdsig=9,
					pstake=50,
					stopafter=0)


	def __init__(self, ):

		self.counttostop = 0
		self.datastatus = 0

		if self.p.macd1 > self.p.macd2:
			raise ValueError("The MACD strategy cannot have the fast moving average's window be greater than the slow moving average window.")

		self.macd = bt.indicators.MACD(self.data,period_me1=self.p.macd1,period_me2=self.p.macd2,period_signal=self.p.macdsig)
		self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
		self.orderid = list()
	 
	    # To set the stop price
	    # self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

	    # self.sma = bt.indicators.SMA(self.data, period=self.p.smaperiod)
	    # self.smadir = self.sma - self.sma(-self.p.dirperiod)

	def next(self):

		dt = self.data.datetime.date()
		portfolio_value = self.broker.get_value()
		print('log {} - {} - Position_Size: {} - Portfolio_Value {}'.format(len(self), dt.isoformat(), self.position.size, portfolio_value))
		# print('MACD value length  {}'.format(len(self.macd.macd)))
		pos = self.getposition().size or 0

		if pos == 0:
			if self.mcross[0] > 0 and self.macd.macd[0] > 0 and self.macd.macd[-1] > 0:
				self.entryprice = self.data.close[0]
				self.order = self.order_target_percent(target=self.p.pstake/100)
				# self.notify_order(self.order)

		elif self.mcross[0] < 0 or ((self.entryprice - self.data.close[0]) >= 0.6) and self.entryprice > 0:
			self.order = self.order_target_size(target=self.position.size)
			self.entryprice = 0
			# self.notify_order(self.order)
		else:
			print('Scanning market; Managing trades')

	def notify_order(self, order):
		if order.Status in [order.Completed, order.Cancelled, order.Rejected]:
			self.order = None
		print('ORDERLOGGED AT: {}'.format(datetime.datetime.now()))
		print(order)
		print('ORDERLOG END')

	def notify_data(self, data, status, *args, **kwargs):
		print('<-----LIVE DATAFEED NOTIFICATION: ', data._getstatusname(status), *args)
		if status == data.LIVE:
			self.counttostop = self.p.stopafter
			self.datastatus = 1