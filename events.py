#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
events.py : classes qui stocke les differentes possibles accions a executer.
classe mère: Event
classe fille1: DataEvent
classe fille2: TradeEvent
classe fille3: OrderEvent
classe fille4: BookedEvent
...classe fille5: TweetEvent
...classe fille6: ImageEvent
"""

class Event:
    """
    Classe Mère trivial d'où heritent toutes les autres classes Event
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
        self.type = 'DATA'
    
    def __str__(self):
        return self.type

class TradeEvent(Event):
    """
    Classe fille d'Event qui donne l'information d'une opportunité
    d'investissement detectée
    """
    def __init__(self,ticker,datetime,direction):
        """
        Parametres:
        ticker: symbol+suffix de l'actif
        datetime: timestamp du signal
        direction: direction de l'operation 'buy' ou 'sell'
        """
        self.type = 'TRADE'
        self.ticker = ticker
        self.datetime = datetime
        self.direction = direction
    
    def __str__(self):
        return "{} signal {}-{} generée à {}".format(self.type, 
                self.direction, self.ticker,self.datetime)

class OrderEvent(Event):
    """
    Classe fille d'Event qui est generé par la classe Portefeuille
    et qui est la modification du signal TradeEvent pour l'adapté
    au niveau de risque et au portefeuille
    """
    def __init__(self,ticker,order_type,quantity,order_price,direction,close_old_position=1):
        """
        Parametres:
        ticker: symbol+suffix de l'actif
        order_type: type d'ordre à executer
        volume: nombre d'unités d'actif
        direction: direction de l'operation 'BUY' ou 'SELL'
        close_old_position = 1 nouvelle position, -1 old position to be closed
        """
        self.type = 'ORDER'
        self.ticker = ticker
        self.order_type = order_type
        self.quantity = quantity
        self.close_old_position = close_old_position
        self.order_price = order_price
        self.direction = direction
    
    def __str__(self):
        return "{} signal generée: {} {} {} {} {}".format(self.type, 
                self.direction, self.order_type, self.quantity, self.ticker,self.order_price)

class BookedEvent(Event):
    """
    Classe fille d'Event qui indique que l'ordre a été executé ou enregistré
    et qui continet les caracteristiques de  l'operation saisie.
    """
    def __init__(self, datetime, ticker, quantity, direction, costs=None):
        self.type = 'BOOKED'
        self.datetime = datetime
        self.ticker = ticker
        self.quantity = quantity
        self.direction = direction
        self.calculer_costs(costs)
    
    def calculer_costs(self,costs):
        """
        Calcul des frais de transaction ( les valeurs typiques pour un broker
        competitif)
        """
        if costs is None :
            if self.quantity < 500:
                self.costs = max(1.3,0.015*self.quantity)
            else:
                self.costs = max(1.3,0.01*self.quantity)
        else: 
            self.costs = costs

class TweetEvent(Event):
    pass

class ImageEvent(Event):
    pass

