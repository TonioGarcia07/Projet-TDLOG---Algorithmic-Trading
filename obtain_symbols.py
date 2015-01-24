#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
obtain_symbols: obtention des symbols (tickers) des actifs dans
yahoo finance pour les utiliser après pour importer leur cotation
"""

import datetime
import lxml.html

def obtain_snp500():  
    now = datetime.datetime.utcnow()
    page = lxml.html.parse('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    symbolslist = page.xpath('//table[1]/tr')[1:]
	symbols = []

	for symbol in symbolslist:
        tds = symbol.getchildren()   
        sd = {'symbol': tds[0].getchildren()[0].text,
              'name':tds[1].getchildren()[0].text,
              'sector':tds[3].text}
        symbols.append(('S & P Indices', sd['symbol'],'stock', sd['name'],sd['sector'],'USD',now,now))
    return symbols

if __name__=="__main__":
	symbolsSNP500 = obtain_snp500()   
    



















