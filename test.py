#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test

"""
from database import DatabaseDailyPrices
from datetime import datetime
from datamanager import SQLDataManagerBacktest
from datastorage import DataStorage
from strategy import BuyandHoldStrategy, MovingAverageStrategy
from portfolio import MovAvePortfolio
import queue
import time


if __name__=="__main__":
    
    base ='test.db'
    tickers =['BNP.PA']#,'GSZ.PA','EDF.PA']
    Trivial = queue.Queue()
    carnet_ordres = queue.Queue()
    initial_capital = 10000
    vitesse = 0.01
    
    DailyPrices = DatabaseDailyPrices(base)
#    DailyPrices.new()
    DailyPrices.tickers=[(1,'BNP','.PA')]#,(2,'GSZ','.PA'),(3,'EDF','.PA')]
#    DailyPrices.get_prices()
#    DailyPrices.update_prices()
    
    
    
    DataManager1 = SQLDataManagerBacktest(Trivial,DailyPrices,tickers,datetime(2009,5, 2),datetime(2010, 8, 30))
    DataManager1.market()
    
    DataStorage1 = DataStorage(tickers)
    
#    Strategy1 = BuyandHoldStrategy(DataManager1,DataStorage1,Trivial)
    Strategy1 = MovingAverageStrategy(DataManager1,DataStorage1,Trivial,6,20)
    
    Portfolio1 = MovAvePortfolio(DataStorage1,Trivial,initial_capital,carnet_ordres)
    
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
#                        print(event)
#                        for ticker in tickers:
#                            print(DataManager1.get_last_ticker(ticker))
                        
                        Strategy1.generate_trade_signal(event)
                        
                        while True:
                            try:
                                ordre = carnet_ordres.get(False)
                                print(ordre)
                                
                            except:
                                break
                            else:
                                Portfolio1.treat_OrderEvent(ordre)
                                
                        Portfolio1.update_portfolio_data()
                            
                    if event.type == 'TRADE':
                        print(event)
                        Portfolio1.treat_TradeEvent(event)
        
        time.sleep(vitesse)
    
    
#    for ticker in DataStorage1.info.keys():
#        print(ticker)
#        for (label,values) in DataStorage1.info[ticker].items():
#            if label in set(['Close','Quantity','Fix_Value','Trade','Market_Value','Value','MtM','Cash','Portfolio_Value']):
#                print(label)
#                for value in values:
#                    print(value)
#    

        
    
    

            
                        