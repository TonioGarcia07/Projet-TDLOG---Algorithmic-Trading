#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
strategy.py: classe qui va contenir les differentes strategies qu'on veut
tester/appliquer. Elles vont generer les signals d'achat/vente sur un actif
et posteriorment la classe portfolio va gestioner le volume du contrat.
"""

from events import TradeEvent
import operator

class Strategy():
    """
    Classe mère des différentes strategies.
    """
    def __init__(self,data,datastorage,events,label_list):
        """
        data: DataManager instance qui continet les cotations
        events: Queue d'Events
        """
        self.data = data
        self.ticker_list =self.data.ticker_list
        self.events = events
        self.datastorage = datastorage
        self.datastorage.generate_keys(label_list)
        self.bought = {ticker:0 for ticker in self.ticker_list}
    
    def calculate_MovingAverage(self,ticker,frame):
        if len(self.datastorage.info[ticker]['Close'])>=frame:
            movave = 1/frame * (sum(self.datastorage.info[ticker]['Close'][-frame:]))
        else:
            movave = None
        return movave
        
    def ConditionBuy1(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-1]>=self.datastorage.info[ticker]['MAL'][-1])
    
    def ConditionBuy2(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-2]<=self.datastorage.info[ticker]['MAL'][-2])
        
    def ConditionBuy3(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-2]>=self.datastorage.info[ticker]['MAL'][-2])    
    
    def ConditionBuy4(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-3]<=self.datastorage.info[ticker]['MAL'][-3])
    
    def ConditionBuy5(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-1]>=self.datastorage.info[ticker]['MAS'][-2])
    
    def ConditionSell1(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-1]<=self.datastorage.info[ticker]['MAL'][-1])
    
    def ConditionSell2(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-2]>=self.datastorage.info[ticker]['MAL'][-2])
    
    def ConditionSell3(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-2]<=self.datastorage.info[ticker]['MAL'][-2])
    
    def ConditionSell4(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-3]>=self.datastorage.info[ticker]['MAL'][-3])
    
    def ConditionSell5(self,ticker):
        return (self.datastorage.info[ticker]['MAS'][-1]<=self.datastorage.info[ticker]['MAS'][-2])
    
    def ConditionOut1(self,ticker):
        return (self.datastorage.info[ticker]['MtM'][-1]<=-0.05*self.datastorage.info[ticker]['Fix_Value'][-1])
    
    def ConditionOut2(self,ticker):
        return (self.datastorage.info[ticker]['MtM'][-1]>=0.1*self.datastorage.info[ticker]['Fix_Value'][-1])

class BuyandHoldStrategy(Strategy):
    """
    Classe fille de Strategy qui donne un signal BUY pour tous
    les tickers dans le ticker_list du DataManager
    """
    
    def __init__(self, data,datastorage, events):
        self.label_list = ['Date','Open','High','Low','Close','Volume','Adj Close','Trade']
        super().__init__(data,datastorage,events,self.label_list)
        
 
    def generate_trade_signal(self,event):
        if event.type == 'DATA':
            for ticker in self.ticker_list:
                bar = self.data.get_last_ticker(ticker,N=1)
                if bar is not None and bar !=[]:
                    self.datastorage.bar_info_stocking(ticker,bar)
                    signal = 0
                    if self.bought[ticker] == 0:
                        self.events.put(TradeEvent(ticker,bar[0][0],'BUY'))
                        signal = 1
                        self.bought[ticker] = signal
                self.datastorage.info[ticker]['Trade'].append(signal)  

class MovingAverageStrategy(Strategy):
    """
    Classe fille de Strategy qui utilise la moyenne mobile pour introduire des 
    signals d'achat ou vente en fonction de la relation entre moyennes mobiles et
    profiteer des marches avec une forte tendance
    """
    
    def __init__(self, data, datastorage, events, small, long):
        """
        data: DataManager instance qui continet les cotations
        events: Queue d'Events
        small: fourchette de la moyenne mobile courte
        long: fourchette de la moyenne mobile longue
        """
        self.small = small
        self.long = long
        self.label_list = ['Date','Open','High','Low','Close','Volume','Adj Close','Trade','Out','MAS','MAL']
        # MMS:moving average small MML: moving average long
        super().__init__(data,datastorage,events,self.label_list)
          
    def generate_trade(self,event,val):
        if event.type == 'DATA':
            for ticker in self.ticker_list:
                bar = self.data.get_last_ticker(ticker,N=1)
                if bar is not None and bar !=[]:
                    self.datastorage.bar_info_stocking(ticker,bar)
                    self.datastorage.info[ticker]['MAS'].append(self.calculate_MovingAverage(ticker,self.small))
                    self.datastorage.info[ticker]['MAL'].append(self.calculate_MovingAverage(ticker,self.long))
                    signal = 0
                    out = 0
                    if len(self.datastorage.info[ticker]['MAL'])>=val:
                        if (self.datastorage.info[ticker]['MAL'][-val] != None):
                            if self.ConditionBuy(ticker):
                                if self.bought[ticker] == 0 or self.bought[ticker] == -1:
                                    self.events.put(TradeEvent(ticker,bar[0][0],'BUY'))
                                    signal = 1
                            if self.ConditionSell(ticker):
                                if self.bought[ticker] == 0 or self.bought[ticker] == 1:
                                    self.events.put(TradeEvent(ticker,bar[0][0],'SELL'))
                                    signal = -1
                            if self.ConditionOut(ticker):
                                if self.bought[ticker] == -1 or self.bought[ticker] == 1:
                                    self.events.put(TradeEvent(ticker,bar[0][0],'OUT'))
                                    signal = 0
                                    out = -self.bought[ticker]
                    self.bought[ticker] = signal
                    self.datastorage.info[ticker]['Trade'].append(signal)
                    self.datastorage.info[ticker]['Out'].append(out) 

              
class MovingAverage_1_Strategy(MovingAverageStrategy):
    def __init__(self, data, datastorage, events, small, long):
        super().__init__(data,datastorage, events, small, long)
    
    
    def generate_trade_signal(self, event):
        self.generate_trade(event,2)
    
    def ConditionBuy(self,ticker):
        return (self.ConditionBuy1(ticker) and self.ConditionBuy2(ticker))
        
    def ConditionSell(self,ticker):
        return (self.ConditionSell1(ticker) and self.ConditionSell2(ticker))
    
    def ConditionOut(self,ticker):
        return (self.ConditionOut1(ticker) or self.ConditionOut2(ticker) )
    
    
        
        