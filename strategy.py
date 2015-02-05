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
    def __init__(self,data,events,info_list):
        """
        data: DataManager instance qui continet les cotations
        events: Queue d'Events
        """
        self.data = data
        self.ticker_list =self.data.ticker_list
        self.events = events
        self.info = self._generate_base_for_info(self.ticker_list,info_list)
        
    def _generate_base_for_info(self,ticker_list,info_list):
        info = {}
        for ticker in ticker_list:
            info[ticker]={element:[] for element in info_list}
        return info
    
    def bar_info_stocking(self,ticker,bar):
        self.info[ticker]['Date'].append(bar[0][0])
        for i in range(1,7):
            self.info[ticker][self.info_list[i]].append(bar[0][1][i-1])
    
    def signal_info_stocking(self,ticker,signal):
        self.info[ticker]['Trade'].append(signal) 

class BuyandHoldStrategy(Strategy):
    """
    Classe fille de Strategy qui donne un signal BUY pour tous
    les tickers dans le ticker_list du DataManager
    """
    
    def __init__(self, data, events):
        self.info_list = ['Date','Open','High','Low','Close','Volume','Adj Close','Trade']
        super().__init__(data,events,self.info_list)
        self.bought = {ticker:0 for ticker in self.ticker_list}
 
    def generate_trade_signal(self,event):
        if event.type == 'DATA':
            for ticker in self.ticker_list:
                bar = self.data.get_last_ticker(ticker,N=1)
                if bar is not None and bar !=[]:
                    self.bar_info_stocking(ticker,bar)
                    signal = 0
                    if self.bought[ticker] == 0:
                        self.events.put(TradeEvent(ticker,bar[0][0],'BUY'))
                        signal = 1
                        self.bought[ticker] = signal
                self.signal_info_stocking(ticker, signal)    

class MovingAverageStrategy(Strategy):
    """
    Classe fille de Strategy qui utilise la moyenne mobile pour introduire des 
    signals d'achat ou vente en fonction de la relation entre moyennes mobiles et
    profiteer des marches avec une forte tendance
    """
    
    def __init__(self, data, events, small, long):
        """
        data: DataManager instance qui continet les cotations
        events: Queue d'Events
        small: fourchette de la moyenne mobile courte
        long: fourchette de la moyenne mobile longue
        """
        self.data = data
        self.ticker_list =self.data.ticker_list
        self.events = events
        self.small = small
        self.long = long
        self.bought = {ticker:0 for ticker in self.ticker_list}
        self.info_list = ['Date','Open','High','Low','Close','Volume','Adj Close','Trade','MAS','MAL']
        # MMS:moving average small MML: moving average long
        self.info = self._generate_base_for_info(self.ticker_list,self.info_list)
       
    def generate_trade_signal(self,event):
        if event.type == 'DATA':
            for ticker in self.ticker_list:
                bar = self.data.get_last_ticker(ticker,N=1)
                if bar is not None and bar !=[]:
                    self.bar_info_stocking(ticker,bar)
                    self.MovAverage_info_stocking(ticker)
                    signal = 0
                    if len(self.info[ticker]['MAL'])>=2:
                        if (self.info[ticker]['MAL'][-2] != None):
                            if (self.info[ticker]['MAS'][-1]>=self.info[ticker]['MAL'][-1]) and (self.info[ticker]['MAS'][-2]<=self.info[ticker]['MAL'][-2]):
                                if self.bought[ticker] == 0 or self.bought[ticker] == -1:
                                    self.events.put(TradeEvent(ticker,bar[0][0],'BUY'))
                                    signal = 1
                            if (self.info[ticker]['MAS'][-1]<=self.info[ticker]['MAL'][-1]) and (self.info[ticker]['MAS'][-2]>=self.info[ticker]['MAL'][-2]):
                                if self.bought[ticker] == 0 or self.bought[ticker] == 1:
                                    self.events.put(TradeEvent(ticker,bar[0][0],'SELL'))
                                    signal = -1
                    self.bought[ticker] = signal
                    self.signal_info_stocking(ticker, signal)

    def calculate_MovingAverage(self,ticker,frame):
        if len(self.info[ticker]['Close'])>=frame:
            movave = 1/frame * (sum(self.info[ticker]['Close'][-frame:]))
        else:
            movave = None
        return movave               
    
    def MovAverage_info_stocking(self,ticker):
        self.info[ticker]['MAS'].append(self.calculate_MovingAverage(ticker,self.small))
        self.info[ticker]['MAL'].append(self.calculate_MovingAverage(ticker,self.long))
        

                












       