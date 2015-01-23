#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
CREATION DATABASE:
Creation des tableaux ou reset des anciens tableaux et creation
pour stocker les informations des marchés financiers et cotations
des produits.

"""

import sqlite3

def creation_db():
    """ 
    Creation Databases: symbols, exchanges,prices
    
    Database symbols:
    symbol_id: INTEGER PRIMARY KEY
    exchange_name: nom de l'exchange du produit
    symbol: symbol utilisé pour identifier le produit
    instrument: type d'instrument
    name: nom du produit
    sector: secteur economique du produit
    currency: monaie du produit
    created_date
    last_updated_date  
    
    Database exchanges:
    exchange id: INTEGER PRIMARY KEY
    exchange_name: nom de l'exchange du produit (reference avec symbol)
    suffix: suffix utilisé dans le distribuiteur de données (ex. Yahoo Finance)
    country: pays de l'exchange
    delay: le retard entre la cotation du prix et la publication sur le distributeur
    
    Database prices:
    price_id: INTEGER PRIMARY KEY
    ticker: symbol(symbols) + suffix(exchanges)
    date_time: date et heure de la cotation
    close,high,low,open: prix de cotation
    volume: volume 
    """
        
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
                       
        # On utilise la connexion SQL pour créer les tableaux
        with con:
            cur = con.cursor()
            # On elimine les anciens tableux s'ils existent.
            cur.execute("""DROP TABLE IF EXISTS symbols;""")
            cur.execute("""DROP TABLE IF EXISTS exchanges;""")
            cur.execute("DROP TABLE IF EXISTS prices;")
            cur.execute("DROP TABLE IF EXISTS prices_min;")
                        
            # Creation du tableau symbols
            cur.executescript("""CREATE TABLE symbols (
                       symbol_id INTEGER PRIMARY KEY,
                       exchange_name int NULL,
                       symbol varchar(32) NOT NULL,
                       instrument varchar(64) NOT NULL,
                       name varchar(255) NULL,
                       sector varchar(255) NULL,
                       currency varchar(32) NULL, 
                       created_date datetime NOT NULL,
                       last_updated_date datetime NOT NULL);""")
            
            cur.executescript("""CREATE TABLE exchanges (
                       exchange_id INTEGER PRIMARY KEY,
                       exchange_name varchar(64) NOT NULL,
                       suffix varchar(32) NULL,
                       country varchar(64) NOT NULL,
                       delay varchar(64) NULL);""")
                       
            cur.executescript("""CREATE TABLE prices (
                       price_id INTEGER PRIMARY KEY,
                       ticker varchar(32) NOT NULL,
                       Date datetime NOT NULL,
                       Open decimal(19,4) NULL,
                       High decimal(19,4) NULL,
                       Low decimal(19,4) NULL,
                       Close decimal(19,4) NULL,
                       Volume float(1) NULL,
                       'Adj Close' decimal(19,4) NULL);""")
                
            cur.executescript("""CREATE TABLE prices_min (
                       price_id INTEGER PRIMARY KEY,
                       ticker varchar(32) NOT NULL,
                       Date datetime NOT NULL,
                       Open decimal(19,4) NULL,
                       High decimal(19,4) NULL,
                       Low decimal(19,4) NULL,
                       Close decimal(19,4) NULL,
                       Volume float(1) NULL);""") 
               
            con.commit()
                
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))
            
    finally:
        if con:
            con.close()

if __name__=="__main__":
    creation_db()







