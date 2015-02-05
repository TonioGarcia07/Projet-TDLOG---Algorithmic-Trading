#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test

"""
from database import DatabaseDailyPrices
from datetime import datetime
from datamanager import SQLDataManagerBacktest
from strategy import BuyandHoldStrategy
import queue

if __name__=="__main__":
    
    base ='test.db'
    tickers =['BNP.PA','GSZ.PA']
    
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    DailyPrices.tickers=[(1,'BNP','.PA'),(2,'GSZ','.PA')]
    DailyPrices.get_prices()
    DailyPrices.update_prices()
    
    Trivial = queue.Queue()
    DataManager1 = SQLDataManagerBacktest(Trivial,DailyPrices,tickers,datetime(2014, 1, 1),datetime(2014, 1, 12))
    DataManager1.market()
    Strategy1 = BuyandHoldStrategy(DataManager1,Trivial)
    
    while True:
        if DataManager1.continue_backtest == True:
            DataManager1.next_bar()
        else:
            break
        
        while True:
            try:
                event = Trivial.get(False)
            except:
                break
            else:
                if event is not None:
                    print(event)
#                    for ticker in tickers:
#                        print(DataManager1.get_last_ticker(ticker))
                    if event.type == 'DATA':
                        Strategy1.generate_trade_signal(event)
                    if event.type == 'TRADE':
                        print('operation')
                        