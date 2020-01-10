from datetime import datetime, timedelta
import backtrader as bt
from ..utils.parseJSON import readJson
from ..notifier.publish_signals import publish

class MACDstrat(bt.Strategy):

	params = dict(macd1=12,
					macd2=26,
					macdsig=9,
					pstake=50,
					stopafter=10000,
					stop_loss=0.6)


	def __init__(self, ):

		self.counttostop = 0
		self.datastatus = 0
		self.macd = dict()
		self.mcross = dict()
		self.order = dict()
		self.sl_ord = dict()

		if self.p.macd1 > self.p.macd2:
			raise ValueError("The MACD strategy cannot have the fast moving average's window be greater than the slow moving average window.")

		for d in self.getdatanames():
			self.macd[d] = bt.indicators.MACD(self.getdatabyname(d),period_me1=self.p.macd1,period_me2=self.p.macd2,period_signal=self.p.macdsig)
			self.mcross[d] = bt.indicators.CrossOver(self.macd[d].macd, self.macd[d].signal)


	def next(self):		

		for d in self.getdatanames():

			today = datetime.now().date()  - timedelta(days=1)
			_dday = datetime(today.year, today.month, today.day, 9)
			dt = self.getdatabyname(d).datetime.datetime(0)	

			if dt >= _dday:
				portfolio_value = self.broker.get_value()
				track_time = datetime.now() - timedelta(minutes=60)
				# print(self.getdatabyname(d).p.sessionend)
				print('Log_{} -Timestamp: {} - Position_Size: {} - Portfolio_Value {}'.format(len(self), dt.isoformat(), self.position.size, portfolio_value))
				publish('Timestamp: {} - Position_Size: {} - Portfolio_Value {}'.format( dt.isoformat(), self.position.size, portfolio_value))
				print('mcross_{}: {}'.format(d, self.mcross[d][0]))
				print('macd signal:{}'.format(self.macd[d].macd[0]))
				print('macd signal:{}'.format(self.macd[d].macd[-1]))

				if dt.minute == 0 and dt > track_time:					
					publish("{} Close price: {}\nAt Timestamp: {}".format(d,self.getdatabyname(d).close[0],dt.isoformat()))

				pos = self.getpositionbyname(d).size or 0

				if pos == 0:
					if self.mcross[d][0] > 0 and self.macd[d].macd[0] > 0 and self.macd[d].macd[-1] > 0:
						self.stop_price = self.getdatabyname(d).close[0] - self.p.stop_loss
						self.order[d] = self.order_target_percent(data=self.getdatabyname(d),target=self.p.pstake/100)
						self.sl_ord[d] = self.sell(data=self.getdatabyname(d),size=self.order[d].size, exectype=bt.Order.Stop, price=self.stop_price)
						self.sl_ord[d].addinfo(name='Long Stop Loss')

				elif self.mcross[d][0] < 0:
					self.cancel(self.sl_ord[d])
					self.sell(data=self.getdatabyname(d),size=self.order[d].size)

				else:
					print('Scanning market; Managing trades')
			# import pdb; pdb.set_trace()


	def notify_order(self, order):

		stock = self.getdatanames()
		date = self.getdatabyname(stock[0]).datetime.datetime(0)
		# date = self.data.datetime.datetime().date()

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
			publish('Accepted Order at: {}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
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
			publish('Completed Order: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,order.created.size))
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
			publish('Cancelled Order: {}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
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
			publish('Rejected Order at:{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))

	def notify_data(self, data, status, *args, **kwargs):
		print('<-----LIVE DATAFEED NOTIFICATION: ', data._getstatusname(status), *args)
		# publish('<-----LIVE DATAFEED NOTIFICATION: {}'.format(data._getstatusname(status)))
		if status == data.LIVE:
			for d in self.getdatanames():
				publish("{} Data feed live !".format(d))
				self.counttostop = self.p.stopafter
				self.datastatus = 1