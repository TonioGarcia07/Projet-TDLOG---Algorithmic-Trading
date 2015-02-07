#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test3 : test creation database

"""

import queue
import time
from random import randint
import qc
from unittest import assertEqual
from database import DatabaseExchanges, DatabaseSymbols, DatabaseDailyPrices, DatabaseIntradayPrices

if __name__=="__main__":
    
    now = time.time ()
    
    base ='test.db'

    IntradayPrices = DatabaseIntradayPrices(base)
    IntradayPrices.new()
    IntradayPrices.obtain_tickers()
    IntradayPrices.get_prices()
    IntradayPrices.affichage()
    
    IntradayPrices2 = DatabaseIntradayPrices(base)
    IntradayPrices2.new()
    IntradayPrices2.obtain_tickers()
    IntradayPrices2.get_prices()
    IntradayPrices2.affichage()
    
    tickers = IntradayPrices.tickers
    
    ticker = tickers(randint(0,len(tickers)-1))
    print(IntradayPrices.toDataframe('intraday_prices',"Date, Open, High, Low, Close, Volume",ticker))
    
    @qc.forall(tries=10, l= qc.integers(low = 0, high = (len(tickers)-1)))
    def test(l):
        ticker_test = tickers(l)
        assertEqual(IntradayPrices.toDataframe('intraday_prices',"Date, Open, High, Low, Close, Volume",ticker_test),
                IntradayPrices2.toDataframe('intraday_prices',"Date, Open, High, Low, Close, Volume",ticker_test))
    
    test()
    
    print(str(time.time() - now))