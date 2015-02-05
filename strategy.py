#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
strategy.py: classe qui va contenir les differentes strategies qu'on veut
tester/appliquer. Elles vont generer les signals d'achat/vente sur un actif
et posteriorment la classe portfolio va gestioner le volume du contrat.
"""

from events import TradeEvent

class Strategy():
    """
    Classe mère des différentes strategies.
    """
    pass

class BuyandHoldStrategy(Strategy):
    """
    Classe fille de Strategy qui donne un signal BUY pour tous
    les tickers dans le ticker_list du DataManager
    """
    
    def __init__(self, data, events):
        """
        data: DataManager instance qui continet les cotations
        events: Queue d'Events
        """
        self.data = data
        self.ticker_list =self.data.ticker_list
        self.events = events
        self.bought = {ticker:False for ticker in self.ticker_list}
        
    def generate_trade_signal(self,event):
        if event.type == 'DATA':
            for ticker in self.ticker_list:
                bar = self.data.get_last_ticker(ticker,N=1)
                if bar is not None and bar !=[]:
                    if self.bought[ticker] == False:
                        self.events.put(TradeEvent(ticker,bar[0][0],'BUY'))
                        self.bought[ticker] = True
    
    # methode pour enregister calculs (ex. media mobil,...flechas de entrada)
                
        