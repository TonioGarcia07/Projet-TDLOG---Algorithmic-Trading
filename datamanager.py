#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
DataManager.py: classe qui permet la gestion de données
Elle va aller chercher les cotations et informations generées
a partir des classe Database et les stocker dans un iterateur
pour 'simuler' le marché quand on fait le backtest
"""
import pandas as pd
from database import DatabaseDailyPrices
from datetime import datetime
from events import DataEvent

class DataManager:
    """
    Classe mère trivial d'où heritent toutes les autres classes DataManager
    """
    pass

class SQLDataManager(DataManager):
    """
    Classe fille de DataManager qui permet de recuperer les cotations et
    informations stockées anterieurement et simuler le marché quand on fait un 
    backtest
    """
    def __init__(self,events,database,ticker_list):
        self.events = events
        self.database = database
        self.ticker_list = ticker_list
        self.ticker_data = {}
        self._sql_request()
        
    def _sql_request(self):
        for ticker in self.ticker_list:
            self.ticker_data[ticker] = self.database.toDataframe(self.database.table,self.database.columns_str,ticker)

if __name__=="__main__":
    base ='test.db'
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    DailyPrices.tickers=[(1,'BNP','.PA')]
    DailyPrices.get_prices()
    DailyPrices.update_prices()
    DataManager1 = SQLDataManager('events',DailyPrices,['BNP.PA'])
    print(DataManager1.ticker_data)