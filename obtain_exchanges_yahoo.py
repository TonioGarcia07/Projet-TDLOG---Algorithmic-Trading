#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
obtain_exchanges_yahoo: code pour obtenir l'information sur 
les differents exchenges ou marchés financiers et le stocker 
dans le base de données test.db
On fait l'extraction de la information disponible dans le site web de yahoo:
http://finance.yahoo.com/exchanges
"""
import lxml.html
import sqlite3

def obtain_exchanges_yahoo():
    """ Telechargement de la information de Yahoo sur les exchanges """
   
    # On utilise xml.html pour télecharger la liste
    page = lxml.html.parse('http://finance.yahoo.com/exchanges')
    symbolslist = page.xpath('//table[2]/tr/td/table[1]/tr')[1:]
    
    # Lecture de symbolslist pour obtenir la liste exchanges
    # Convention: 'N/A'=''
    exchanges = []
    for exchange in symbolslist:
        tds = exchange.getchildren()
        if tds[2].text=='N/A':
            suffix = ''
        else:
            suffix = tds[2].text
            
        sd = {'exchange': tds[1].text,
              'suffix':suffix,
              'country':tds[0].text,
              'delay':tds[3].text}
        exchanges.append((sd['exchange'], sd['suffix'], sd['country'], sd['delay'] ))

    return exchanges 

def insert_exchanges_db(exchanges):
    """Insertion des exchanges dans la base de donnnees exchanges."""
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        # Creation des strings à inserter
        column_str = "(exchange_name, suffix, country, delay)"
        insert_str = ("(" + "?," * 3 + "?)" )
        final_str = "INSERT INTO exchanges {} VALUES {}".format(column_str,insert_str)
        
        # Using the sql connection, faire un INSERT INTO pour chaque exchange
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM exchanges")
            cur.executemany(final_str, exchanges)
            con.commit()
            
    except sqlite3.Error, e:
        if con:
            con.rollback()
            print("There was a probem with the Database: {}".format(e))
            
    finally:
        if con:
            con.close()

def print_exchanges_db():
    try:
        # Connexion a la base de données
        con = sqlite3.connect('test.db')
        
        # Using the sql connection, faire une request pour obtir le tableau exchanges
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM exchanges")
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
    #exchanges = obtain_exchanges_yahoo()
    #insert_exchanges_db(exchanges)
    print_exchanges_db()




















