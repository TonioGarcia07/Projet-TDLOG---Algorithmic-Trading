#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test

"""
from database import DatabaseDailyPrices
from datetime import datetime
from datamanager import SQLDataManagerBacktest
from datastorage import DataStorage
from strategy import BuyandHoldStrategy, MovingAverageStrategy, MovingAverage_1_Strategy
from portfolio import MovAvePortfolio
import queue
import time


if __name__=="__main__":
 
    # Definition des parametres:
    # base: base de données
    # tickers: actif a étudier
    # initial_capital: capital initial du portefeuille
    # vitesse: vitesse de chaque iteration de nouvelle bar: (Date, Open, High....)
    # start_date : date de commencement du backtest
    # end_date: date de fin du backtest 

    base ='test.db'
    tickers =['AC.PA']#,'GSZ.PA','EDF.PA']
    initial_capital = 10000
    vitesse = 0.01
    start_date = datetime(2012,5, 2)
    end_date = datetime(2013, 6, 30)
    
    # Construction de la Queue qui va stocker les events : DATA et TRADE 
    Trivial = queue.Queue()
    # Construction de la Queue qui va stocker les events ORDRES
    carnet_ordres = queue.Queue()
    
    # Creation d'un instance Database pour se connecter a la base SQL
    # Si on veut que requeter la base on va créer la instance seulement
    DailyPrices = DatabaseDailyPrices(base)
    # (on peut la recreer =new(), get_price() et l'actualiser update_price())
    # DailyPrices.new()
    # DailyPrices.get_prices()
    # DailyPrices.update_prices()
   
    
    # Creation instance DataManager pour requeter la base de donnes et generé le
    # "marché" = iterator avec les cotations  (methode .market()) 
    DataManager1 = SQLDataManagerBacktest(Trivial,DailyPrices,tickers,start_date,end_date)
    DataManager1.market()
    
    # Creation instanse DataStorage pour stocker les donnes generes
    DataStorage1 = DataStorage(tickers)
    
    # Creation instance strategy pour appliquer une strategie et gesitonner l'event DATA
    # et produire event TRADE qui vont se placer dans la Queue Trivial
    Strategy1 = MovingAverage_1_Strategy(DataManager1,DataStorage1,Trivial,5,20)
    # Strategy1 = BuyandHoldStrategy(DataManager1,DataStorage1,Trivial)
    # Strategy1 = MovingAverageStrategy(DataManager1,DataStorage1,Trivial,10,60)
    
    # Creation instance Portfolio pour traiter les events TRADE et mettre events ORDRE dans
    # la Queue carnet_ordres et executer les ordres
    Portfolio1 = MovAvePortfolio(DataStorage1,Trivial,initial_capital,carnet_ordres)
    
    # Event-Loop: pour chaque iteration:
    #       Extraction new data ---> generation Event Data
    #       Strategy. generate_trade_Signal(event) : processe le DATA et analyse 
    #           des signaux d'investissement selon les critères fournis. Soit genere un
    #           event TRADE, soit ne genere rien.
    #       On passe un deuxième boucle pour executer les ordres
    #       Actualsation du protfolio (calcul P&L, positions, MtM)
    #       Si strategy a generé event Trade: portfolio va considere la quantite a traiter
    #           et va genere l'ordre
    #       Extraction new data ...   
    
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
                    if event.type == 'DATA':
#                        print(event)
#                        for ticker in tickers:
#                            print(DataManager1.get_last_ticker(ticker))
                        
                        Strategy1.generate_trade_signal(event)
                        
                        while True:
                            try:
                                ordre = carnet_ordres.get(False)
                                print(ordre)
                                
                            except:
                                break
                            else:
                                Portfolio1.treat_OrderEvent(ordre)
                                
                        Portfolio1.update_portfolio_data()
                            
                    if event.type == 'TRADE':
                        print(event)
                        Portfolio1.treat_TradeEvent(event)
        
        time.sleep(vitesse)
    
    
#    for ticker in DataStorage1.info.keys():
#        print(ticker)
#        for (label,values) in DataStorage1.info[ticker].items():
#            if label in set(['Close','Quantity','Fix_Value','Trade','Market_Value','Value','MtM','Cash','Portfolio_Value']):
#                print(label)
#                for value in values:
#                    print(value)
#    

        
    
    

            
                        