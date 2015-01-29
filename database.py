#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Class Database: cette classe a pour but la création, remplissage 
et affichage des tableaux de la base de données generée
"""
import sqlite3
import lxml.html

class ErrorConnexion(Exception):
    def __init__(self, base, table, msg):
        self.base = base
        self.table = table
        self.message = msg    
    
    def __str__(self):
        return ("Il y a un erreur avec la base de données: {} le tableau: {} problème: {}".format(self.base, self.table, self.message)) 
    
class Database:
    def __init__(self, base):
        self.base = base
    
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
        except sqlite3.Error, e:
            if self.con:
                self.con.rollback()
                raise ErrorConnexion(self.base, table, e)
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
        except sqlite3.Error, e:
            if self.con:
                self.con.rollback()
                raise ErrorConnexion(self.base, table, e)
        finally:
            self.deconnexion()
            
    def __str__(self):
        #print
    
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
            
    
    def toDataframe(self):
        #para pasar a data frame o vector auto
        
        
class DatabaseExchanges(Database):
    def __init__(self, base):
        super().__init__(base)
    
    def new(self):
        command_str =("""CREATE TABLE exchanges (
                         exchange_id INTEGER PRIMARY KEY,
                         exchange_name varchar(64) NOT NULL,
                         suffix varchar(32) NULL,
                         country varchar(64) NOT NULL,
                         delay varchar(64) NULL);""")
        self.creation('exchanges',command_str)
    
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
        self.insert('exchanges',command_str,data)
        















