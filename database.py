
"""
Class Database: cette classe a pour but la création, remplissage 
et affichage des tableaux de la base de données generée
"""
import sqlite3
import lxml.html
from datetime import datetime
from pandas.io.data import DataReader
from urllib.request import urlopen
import pandas as pd
from pandas.lib import Timestamp



class ErrorDatabaseConnexion(Exception):
    def __init__(self, base, msg, table= 'Not specified' ):
        self.base = base
        self.table = table
        self.message = msg    
    
    def __str__(self):
        return ("Il y a un erreur avec la base de données: {} le tableau: {} problème: {}".format(self.base, self.table, self.message)) 

class ErrorInternetConnexion(Exception):
    def __init__(self, path, msg):
        self.base = path
        self.message = msg    
    
    def __str__(self):
        return ("Il y a un erreur avec l'accés à: {} problème: {}".format(self.path, self.message)) 


    
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
                raise ErrorDatabaseConnexion(self.base, e , table)
        finally:
            self.deconnexion()
    
    def insert(self, table, command_str, data, delete='yes'):
        insert_str = ("(" + "?," * (len(command_str.split(','))-1) + "?)" )
        final_str = "INSERT OR IGNORE INTO {} {} VALUES {}".format(table,command_str,insert_str)
        try:
            self.connexion()
            if delete=='yes':self.cur.execute("DELETE FROM "+ table)
            self.cur.executemany(final_str, data)
            self.con.commit()
        except sqlite3.Error as e:
            if self.con:
                self.con.rollback()
                raise ErrorDatabaseConnexion(self.base, e, table)
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
            raise ErrorDatabaseConnexion(self.base, e, table)
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
                raise ErrorDatabaseConnexion(self.base, e)
        finally:
            self.deconnexion()
            return data
    
    def toDataframe(self,table,columns_str,ticker):
        try:
            self.connexion()
            cotation_ticker_df = pd.read_sql("""SELECT {} FROM {} WHERE ticker='{}'""".format(columns_str,table,ticker), self.con) #,index_col='Date')
            #cotation_ticker_df = cotation_ticker_df.astype(str)
            #pd.to_datetime(cotation_ticker_df.index, errors= 'raise',format ='%Y-%m-%d %H:%M:%S')
            cotation_ticker_df.Date = cotation_ticker_df.Date.apply(Timestamp)
            cotation_ticker_df.set_index('Date', inplace=True)
        except sqlite3.Error as e:
            raise ErrorDatabaseConnexion(self.base, e, table)
        finally:
            self.deconnexion()
            return cotation_ticker_df
            
        
        
        
class DatabaseExchanges(Database):
    def __init__(self, nombase):
        super().__init__(nombase)
        self.table = 'exchanges'
        self.columns_str = "exchange_id,exchange_name,suffix,country,delay"
    
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
        self.columns_str = "symbol_id, exchange_name, symbol,instrument,name,sector,currency"
    
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
            if sd['symbol']=='PP' or sd['symbol']=='SOLB' :pass
            else: self.symbols.append(('Paris Stock Exchange', sd['symbol'],'stock', sd['name'],sd['sector'],'EUR'))      
    
        
    def yahoo_scan(self):
        #self.obtain_SNP500()
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
        self.columns_str = """Date, Open, High, Low, Close,  Volume, "Adj Close" """
    
    def new(self):
        command_str =("""CREATE TABLE daily_prices (
                       ticker varchar(32) NOT NULL,
                       Date date NOT NULL,
                       Open decimal(19,4) NULL,
                       High decimal(19,4) NULL,
                       Low decimal(19,4) NULL,
                       Close decimal(19,4) NULL,
                       Volume float(1) NULL,
                       'Adj Close' decimal(19,4) NULL,
                       PRIMARY KEY(ticker,Date) ON CONFLICT IGNORE);""")
                       
        self.creation(self.table ,command_str)
    
    def obtain_tickers(self):
        command_str = ("SELECT S.symbol_id, S.symbol, E.suffix FROM symbols S JOIN exchanges E ON S.exchange_name = E.exchange_name ")
        self.tickers = self.picking(command_str)
        
    def get_prices_df(self,ticker, date_start, date_end):
        try:
            cotation_data = DataReader(ticker,  "yahoo", date_start, date_end)
        except Exception as e:
            raise ErrorInternetConnexion('yahoo DataReader',  e)
        return cotation_data
    
    def get_prices(self,date_start=datetime(2009,1,1), date_end=datetime(2014,12,1)):
        #multiprocessing
        for (symbol_id, symbol ,suffix) in self.tickers:
            #print(symbol_id,symbol+suffix)
            cotation_data = self.get_prices_df(symbol+suffix, date_start, date_end)
            print(cotation_data)
            print(cotation_data.index)
            try:
                self.connexion()
                cotation_data['ticker']=symbol+suffix
                cotation_data.to_sql('daily_prices',self.con,if_exists='append')
            except sqlite3.Error as e:
                raise ErrorDatabaseConnexion(self.base, e, self.table)
            finally:
                self.deconnexion()
                
    def update_prices(self,date_start=datetime(2014,12,24), date_end=datetime.today()):
        for (symbol_id, symbol ,suffix) in self.tickers:
            #print(symbol_id,symbol+suffix)
            cotation_df = self.get_prices_df(symbol+suffix, date_start, date_end)
            cotation_df['ticker']=symbol+suffix
            cotation_df['Volume'] = cotation_df['Volume'].astype(float)
            cotation_list=cotation_df.to_records()
            command_str = "(Date , Open, High, Low, Close, Volume, 'Adj Close', ticker)"
            self.insert( self.table, command_str, cotation_list, 'no')
  
    def affichage(self):
        self.printing(self.table)

