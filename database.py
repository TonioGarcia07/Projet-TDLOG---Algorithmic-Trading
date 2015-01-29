#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Class Database: cette classe a pour but la création, remplissage 
et affichage des tableaux de la base de données generée
"""
import sqlite3
import lxml.html

class ErrorConnexion(Exception):
    def __init__(self, base, msg, table= 'Not specified' ):
        self.base = base
        self.table = table
        self.message = msg    
    
    def __str__(self):
        return ("Il y a un erreur avec la base de données: {} le tableau: {} problème: {}".format(self.base, self.table, self.message)) 
    
class Database:
    def __init__(self, nombase):
        self.base = nombase
    
    def connexion(self):
        self.con = sqlite3.connect(self.base)
        self.cur = self.con.cursor()
    
    def deconnexion(self):
        if self.con:
            self.con.close()
            
    def dropping(self, table):
        command_str = "DROP TABLE IF EXISTS " + str(table)
        self.cur.execute(command_str)
    
    def creation(self, table, command_str):
        try:   
            self.connexion()
            self.dropping(table)
            self.cur.executescript(command_str)
            self.con.commit()
        except sqlite3.Error as e:
            if self.con:
                self.con.rollback()
                raise ErrorConnexion(self.base, e , table)
        finally:
            self.deconnexion()
    
    def insert(self, table, command_str, data):
        insert_str = ("(" + "?," * (len(command_str.split(','))-1) + "?)" )
        final_str = "INSERT INTO {} {} VALUES {}".format(table,command_str,insert_str)
        try:
            self.connexion()
            self.cur.execute("DELETE FROM "+ table)
            self.cur.executemany(final_str, data)
            self.con.commit()
        except sqlite3.Error as e:
            if self.con:
                self.con.rollback()
                raise ErrorConnexion(self.base, e, table)
        finally:
            self.deconnexion()
            
    def printing(self, table):
        try:
            self.connexion()
            self.cur.execute("SELECT * FROM "+ table)
            data = self.cur.fetchall()
            for line in data:
                print(line)
        except sqlite3.Error as e:
            raise ErrorConnexion(self.base, e, table)
        finally:
            self.deconnexion()
    
    def picking(self,command_str):
        try:   
            self.connexion()
            self.cur.execute(command_str)
            data = self.cur.fetchall() 
        except sqlite3.Error as e:
            if self.con:
                self.con.rollback()
                raise ErrorConnexion(self.base, e)
        finally:
            self.deconnexion()
            return data
        

        
    
#    def toDataframe(self):
#        #para pasar a data frame o vector auto
        
        
class DatabaseExchanges(Database):
    def __init__(self, nombase):
        super().__init__(nombase)
        self.table = 'exchanges'
    
    def new(self):
        command_str =("""CREATE TABLE exchanges (
                         exchange_id INTEGER PRIMARY KEY,
                         exchange_name varchar(64) NOT NULL,
                         suffix varchar(32) NULL,
                         country varchar(64) NOT NULL,
                         delay varchar(64) NULL);""")
        self.creation(self.table ,command_str)
    
    def yahoo_scan(self):
        """ Telechargement de la information de Yahoo sur les exchanges """
        # On utilise xml.html pour télecharger la liste
        page = lxml.html.parse('http://finance.yahoo.com/exchanges')
        symbolslist = page.xpath('//table[2]/tr/td/table[1]/tr')[1:]
    
        # Lecture de symbolslist pour obtenir la liste exchanges
        exchanges = []
        for exchange in symbolslist:
            tds = exchange.getchildren()
            if tds[2].text=='N/A': # Convention: 'N/A'=''
                suffix = ''
            else:
                suffix = tds[2].text
            sd = {'exchange': tds[1].text,
                  'suffix':suffix,
                  'country':tds[0].text,
                  'delay':tds[3].text}
            exchanges.append((sd['exchange'], sd['suffix'], sd['country'], sd['delay'] ))

        return exchanges
        
    def remplissage(self):
        command_str = "(exchange_name, suffix, country, delay)"
        data = self.yahoo_scan()
        self.insert(self.table ,command_str,data)
    
    def affichage(self):
        self.printing(self.table)

class DatabaseSymbols(Database):
    def __init__(self, nombase):
        super().__init__(nombase)
        self.table = 'symbols'
        self.symbols = []
    
    def new(self):
        command_str =("""CREATE TABLE symbols (
                       symbol_id INTEGER PRIMARY KEY,
                       exchange_name int NULL,
                       symbol varchar(32) NOT NULL,
                       instrument varchar(64) NOT NULL,
                       name varchar(255) NULL,
                       sector varchar(255) NULL,
                       currency varchar(32) NULL);""")
        self.creation(self.table ,command_str)
    
    def obtain_SNP500(self):
        # Use libxml to download the list of S&P500 companies and obtain the symbol table
        page = lxml.html.parse('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        symbolslist = page.xpath('//table[1]/tr')[1:]
        number_stocks=502
        for symbol in symbolslist:
            tds = symbol.getchildren()   
            sd = {'symbol': tds[0].getchildren()[0].text,
                  'name':tds[1].getchildren()[0].text,
                  'sector':tds[3].text}
            # Create a tuple (for the DB format) and append to the grand list
            self.symbols.append(('S & P Indices', sd['symbol'],'stock', sd['name'],sd['sector'],'USD'))
            number_stocks -= 1
            if number_stocks == 0 : break
    
    def obtain_CAC40(self):
        # Use libxml to download the list of S&P500 companies and obtain the symbol table
        page = lxml.html.parse('http://en.wikipedia.org/wiki/CAC_40')
        symbolslist = page.xpath('//table[2]/tr')[1:]
        for symbol in symbolslist:
            tds = symbol.getchildren()   
            sd = {'symbol': tds[0].text,
                  'name':tds[1].getchildren()[0].text,
                  'sector':tds[2].text}
            # Create a tuple (for the DB format) and append to the grand list
            self.symbols.append(('Paris Stock Exchange', sd['symbol'],'stock', sd['name'],sd['sector'],'EUR'))      
    
    def yahoo_scan(self):
        self.obtain_SNP500()
        self.obtain_CAC40()
        
    def remplissage(self):
        command_str = "(exchange_name,symbol, instrument, name, sector, currency)"
        self.yahoo_scan()
        self.insert(self.table ,command_str,self.symbols)
    
    def affichage(self):
        self.printing(self.table)

class DatabaseDailyPrices(Database):
    def __init__(self, nombase):
        super().__init__(nombase)
        self.table = 'daily_prices'
        self.tickers = []
    
    def obtain_tickers(self):
        command_str = ("SELECT S.symbol_id, S.symbol, E.suffix FROM symbols S JOIN exchanges E ON S.exchange_name = E.exchange_name ")
        self.tickers = self.picking(command_str)
        #print(data)
        #self.tickers = [(d[0],d[1],d[2]) for d in data]

      
if __name__=="__main__":
    Exchange = DatabaseExchanges('test.db')
    Exchange.new()
    Exchange.remplissage()
    Exchange.affichage()
    Symbols = DatabaseSymbols('test.db')
    Symbols.new()
    Symbols.remplissage()
    Symbols.affichage()
    DailyPrices = DatabaseDailyPrices('test.db')
    prices = DailyPrices.obtain_tickers()
    print(DailyPrices.tickers)
    
    

    















