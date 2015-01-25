#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from pandas.io.data import DataReader
from pandas import DataFrame
import sqlite3
import urllib2

def obtain_list_of_db_tickers():
    try:
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
    yahoo_url = "http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range=100d/csv".format(ticker)
    try:
        yf_data = urllib2.urlopen(yahoo_url).readlines()[32:]
        cotation_data = []
        for line in yf_data:
            p = line.strip().split(',')
            cotation_data.append((ticker,datetime.fromtimestamp(int(p[0])).strftime('%Y-%m-%d %H:%M'),p[4],p[2],p[3],p[1],p[5]))
    except Exception, e:
        print "Could not download Yahoo data{}".format(e)
    return cotation_data

def get_daily_historic_data_yahoo(ticker):
    try:
        date_start=datetime(2000,1,1)
        cotation_data = DataReader(ticker,  "yahoo", date_start)
        return cotation_data
    except Exception,e:
        print("There was a probem getting the ticker: {}".format(e))
    
def insert_prices_db(market_data):
    try:
        con = sqlite3.connect('test.db')
        column_str = "(ticker, Date, Open, High, Low, Close, Volume)"
        insert_str = ("(" + "?," * 6 + "?)" )
        final_str = "INSERT INTO prices_min {} VALUES {}".format(column_str,insert_str)
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
            
def insert_dataframe_to_sql(market_data):
    try:
        con = sqlite3.connect('test.db')
        market_data.to_sql("prices",con, if_exists='append')   
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))       
    finally:
        if con:
            con.close()
 
def print_prices_db(ticker,db):
    select_str="SELECT * FROM {} WHERE ticker = '{}'".format(db,ticker)
    try:
        con = sqlite3.connect('test.db')
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

def delete_rows_prices(db):
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        delete_str="DELETE FROM {}".format(db)
        # Using the sql connection, faire une request pour obtir le tableau exchanges
        with con:
            cur = con.cursor()
            cur.execute(delete_str)
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

def minute_data():
    delete_rows_prices('prices_min')
    tickers = obtain_list_of_db_tickers()
    for (symbol_id, symbol ,suffix) in tickers:
        try:
            print(symbol_id,symbol+suffix)
            yf_data = get_minute_historic_data_yahoo(symbol+suffix)
            insert_prices_db(yf_data)    
            #print_prices_db(symbol+suffix,'prices_min')
        except Exception, e :
            print("There was a probem with the ticker: {}  error: {}".format(symbol+suffix,e))

#        a = input()
#        if a==2:break  
        
def daily_data():
    delete_rows_prices('prices')
    tickers = obtain_list_of_db_tickers()
    for (symbol_id, symbol ,suffix) in tickers:
        try:
            print(symbol_id,symbol+suffix)
            yf_data = get_daily_historic_data_yahoo(symbol+suffix)
            yf_data['ticker']=(symbol+suffix)
            insert_dataframe_to_sql(yf_data)    
            #print_prices_db(symbol+suffix,'prices')
        except Exception, e :
            print("There was a probem with the ticker: {}  error: {}".format(symbol+suffix,e))

#        a = input()
#        if a==2:break   


   
if __name__=="__main__":
    #daily_data()
    #minute_data()
    print_prices_db('BNP.PA','prices_min')
            
        
        
        
 

















   
