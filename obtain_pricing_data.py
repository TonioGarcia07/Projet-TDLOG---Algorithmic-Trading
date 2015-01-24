#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from pandas.io.data import DataReader
import sqlite3
import urllib2

def obtain_list_of_db_tickers():
    """ Obtains a list of the ticker symbols in the database."""
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        with con:
            cur = con.cursor()
            cur.execute("SELECT S.symbol_id, S.symbol, E.suffix FROM symbols S JOIN exchanges E ON S.exchange_name = E.exchange_name ")
            data = cur.fetchall()
            return [(d[0],d[1],d[2]) for d in data]
    
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))
            
    finally:
        if con:
            con.close()
        
def get_minute_historic_data_yahoo(ticker):
       
    # Construct the Yahoo URL with the correct integer query parameters
    # 1.0 is the frequency
    # range=100d is the timeframe (100 days, but the maximum is 15)
    yahoo_url = "http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range=100d/csv".format(ticker)
    
    # Try connectiong to Yahoo Finance and obtaining the data
    # On failure, print an error message.
    try:
        yf_data = urllib2.urlopen(yahoo_url).readlines()[32:]
        prices = []
        for y in yf_data:
            p = y.strip().split(',')
            prices.append((ticker,datetime.datetime.fromtimestamp(int(p[0])).strftime('%Y-%m-%d %H:%M'),p[1],p[2],p[3],p[4],p[5]))
    except Exception, e:
        print "Could not download Yahoo data{}".format(e)
    return prices


def get_daily_historic_data_yahoo(ticker):
    yahoo_url = "http://finance.yahoo.com/q/hp?s={}&a=06&b=20&c=2000&d=00&e=11&f=2015&g=d".format(ticker)
    
    date_start=datetime.datetime(2000,1,1)
    print(date_start)
    date_end = datetime.datetime(2015,1,1)
    goog = DataReader(ticker,  "yahoo", date_start, date_end)
    return goog
    

    
def insert_prices_db(market_data):
    """Takes a list of tuples of daily data and adds it to the
    database. Appends the vendor ID and symbol ID to the data."""
    
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        # Creation des strings à inserter
        column_str = "(ticker, date_time, close, high, low, open, volume)"
        insert_str = ("(" + "?," * 6 + "?)" )
        final_str = "INSERT INTO prices {} VALUES {}".format(column_str,insert_str)
        
        # Using the sql connection, faire un INSERT INTO pour chaque exchange
        with con:
            cur = con.cursor()
            cur.executemany(final_str, market_data)
            con.commit()
            
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))
            
    finally:
        if con:
            con.close()
    
def print_prices_db(ticker):
    select_str="SELECT * FROM prices WHERE ticker = '{}'".format(ticker)
    print(select_str)
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        # Using the sql connection, faire un INSERT INTO pour chaque exchange
        with con:
            cur = con.cursor()
            cur.execute(select_str)
            data = cur.fetchall()
            for row in data:
                print(row)
            
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))
            
    finally:
        if con:
            con.close()
    



    
if __name__=="__main__":
    #print_prices_db("VIE.PA")
    #google =get_daily_historic_data_yahoo("GOOG")
    print(google)
    print(google.index)
    
    #date_start=datetime.datetime(2010,2,1)
    print(date_start)
    date_end = datetime.datetime(2015,1,1)
    goog = DataReader(,  "yahoo", date_start, date_end)
    print(goog)
    
    
#    tickers = obtain_list_of_db_tickers()
#    i=0
#    for (symbol_id, symbol ,suffix) in tickers:
#        print(symbol_id,symbol+suffix)
#        yf_data = get_daily_historic_data_yahoo(symbol+suffix)
#        insert_prices_db(yf_data)
#        i=i+1
#        print(i)
#        if len(yf_data)>1:
#            print(yf_data.pop(0))
#            print(yf_data.pop())
#        else:
#            print("="*50)
        
        
        #a = input()
        #if a==2:break


    
    
