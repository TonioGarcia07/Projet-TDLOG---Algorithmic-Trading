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
        except e:
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
        except e:
            if self.con:
                self.con.rollback()
                raise ErrorConnexion(self.base, table, e)
        finally:
            self.deconnexion()
            
    def printing(self, table):
        try:
            self.connexion()
            self.cur.execute("SELECT * FROM "+ table)
            data = self.cur.fetchall()
            for line in data:
                print(line)
        except e:
            raise ErrorConnexion(self.base, table, e)
        finally:
            self.deconnexion()
          
    
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
        
if __name__=="__main__":
    Exchange = DatabaseExchanges('test.db')
    Exchange.new()
    Exchange.remplissage()
    Exchange.affichage()
    















