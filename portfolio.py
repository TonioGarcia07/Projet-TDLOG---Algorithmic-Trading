#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
portfolio.py: classe qui va contenir le portfolio a gerer et qui va recevoir les
signals de BUY/SELL de la classe strategy et va determiner le volume selon le
politique de gestion monaitaire adoptée.
Va contenir aussi des informations sur les positions ouvertes.
"""

from math import floor
from events import OrderEvent

class Portfolio():
    """
    
    """
    def __init__(self,datastorage,initial_capital,carnet_ordres):
        self.datastorage = datastorage
        self.ticker_list = self.datastorage.ticker_list
        self.cash =initial_capital
        self.label_list = ['Quantity','Fix_Value','Market_Value','MtM']
        self.label_list_portfolio = ['Date','Cash','Market_Value','Portfolio_Value','MtM']
        self.datastorage.generate_keys(self.label_list)
        self.datastorage.info['Portfolio']={label:[] for label in self.label_list_portfolio}
        self.dict_quantities={ticker:0 for ticker in self.ticker_list}
        self.dict_contractprices={ticker:0.0 for ticker in self.ticker_list}
        self.carnet_ordres = carnet_ordres
        self.provisional_cash = initial_capital     
        
    def update_portfolio_data(self):
        sum_Market_Value = 0
        sum_MtM = 0
        for ticker in self.ticker_list:
            self.datastorage.info[ticker]['Quantity'].append(self.dict_quantities[ticker])
            self.datastorage.info[ticker]['Fix_Value'].append(self.dict_contractprices[ticker]*self.dict_quantities[ticker])
            self.datastorage.info[ticker]['Market_Value'].append(self.datastorage.info[ticker]['Close'][-1]*self.dict_quantities[ticker])
            self.datastorage.info[ticker]['MtM'].append(self.datastorage.info[ticker]['Market_Value'][-1]-self.datastorage.info[ticker]['Fix_Value'][-1])
            sum_Market_Value = sum_Market_Value + self.datastorage.info[ticker]['Market_Value'][-1]
            sum_MtM = sum_MtM + self.datastorage.info[ticker]['MtM'][-1]
            
        self.datastorage.info['Portfolio']['Date'].append(self.datastorage.info[self.ticker_list[0]]['Date'][-1])
        self.datastorage.info['Portfolio']['Cash'].append(self.cash)
        self.datastorage.info['Portfolio']['Portfolio_Value'].append(self.cash + sum_Market_Value)
        self.datastorage.info['Portfolio']['Market_Value'].append(sum_Market_Value)
        self.datastorage.info['Portfolio']['MtM'].append(sum_MtM)

    def treat_TradeEvent(self,event):
        if event.type == 'TRADE':
            order_event = self.generate_order(event)
            self.carnet_ordres.put(order_event)
    
    def execute_operation(self,ordre):
        ticker = ordre.ticker
        order_type = ordre.order_type
        quantity = ordre.quantity
        order_price = ordre.order_price
        direction = ordre.direction
        
        if direction == 'BUY': sign = 1
        elif direction == 'SELL': sign = -1
        
        if order_type == 'LMT':
            if self.datastorage.info[ticker]['Low'][-1]<=order_price <=self.datastorage.info[ticker]['High'][-1]:
                self.dict_quantities[ticker] = self.dict_quantities[ticker] + quantity
                self.dict_contractprices[ticker] = order_price
                self.cash = self.cash - abs(self.dict_contractprices[ticker] * self.dict_quantities[ticker])
        elif order_type == 'MKT':
            self.dict_quantities[ticker] = self.dict_quantities[ticker] + quantity
            self.dict_contractprices[ticker] = self.datastorage.info[ticker]['Open'][-1] + sign * 0.0025 * self.datastorage.info[ticker]['Open'][-1]
            self.cash = self.cash - abs(self.dict_contractprices[ticker] * self.dict_quantities[ticker])
                
        self.provisional_cash = self.cash
   
    def treat_OrderEvent(self,ordre):
        if ordre.type == 'ORDER':
            self.execute_operation(ordre)        

class MovAvePortfolio(Portfolio):
    """
    
    """
    def __init__(self,datastorage,events,initial_capital,carnet_ordres):
        super().__init__(datastorage,initial_capital,carnet_ordres)
        self.events = events
    
    def generate_order(self,tradeEvent):
        ticker = tradeEvent.ticker
        direction = tradeEvent.direction
        
        if direction == 'BUY': 
            sign = 1
        elif direction == 'SELL': 
            sign = -1
            
        order_type = 'LMT' # 'MKT'
        order_price = self.datastorage.info[ticker]['Close'][-1] + sign *  0.0025 * self.datastorage.info[ticker]['Close'][-1]
        
        old_quantity = self.dict_quantities[ticker]

        
        if  old_quantity == 0:
            quantity = sign * floor(self.provisional_cash*0.1/order_price)
        elif old_quantity != 0:
            quantity = sign * abs(old_quantity) + sign * floor(self.provisional_cash*0.1/order_price)
        
        self.provisional_cash = self.provisional_cash - abs(quantity * order_price)
        
        return OrderEvent(ticker,order_type,quantity,order_price,direction)
           

            
    
    
    
