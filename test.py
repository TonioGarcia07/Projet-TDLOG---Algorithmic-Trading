#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test

"""
from database import DatabaseDailyPrices
from datetime import datetime
from datamanager import SQLDataManagerBacktest
from strategy import BuyandHoldStrategy, MovingAverageStrategy
import queue
import time


if __name__=="__main__":
    
    base ='test.db'
    tickers =['BNP.PA']#,'GSZ.PA','EDF.PA']
    vitesse = 0.1
    
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    DailyPrices.tickers=[(1,'BNP','.PA')]#,(2,'GSZ','.PA'),(3,'EDF','.PA')]
    DailyPrices.get_prices()
    DailyPrices.update_prices()
    
    Trivial = queue.Queue()
    
    DataManager1 = SQLDataManagerBacktest(Trivial,DailyPrices,tickers,datetime(2014, 1, 1),datetime(2014, 2, 15))
    DataManager1.market()
    
#    Strategy1 = BuyandHoldStrategy(DataManager1,Trivial)
    Strategy1 = MovingAverageStrategy(DataManager1,Trivial,5,10)
    
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
                    if event.type == 'DATA':
                        print(event)
                        for ticker in tickers:
                            print(DataManager1.get_last_ticker(ticker))
                        Strategy1.generate_trade_signal(event)
                    if event.type == 'TRADE':
                        print(event)
                        print('operation')
        
        time.sleep(vitesse)
    
    for ticker in tickers:
        print(ticker)
        for (info,value) in Strategy1.info[ticker].items():
            print(info)
            for element in value:
                print(element)
    
    

            
                        