class DatabaseIntradayPrices(Database):
    def __init__(self, nombase,table = 'intraday_prices'):
        super().__init__(nombase)
        self.table=table
        self.tickers = []
        self.columns_str = "Date, Open, High, Low, Close, Volume"
    
    def new(self):
        command_str =("""CREATE TABLE {} (
                       ticker varchar(32) NOT NULL,
                       Date_timestamp float(4) NULL,
                       Date datetime NOT NULL,
                       Open decimal(19,4) NULL,
                       High decimal(19,4) NULL,
                       Low decimal(19,4) NULL,
                       Close decimal(19,4) NULL,
                       Volume float(1) NULL,
                       PRIMARY KEY (ticker,Date_timestamp) ON CONFLICT IGNORE);""".format(self.table))
                       
        self.creation(self.table ,command_str)
    
    def obtain_tickers(self):
        command_str = ("SELECT S.symbol_id, S.symbol, E.suffix FROM symbols S JOIN exchanges E ON S.exchange_name = E.exchange_name ")
        self.tickers = self.picking(command_str)
        
    def get_prices_list(self,ticker,days):
        yahoo_url = "http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}d/csv".format(ticker,days)
        try:
            yf_data = urlopen(yahoo_url).readlines()[32:]
            cotation_data = []
            for line in yf_data:
                line = line.decode('utf-8')
                p = line.strip().split(',')
                print(ticker)
                cotation_data.append((ticker,p[0],datetime.fromtimestamp(int(p[0])).strftime('%Y-%m-%d %H:%M'),p[4],p[2],p[3],p[1],p[5]))
        except Exception as e:
            raise ErrorInternetConnexion('yahoo acces',  e)
        return cotation_data
    
    def get_prices(self,days=100):
        #multiprocessing
        for (symbol_id, symbol ,suffix) in self.tickers:
            #print(symbol_id,symbol+suffix)
            cotation_list = self.get_prices_list(symbol+suffix,days)
            command_str = "(ticker,Date_timestamp,Date , Open, High, Low, Close, Volume)"
            self.insert( self.table, command_str, cotation_list, 'no')
                
    def update_prices(self):
        self.get_prices()
  
    def affichage(self):
        self.printing(self.table)
      
if __name__=="__main__":
    base ='test.db'
    Exchange = DatabaseExchanges(base)
    Exchange.new()
    Exchange.remplissage()
    Exchange.affichage()
    Symbols = DatabaseSymbols(base)
    Symbols.new()
    Symbols.remplissage()
    Symbols.affichage()
    DailyPrices = DatabaseDailyPrices(base)
    DailyPrices.new()
    #DailyPrices.obtain_tickers()
    DailyPrices.tickers=[(1,'BNP','.PA')]
    DailyPrices.get_prices()
    a = DailyPrices.toDataframe(DailyPrices.table, DailyPrices.columns_str,'BNP.PA')
    print(a.index)
    #DailyPrices.affichage()
    #DailyPrices.update_prices()
    #DailyPrices.affichage()
#    IntradayPrices = DatabaseIntradayPrices(base)
#    IntradayPrices.new()
#    #Intraday.obtain_tickers()
#    IntradayPrices.tickers=[(1,'BNP','.PA')]
#    IntradayPrices.get_prices()
#    IntradayPrices.affichage()

    
    
    

    















