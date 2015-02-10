#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
graphical_user_interface.py

"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg ,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

from database import DatabaseExchanges, DatabaseSymbols, DatabaseDailyPrices
from datetime import datetime
from datamanager import SQLDataManagerBacktest
from datastorage import DataStorage
from strategy import BuyandHoldStrategy, MovingAverageStrategy, MovingAverage_1_Strategy
from portfolio import MovAvePortfolio
import queue


LARGE_FONT= ("Verdana", 20)
NORM_FONT = ("Verdana", 15)
SMALL_FONT = ("Verdana", 8)

style.use("ggplot")



    

class GUIBacktest(tk.Tk):
    def __init__(self, Info, *args, **kwargs):
        """
        Construciton de l'app qui va contenir les differentes pages
        """
        tk.Tk.__init__(self, *args, **kwargs)
        
#        tk.Tk.wm_iconbitmap(self, default="trading.ico")
        tk.Tk.wm_title(self,"Algorithmic Trading Station")
        
        self.geometry("720x300")
        self.Info = Info
        container = ttk.Frame(self, padding =(5,5,12,0))
        container.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        for Page in (StartPage, PageOne,PageGraph):
            frame = Page(container, self,Info)
            self.frames[Page] = frame
            frame.grid(row = 0, column = 0, sticky="nsew")
        
        self.show_frame(StartPage)
    
    def show_frame(self,cont):
        """
        Mettre en premier plan la page choisie
        """
        if cont == PageOne:
            self.geometry("1200x800")
        elif cont == PageGraph:
            self.geometry("1200x800")
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller,Info):
        """
        Page introduciton: phrase de Warren Buffet 
        2 buttons pour choisir tester l'aplication ou sortir
        """
        ttk.Frame.__init__(self,parent)        
        self.Info = Info
                       
        label1 = tk.Label(self, text=("Welcome to Algorithmic Trading Platform"),font=LARGE_FONT, relief= tk.RAISED) # , fg = "blue", relief=tk.SUNKEN, tk.RAISED, tk.GROOVE, tk.FLAT, tk.RIDGE
        label2 = tk.Label(self, text=("'On Earnings: Never depend on a single income. \nMake investment to creat a second source'"),font=("Times", "20", "italic"))
        label3 = tk.Label(self, text=("Warren Buffet"),font=("Times", "15", "italic"))

        
        button1 = ttk.Button(self,text="Let's try",command=lambda: controller.show_frame(PageOne))
        button2 = ttk.Button(self,text="Too risky for me",command=quit)
        
        
        label1.grid(column=0,row=0, columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W))
        label2.grid(column=0, row=3,columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W),padx=10, pady=10)
        label3.grid(column=0, row=4, columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W))

        button1.grid(column=1, row=5, sticky=(tk.N,tk.S),padx=10, pady=10)
        button2.grid(column=1, row=6, sticky=(tk.N,tk.S),padx=10, pady=10)
        
        
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(7,weight=1)

