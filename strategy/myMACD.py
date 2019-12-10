import datetime
import backtrader as bt
from ..utils.parseJSON import readJson
from ..notifier.publish_signals import publish

class MACDstrat(bt.Strategy):

	params = dict(macd1=12,
					macd2=26,
					macdsig=9,
					pstake=50,
					stopafter=0,
					stop_loss=0.6)


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

		# for d in self.getdatanames():

		dt = self.data.datetime.datetime(0)
		portfolio_value = self.broker.get_value()
		track_time = datetime.datetime.now()
		

		print('Log{} -Timestamp: {} - Position_Size: {} - Portfolio_Value {}'.format(len(self), dt.isoformat(), self.position.size, portfolio_value))
		# print('MACD value length  {}'.format(len(self.macd.macd)))
		if track_time.minute == 1:
			publish("Close price at {} is {}".format(track_time, self.data.close[0]))

		pos = self.getposition().size or 0

		if pos == 0:
			if self.mcross[0] > 0 and self.macd.macd[0] > 0 and self.macd.macd[-1] > 0:
				self.stop_price = self.data.close[0] - self.p.stop_loss
				self.order = self.order_target_percent(target=self.p.pstake/100)
				self.sl_ord = self.sell(size=self.order.size, exectype=bt.Order.Stop, price=self.stop_price)
				self.sl_ord.addinfo(name='Long Stop Loss')

		elif self.mcross[0] < 0:
			# self.order_target_size(target=-self.position.size)
			cls_ord = self.cancel(self.sl_ord)
			# cls_ord.addinfo(name="Close Stop Loss Order")
			self.sell(size=self.order.size)

		else:
			print('Scanning market; Managing trades')

	def notify_order(self, order):
		date = self.data.datetime.datetime().date()

		if order.status == order.Accepted:
			print('-'*32,' NOTIFY ORDER ','-'*32)
			print('{} Order Accepted'.format(order.info['name']))
			print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
			publish('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
		if order.status == order.Completed:
			print('-'*32,' NOTIFY ORDER ','-'*32)
			print('{} Order Completed'.format(order.info['name']))
			print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
			print('Created: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,order.created.size))
			publish('Created: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,order.created.size))
			print('-'*80)

		if order.status == order.Canceled:
			print('-'*32,' NOTIFY ORDER ','-'*32)
			print('{} Order Canceled'.format(order.info['name']))
			print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
			publish('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))

		if order.status == order.Rejected:
			print('-'*32,' NOTIFY ORDER ','-'*32)
			print('WARNING! {} Order Rejected'.format(order.info['name']))
			print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
			publish('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))

	def notify_data(self, data, status, *args, **kwargs):
		print('<-----LIVE DATAFEED NOTIFICATION: ', data._getstatusname(status), *args)
		publish('<-----LIVE DATAFEED NOTIFICATION: {}'.format(data._getstatusname(status)))

		if status == data.LIVE:
			publish("Data feed live !")
			self.counttostop = self.p.stopafter
			self.datastatus = 1