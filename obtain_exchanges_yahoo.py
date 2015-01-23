#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
obtain_exchanges_yahoo: code pour obtenir l'information sur 
les differents exchenges ou marchés financiers.
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
            
if __name__=="__main__":
    exchanges = obtain_exchanges_yahoo()

    





















