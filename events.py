#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
events.py : classes qui stocke les differentes possibles accions a executer.
classe mère: Event
classe fille1: DataEvent
classe fille2: TradeEvent
classe fille3: OrderEvent
classe fille4: BookedEvent
"""

class Event:
    """
    Classe Mère d'où heritent toutes les autres classes Event
    """
    pass

class DataEvent(Event):
    """
    Classe fille d'Event qui donne le signal de qu'une nouvelle
    entrée de données est disponible.
    Pendant le backtest sert a controler les lockhead bias qu'on a
    si on regard le futur pour construir la strategie
    """
    def __init__(self):
        self.tpye = 'DATA'
    
    def __str__(self):
        return self.type

class TradeEvent(Event):
    """
    Classe fille d'Event qui donne l'information d'une opportunité
    d'investissement detectée
    """
    def __init__(self,ticker,datetime,direction):
        """
        Parameters:
        ticker: symbol+suffix de l'actif
        datetime: timestamp du signal
        direction: direction de l'operation 'buy' or 'sell'
        """
        self.type = 'TRADE'
        self.ticker = ticker
        self.datetime = datetime
        self.direction = direction
    
    def __str__(self):
        return "{} signal generée à {}: {} {}".format(self.type, self.datetime, self.direction, self.ticker)

class OrderEvent(Event):
    """
    Classe fille d'Event qui est generé par la classe Portefeuille
    et qui est la modification du signal TradeEvent pour l'adapté
    au niveau de risque et au portefeuille
    """

    
        
    
