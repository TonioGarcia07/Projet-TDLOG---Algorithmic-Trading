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
    def __init__(self,events,database,ticker_list,date_start='',date_end=''):
        self.events = events
        self.database = database
        self.ticker_list = ticker_list
        self.ticker_data = {}
        self._sql_request(date_start,date_end)
        
    def _sql_request(self,date_start,date_end):
        """
        Creátion du dictionnaire qui contient les dataframes avec les
        cotations pour les tickers de la liste entrée dans ticker_list
        """
        for ticker in self.ticker_list:
            self.ticker_data[ticker] = self.database.toDataframe(self.database.table,self.database.columns_str,ticker)
            self.ticker_data[ticker] = self.ticker_data[ticker][date_start:date_end]
            
    def bar_iterator(self,ticker,N=1):
        """
        Construction de l'iterateur a partir de la Dataframe du ticker
        """
        for bar in self.ticker_data[ticker]:
            yield tuple([ticker, datetime.strptime(bar[0], '%Y-%m-%d'), 
                        bar[1][0], bar[1][1], bar[1][2], bar[1][3], bar[1][4]])
    
    def next_bar(self):
        """
        Prend la suivant bar de l'iterateur et le stock dans le
        dictionnaire lastest_ticker_data.
        """
        for ticker in self.ticker_list:
            pass
        
        
        
if __name__=="__main__":
    base ='test.db'
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    DailyPrices.tickers=[(1,'BNP','.PA')]
    DailyPrices.get_prices()
    DailyPrices.update_prices()
    DataManager1 = SQLDataManager('events',DailyPrices,['BNP.PA'],datetime(2011, 1, 7),datetime(2012, 1, 7))
    print(DataManager1.ticker_data)
    print(DataManager1.ticker_data['BNP.PA'].index.dtype)
    
    