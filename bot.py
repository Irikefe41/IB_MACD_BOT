import os
import sys
import backtrader as bt 
from datetime import datetime
from .utils.parseJSON import readJson
from .strategy.myMACD import MACDstrat
import backtrader.filters as btfilters


config = readJson('config.json')
print("Current Settings: \n{}".format(config))


def reportStatus():
	pass


if __name__ == '__main__':
    try:
        cerebro = bt.Cerebro(stdstats=False)
        IB = bt.stores.IBStore(port=7497)
        sStart = datetime.strptime('9:30', '%H:%M')
        sEnd = datetime.strptime('16:00', '%H:%M')
        data = IB.getdata(dataname=config['stocklist'][0],timeframe=bt.TimeFrame.Ticks, rtbar=True, sessionstart=sStart, sessionend=sEnd)
        data0 = IB.getdata(dataname=config['stocklist'][1],timeframe=bt.TimeFrame.Ticks, rtbar=True, sessionstart=sStart, sessionend=sEnd)
        # 
        # lastPV = 10067.5
        data.addfilter(btfilters.SessionFilter)
        data0.addfilter(btfilters.SessionFilter)

        #data.addfilter(btfilters.SessionFiller, fill_vol=args.fvol)
        cerebro.broker = IB.getbroker()
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes,compression=60)
        cerebro.resampledata(data0, timeframe=bt.TimeFrame.Minutes,compression=60)
        
        cerebro.adddata(data)        
        cerebro.adddata(data0)

        # cerebro.broker.setcash(lastPV)

        cerebro.addstrategy(MACDstrat)
        cerebro.run()
    except KeyboardInterrupt:
        print('\n\tBot Stopped!!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)