class PageOne(tk.Frame):
    def __init__(self, parent, controller,Info):
        """
        Page qui contient les Settings pour le backtest
        """
        tk.Frame.__init__(self,parent)
        self.Info = Info
        
        label1 = tk.Label(self, text=("BackTest Environment"),font=("Verdana", 20), relief= tk.RAISED)
        
        labelText2=tk.StringVar()
        labelText2.set("This page allows you to set the parameters to run the backtest")
        label2=tk.Label(self, textvariable=labelText2,height=4)
        
        label3 = tk.Label(self, text=("Setting the Database"),font=("Verdana", 12), relief= tk.RAISED)
        
        labelText4=tk.StringVar()
        labelText4.set("You have to chose your database: \n  -if it's already build : put the name\n  -if not, chose one name and press generate Database")
        label4=tk.Label(self, textvariable=labelText4,height=4, justify=tk.LEFT)
        
        labelText5=tk.StringVar()
        labelText5.set("Enter the base (format[base.db]): ")
        label5=tk.Label(self, textvariable=labelText5, height=4)

        labelText6=tk.StringVar(None)
        self.basename=tk.Entry(self,textvariable=labelText6,width=10)
        self.basename.focus_set()
        
        button1 = ttk.Button(self,text="Generate base",command=self.generate_base)
        button2 = ttk.Button(self,text="Use old base",command=self.use_old_base)
        
        label7 = tk.Label(self, text=("Setting the Backtest Parameters"),font=("Verdana", 12), relief= tk.RAISED)
        
        def get_ticker(*args):
            idxs = listbox.curselection()
            if len(idxs)==1:
                idx = int(idxs[0])
                (symbol_id,symbol,suffix)=self.Info.DailyPrices.tickers[idx]
                self.Info.tickers = [symbol+suffix]
        
        s = ttk.Scrollbar(self, orient=tk.VERTICAL)
        listbox = tk.Listbox(self,width =10, height = 15 , yscrollcommand = s.set,selectbackground = "green", selectmode ="SINGLE")
        
        listbox.bind('<<ListboxSelect>>', get_ticker)
        
        for ticker in self.Info.DailyPrices.tickers:
            (symbol_id,symbol,suffix) = ticker
            listbox.insert(tk.END, symbol+suffix)
        for i in range(0,len(self.Info.DailyPrices.tickers),2):
            listbox.itemconfigure(i, background='#f0f0ff')
        
        def get_spinbox_parameters():
            self.Info.initial_capital = int(spinbox1.get())
            sd_day = spinbox21.get()
            sd_month = spinbox22.get()
            sd_year = spinbox23.get()
            ed_day = spinbox31.get()
            ed_month = spinbox32.get()
            ed_year = spinbox33.get()
            self.Info.start_date = datetime(int(sd_year),int(sd_month), int(sd_day))
            self.Info.end_date = datetime(int(ed_year),int(ed_month), int(ed_day))
        
        labelText8=tk.StringVar()
        labelText8.set("Enter the initial capital: ")
        label8=tk.Label(self, textvariable=labelText8, height=4)        
        

        spinbox1 = tk.Spinbox(self, from_=1000.0, to=100000.0,width=6)
        
        labelText9=tk.StringVar()
        labelText9.set("Enter the initial date: ")
        label9=tk.Label(self, textvariable=labelText9, height=4)        
        
        spinbox21 = tk.Spinbox(self, from_=1, to=31,width=3)       

        spinbox22 = tk.Spinbox(self, from_=1, to=12,width=3)
        
        spinbox23 = tk.Spinbox(self, from_=2000, to=2015,width=5)
        
        labelText10=tk.StringVar()
        labelText10.set("Enter the final date: ")
        label10=tk.Label(self, textvariable=labelText10, height=4)        
        

        spinbox31 = tk.Spinbox(self, from_=1, to=31,width=3)
        
        spinbox32 = tk.Spinbox(self, from_=1, to=12,width=3)
        
        spinbox33 = tk.Spinbox(self, from_=2000, to=2015,width=5)
        
        get_spinbox_parameters()
               
        button3 = ttk.Button(self,text="Set Parameters",command=get_spinbox_parameters)
        button4 = ttk.Button(self,text="Go to Simulation",command=lambda: controller.show_frame(PageGraph))
        
        label1.grid(column=0,row=0, columnspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
        label2.grid(column=0, row=1,columnspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
        label3.grid(column=0, row=2, columnspan=1, sticky=(tk.N,tk.S,tk.E,tk.W))
        label4.grid(column=0, row=3, rowspan=3,columnspan=1, sticky=tk.W)
        label5.grid(column=0, row=5, columnspan=1, sticky=tk.W)
        self.basename.grid(column=0, row=5, columnspan=1, sticky=tk.W, padx =210)
        button1.grid(column=0, row=6, sticky=(tk.E),padx=100, pady=10)
        button2.grid(column=0, row=6, sticky=(tk.W),padx=100, pady=10)
        
        label7.grid(column=1, row=2, columnspan=1, sticky=(tk.N,tk.S,tk.E,tk.W))
        listbox.grid(column=1, row=3, rowspan=5,sticky=(tk.N,tk.W),pady=10)
        label8.grid(column=1, row=3,sticky=(tk.N,tk.W),padx=100, pady=10)
        spinbox1.grid(column=1, row=3 ,sticky=(tk.N,tk.W), padx=100 ,pady=50 )
        label9.grid(column=1, row=4,sticky=(tk.N,tk.W),padx=100, pady=10)
        spinbox21.grid(column=1, row=4 ,sticky=(tk.N,tk.W), padx=100 ,pady=50 )
        spinbox22.grid(column=1, row=4 ,sticky=(tk.N,tk.W), padx=140 ,pady=50 )
        spinbox23.grid(column=1, row=4 ,sticky=(tk.N,tk.W), padx=180 ,pady=50 )
        label10.grid(column=1, row=5,sticky=(tk.N,tk.W),padx=100, pady=10)
        spinbox31.grid(column=1, row=5 ,sticky=(tk.N,tk.W), padx=100 ,pady=50 )
        spinbox32.grid(column=1, row=5 ,sticky=(tk.N,tk.W), padx=140 ,pady=50 )
        spinbox33.grid(column=1, row=5 ,sticky=(tk.N,tk.W), padx=180 ,pady=50 )

        
        button3.grid(column=1, row=8,columnspan=1,ipadx=5,ipady=5)
        button4.grid(column=0, row=10,columnspan=2,pady=50,ipadx=70, ipady=20)         
        
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(10,weight=1)

    
    
    def use_old_base(self):
        self.Info.base = self.basename.get()
        self.Info.old_database()
    
    def generate_base(self):
        self.Info.base = self.basename.get()
        self.Info.new_database()
        

class PageGraph(tk.Frame):
    def __init__(self, parent, controller,Info):
        """
        Page qui contient l'affichage grpahique des cotations et MAS et MAL
        """
        tk.Frame.__init__(self,parent)
        self.Info = Info
        label1 = tk.Label(self, text=("BackTest Simulation"),font=("Verdana", 20), relief= tk.RAISED)
        label1.pack(side=tk.TOP, fill = tk.BOTH, expand=True)
        label2 = tk.Label(self, text=(""),font=("Verdana", 30), relief= tk.RAISED)
        label2.pack(side=tk.TOP, fill = tk.BOTH, expand=True)
                      
        canvas = FigureCanvasTkAgg(f,self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill = tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2TkAgg(canvas,self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill = tk.BOTH, expand=True)
        
        button1 = ttk.Button(self,text="Back to settings", command=lambda: controller.show_frame(PageOne))
        button1.place(x=30,y=70)
        
        buttonRun = ttk.Button(self,text="Run", command= lambda: self.Info.loadChart("Run"))
        buttonRun.place(x=230,y=70)
        
        buttonPause = ttk.Button(self,text="Pause", command= lambda: self.Info.loadChart("Pause"))
        buttonPause.place(x=430,y=70)
        
        buttonStop = ttk.Button(self,text="Stop", command= lambda: self.Info.loadChart("Stop"))
        buttonStop.place(x=630,y=70)
        
        label11 = tk.Label(self, text="Vitesse: ", height=1)
        label11.place(x=830,y=70)
        label12 = tk.Label(self, text="Vitesse", height=1)
        label12.place(x=900,y=70)

        def getx(*args):
            self.Info.vitesse=Sx.get()
            label12.configure(text=self.Info.vitesse)
        
        Sx = tk.Scale(self, from_=0.01, to=1000, resolution=1,orient = 'horizontal', command=getx)
        Sx.place(x=950,y=70)
        
        
class Information():
    def __init__(self,f):
        self.f = f
        self.a = self.f.add_subplot(111)
        
        self.base = 'test2.db'
        self.tickers = ['AC.PA']
        self.initial_capital = 10000
        self.vitesse = 1
        self.start_date = datetime(2013,5, 2)
        self.end_date = datetime(2013, 6, 30)
        
        self.QueueEvents= queue.Queue()
        self.carnet_ordres = queue.Queue()
        
        self.RunPauseStop = 'Stop'
        
        self.old_database()
        self.parameters()
            
    def new_database(self):
        Exchange = DatabaseExchanges(self.base)
        Exchange.new()
        Exchange.remplissage()

        Symbols = DatabaseSymbols(self.base)
        Symbols.new()
        Symbols.remplissage()

        self.DailyPrices = DatabaseDailyPrices(self.base)
        self.DailyPrices.new()
        self.DailyPrices.obtain_tickers()
        self.DailyPrices.get_prices()
        self.DailyPrices.update_prices()
        
        self.parameters()
   
    def old_database(self):
        self.DailyPrices = DatabaseDailyPrices(self.base)
        self.DailyPrices.obtain_tickers()
        
        self.parameters()
        
    def parameters(self):    
        self.DataManager1 = SQLDataManagerBacktest(self.QueueEvents,self.DailyPrices,self.tickers,self.start_date,self.end_date)
        self.DataManager1.market()
        self.DataStorage1 = DataStorage(self.tickers)
        self.Strategy1 = MovingAverage_1_Strategy(self.DataManager1,self.DataStorage1,self.QueueEvents,5,20)

        self.Portfolio1 = MovAvePortfolio(self.DataStorage1,self.QueueEvents,self.initial_capital,self.carnet_ordres)
        

    def loadChart(self,action_str):
        if self.RunPauseStop=='Pause' and action_str =='Run': 
            self.RunPauseStop = action_str
        elif self.RunPauseStop !='Pause' and action_str =='Run':
            self.parameters()
        elif action_str == 'Stop': self.parameters()
        self.RunPauseStop = action_str
        
       
    def animate(self,i):
        """
        Event-Loop: pour chaque iteration:
            Extraction new data ---> generation Event Data
            Strategy. generate_trade_Signal(event) : processe le DATA et analyse 
                des signaux d'investissement selon les critères fournis. Soit genere un
                event TRADE, soit ne genere rien.
            On passe un deuxième boucle pour executer les ordres
            Actualsation du protfolio (calcul P&L, positions, MtM)
           Si strategy a generé event Trade: portfolio va considere la quantite a traiter
           et va genere l'ordre
           Extraction new data ...
        """
        if self.RunPauseStop == 'Run':
            if self.DataManager1.continue_backtest == True:
                self.DataManager1.next_bar()
                while True:
                    try:
                        event = self.QueueEvents.get(False)
                    except:
                        break
                    else:
                        if event is not None:
                            if event.type == 'DATA':                                
                                self.Strategy1.generate_trade_signal(event)
                                
                                while True:
                                    try:
                                        ordre = self.carnet_ordres.get(False)
                                        print(ordre)
                                    except:
                                        break
                                    else:
                                        self.Portfolio1.treat_OrderEvent(ordre)
                                        
                                self.Portfolio1.update_portfolio_data()
                                    
                            if event.type == 'TRADE':
                                print(event)
                                self.Portfolio1.treat_TradeEvent(event)
        
            try:
                self.a.clear()
                
                x = self.Portfolio1.datastorage.info[self.tickers[-1]]['Date']
                y0 = self.Portfolio1.datastorage.info[self.tickers[-1]]['Close']
                y1 = self.Portfolio1.datastorage.info[self.tickers[-1]]['MAS']
                y2 = self.Portfolio1.datastorage.info[self.tickers[-1]]['MAL']
                
                self.a.clear()
                self.a.plot_date(x,y0,"#00A3E0", label="Close") # "#00A3E0"
                self.a.plot_date(x,y1,"g", label="MA Small") # "#00A3E0"
                self.a.plot_date(x,y2,"r",label = "MA Long") # "#183A54"

                self.a.legend(bbox_to_anchor = (0,1.02,1,0.102),loc=3, ncol =2,borderaxespad = 0)

                title = ( self.tickers[-1] +"\n"+
                        "Last date: "+ str(self.Portfolio1.datastorage.info[self.tickers[-1]]['Date'][-1]) 
                        +" Portfolio Value: "+ str(self.Portfolio1.datastorage.info['Portfolio']['Portfolio_Value'][-1]))
                self.a.set_title(title)
    
            except Exception as e:
                print("Exception: print process:".format(e))

global interval1       
if __name__=="__main__":
    f = Figure()
    Info= Information(f)

    app = GUIBacktest(Info)
    
    interval = Info.vitesse*10
    
    ani = animation.FuncAnimation(Info.f,Info.animate, interval=interval)
    app.mainloop()
    


  


    
 
     
        
        

 
     
        
        
