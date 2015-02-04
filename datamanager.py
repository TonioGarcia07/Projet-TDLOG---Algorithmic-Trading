#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
DataManager.py: classe qui permet la gestion de données
Elle va aller chercher les cotations et informations generées
a partir des classe Database et les stocker dans un iterateur
pour 'simuler' le marché quand on fait le backtest
"""

from database import DatabaseDailyPrices
from datetime import datetime
from events import DataEvent
import queue

class DataManager:
    """
    Classe mère trivial d'où heritent toutes les autres classes DataManager
    """
    pass

class SQLDataManagerBacktest(DataManager):
    """
    Classe fille de DataManager qui permet de recuperer les cotations et
    informations stockées anterieurement et simuler le marché quand on fait un 
    backtest
    """
    def __init__(self,events,database,ticker_list,date_start=datetime(2010, 1, 1),date_end=datetime.today()):
        self.events = events
        self.database = database
        self.ticker_list = ticker_list
        self.ticker_data = {}
        self.bars = {}
        self.last_ticker_data = {}
        self.continue_backtest = True
        self._sql_request(date_start,date_end)
        
    def _sql_request(self,date_start,date_end):
        """
        Creátion du dictionnaire qui contient les dataframes avec les
        cotations pour les tickers de la liste entrée dans ticker_list
        """
        for ticker in self.ticker_list:
            self.ticker_data[ticker] = self.database.toDataframe(self.database.table,self.database.columns_str,ticker)
            self.ticker_data[ticker] = self.ticker_data[ticker][date_start:date_end]
            self.last_ticker_data[ticker] =[]
               
    def market(self):
        for ticker in self.ticker_list:
            self.bars[ticker] = self.ticker_data[ticker].iterrows()
   
    def next_bar(self):
        for ticker in self.ticker_list:
            try:
                bar = next(self.bars[ticker])
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar != None:
                    self.last_ticker_data[ticker].append(bar)
        if self.continue_backtest == True: self.events.put(DataEvent())
    
    def get_last_ticker(self, ticker, N=1):
        try:
            bars_list = self.last_ticker_data[ticker]
        except KeyError:
            print( "Le ticker n'est pas disponible")
        else:
            return bars_list[-N:]
   
        
if __name__=="__main__":
    
    base ='test.db'
    ticker ='BNP.PA'
    
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    DailyPrices.tickers=[(1,'BNP','.PA')]
    DailyPrices.get_prices()
    DailyPrices.update_prices()
    
    Trivial = queue.Queue()
    DataManager1 = SQLDataManagerBacktest(Trivial,DailyPrices,[ticker],datetime(2014, 1, 1),datetime(2014, 1, 12))
    print(DataManager1.ticker_data)
    print(DataManager1.ticker_data[ticker].index.dtype)

    DataManager1.market()
    
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
                    print(DataManager1.get_last_ticker(ticker))

    
    
    
    
    
    
    
    
    
    
    
    
    