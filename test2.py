#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test2 : test creation database

"""
from database import DatabaseExchanges, DatabaseSymbols, DatabaseDailyPrices, DatabaseIntradayPrices

if __name__=="__main__":
    base ='test.db'
    Exchange = DatabaseExchanges(base)
    Exchange.new()
    Exchange.remplissage()
    Exchange.affichage()
    Symbols = DatabaseSymbols(base)
    Symbols.new()
    Symbols.remplissage()
    Symbols.affichage()
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    #DailyPrices.obtain_tickers()
    DailyPrices.tickers=[(1,'BNP','.PA')]
    DailyPrices.get_prices()
    a = DailyPrices.toDataframe(DailyPrices.table, DailyPrices.columns_str,'BNP.PA')
    print(a.index)
    #DailyPrices.affichage()
    #DailyPrices.update_prices()
    #DailyPrices.affichage()
    IntradayPrices = DatabaseIntradayPrices(base)
    IntradayPrices.new()
    #Intraday.obtain_tickers()
    IntradayPrices.tickers=[(1,'BNP','.PA')]
    IntradayPrices.get_prices()
    IntradayPrices.affichage()