#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
obtain_symbols: obtention des symbols (tickers) des actifs dans
yahoo finance pour les utiliser après pour importer leur cotation
"""

import datetime
import lxml.html
import sqlite3

from math import ceil

def obtain_snp500():   
    
    now = datetime.datetime.utcnow()

    page = lxml.html.parse('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    symbolslist = page.xpath('//table[1]/tr')[1:]
 	symbols = []
    number_stocks=502
    for symbol in symbolslist:
        tds = symbol.getchildren()   
        sd = {'symbol': tds[0].getchildren()[0].text,
              'name':tds[1].getchildren()[0].text,
              'sector':tds[3].text}
        symbols.append(('S & P Indices', sd['symbol'],'stock', sd['name'],sd['sector'],'USD',now,now))
        if len(symbols)==number_stocks: break
    return symbols

def obtain_CAC40():
    now = datetime.datetime.utcnow()
    page = lxml.html.parse('http://en.wikipedia.org/wiki/CAC_40')
    symbolslist = page.xpath('//table[2]/tr')[1:]
   
    symbols = []
    for symbol in symbolslist:
        tds = symbol.getchildren()   
        sd = {'symbol': tds[0].text,
              'name':tds[1].getchildren()[0].text,
              'sector':tds[2].text}
        
        symbols.append(('Paris Stock Exchange', sd['symbol'],'stock', sd['name'],sd['sector'],'EUR',now,now))
        
    return symbols

def delete_rows_symbols():
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        # Using the sql connection, faire une request pour obtir le tableau exchanges
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM symbols")
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

def insert_symbols(symbols):
    """Insert the S&P500 symbols into the database."""
    try:
        # Connect to Database
        con = sqlite3.connect('test.db')
        
        # Create the insert strings
        column_str = "(exchange_name,symbol, instrument, name, sector, currency, created_date, last_updated_date)"
        insert_str = ("(" + "?," * 7 + "?)" )
        final_str = "INSERT INTO symbols {} VALUES {}".format(column_str,insert_str)
        
        # Using the sql connection, carry out an INSERT INTO for every symbol
        with con:
            cur = con.cursor()
            for i in range(0,int(ceil(len(symbols)/100.0))):
                cur.executemany(final_str, symbols[i*100:(i+1)*100])
            
            con.commit()
                
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))
            
    finally:
        if con:
            con.close()

def print_symbols_db():
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        # Using the sql connection, faire une request pour obtir le tableau symbols
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM symbols")
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
    delete_rows_symbols()
    symbolsCAC40 = obtain_CAC40()   
    insert_symbols(symbolsCAC40)
    #symbolsSNP500 = obtain_snp500()   
    #insert_symbols(symbolsSNP500)
    
    print_symbols_db()




































