#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
datastorage.py: classe qui va contenir les differentes infromations generées par
Strategy and Portfolio
"""


class DataStorage():
    """
    
    """
    def __init__(self,ticker_list):
        self.ticker_list = ticker_list
        self.info = {ticker:{} for ticker in self.ticker_list}
        self.bar_labels = ['Date','Open','High','Low','Close','Volume','Adj Close']
        
    def generate_keys(self,labels_list):
        for ticker in self.ticker_list:
            for label in labels_list:
                self.info[ticker][label]=[]
    
    def bar_info_stocking(self,ticker,bar):
        self.info[ticker]['Date'].append(bar[0][0])
        for i in range(1,7):
            self.info[ticker][self.bar_labels[i]].append(bar[0][1][i-1])        
       
    def info_stocking(self,information):
        for ticker in self.ticker_list:
            for (label,value) in information:
                self.info[ticker][label].append(value)

    
     