import os
import sys
import backtrader as bt 
from utils.parseJSON import readJson
from strategy.myMACD import MACDstrat

config = readJson('config.json')
print("Current Settings: \n{}".format(config))

def reportStatus():
	pass


if __name__ == '__main__':
    try:
        cerebro = bt.Cerebro(stdstats=False)
        IB = bt.stores.IBStore(port=7497)
        data = IB.getdata(dataname=config['stocklist'][0],timeframe=bt.TimeFrame.Ticks, rtbar=True)
        # cerebro.broker = IB.getbroker()
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes,compression=60)
        cerebro.adddata(data)

        cerebro.addstrategy(MACDstrat
   			)
        cerebro.run()
    except KeyboardInterrupt:
        print('\n\tBot Stopped!!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)