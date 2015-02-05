#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
portfolio.py: classe qui va contenir le portfolio a gerer et qui va recevoir les
signals de BUY/SELL de la classe strategy et va determiner le volume selon le
politique de gestion monaitaire adoptée.
Va contenir aussi des informations sur les positions ouvertes.
"""

class Portfolio():
    """
    
    """
    def __init__(self,datastorage,initial_capital):
        self.datastorage = datastorage
        self.ticker_list = self.datastorage.ticker_list
        self.initial_capital =initial_capital
        self.label_list = ['Quantity','Fix_Value','Market_Value','MtM']
        self.label_list_portfolio = ['Date','Cash','Market','Porfolio','MtM']
        self.datastorage.generate_keys(self.label_list)
        self.datastorage.info['Portfolio']={label:[] for label in self.label_list_portfolio}
        self.dict_quantities={ticker:0 for ticker in self.ticker_list}
        self.dict_contractprices={ticker:0.0 for ticker in self.ticker_list}
    
#    def _initial_values(self):
#        self.datastorage.info['Portfolio']['Cash'].append(self.initial_capital)
#        self.datastorage.info['Portfolio']['Market'].append(0.0)
#        self.datastorage.info['Portfolio']['Portfolio'].append(self.initial_capital)
#        self.datastorage.info['Portfolio']['MtM'].append(0.0)
#        information = [tuple(label,0.0) for label in self.label_list]
#        self.datastorage.info_stocking(information)     
        
    def update_portfolio_data(self):
        for ticker in self.ticker_list:
            self.datastorage.info[ticker]['Quantity'].append(self.dict_quantities[ticker])
            self.datastorage.info[ticker]['Fix_Value'].append(self.dict_contractprices[ticker]*self.dict_quantities[ticker])
            self.datastorage.info[ticker]['Market_Value'].append(self.datastorage.info[ticker]['Close'][-1]*self.dict_quantities[ticker])
            self.datastorage.info[ticker]['MtM'].append(self.datastorage.info[ticker]['Market_Value'][-1]-self.datastorage.info[ticker]['Fix_Value'][-1])
            
        

class MovAvePortfolio(Portfolio):
    """
    
    """
    def __init__(self,datastorage,events,initial_capital):
        super().__init__(datastorage,initial_capital)
        self.events = events
    
    def generate_order(tradeEvent):
        ticker = tradeEvent.ticker
        datetime = tradeEvent.datetime
        direction = tradeEvent.direction
               
        
#        self.ticker = ticker
#        self.order_type = order_type
#        self.volume = volume
#        self.direction = direction
    
    def treat_TradeSginal(self,event):
        if event.type == 'TRADE':
            order_event = self.generate_order(event)
            self.events.put(order_event)
    
    
    
