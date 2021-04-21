# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 05:14:16 2020

@author: Shaswat
"""

import pandas as pd
import datetime as dt
import numpy as np
import yfinance as yf
import copy
import matplotlib.pyplot as plt


def CAGR(DF):
    df = DF.copy()
    
    df["cum_ret"] = (1+df["mon_ret"]).cumprod()
    n = len(df)/12
    CAGR = (df["cum_ret"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    df = DF.copy()
    
    vola = df["mon_ret"].std() * np.sqrt(12)
    return vola


def sharpe(DF,rf):
    df = DF.copy()
    ratio = (CAGR(df) - rf)/volatility(df)
    return ratio

def maxdraw(DF):
    df = DF.copy()
    
    df["cum_ret"] = (1+df["mon_ret"]).cumprod()
    df["cum_roll_max"] = df["cum_ret"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_ret"]
    df["drawdownpct"] = df["drawdown"]/df["cum_roll_max"]
    maxdd = df["drawdownpct"].max()
    return maxdd

tickers = ["ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS",	
           "BAJAJ-AUTO.NS",	"BAJFINANCE.NS", "DABUR.NS", "BPCL.NS",	"BIOCON.NS",
           "BHARTIARTL.NS", "INFRATEL.NS", "BRITANNIA.NS", "CIPLA.NS",	
           "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "GAIL.NS",	"INDIGO.NS", 
           "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HEROMOTOCO.NS",	
           "HINDALCO.NS", "MARICO.NS", "HDFC.NS", "ICICIBANK.NS",	
           "ITC.NS", "IOC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS",	
           "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS",	
           "IRCTC.NS", "ONGC.NS", "POWERGRID.NS", "PVR.NS", "RELIANCE.NS",	
           "SBICARD.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS",	
           "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "UPL.NS",
           "ULTRACEMCO.NS", "VEDL.NS", "WIPRO.NS", "ZEEL.NS"]

ohlc_mon = {} # directory with ohlc value for each stock            
start = dt.datetime.today()-dt.timedelta(3650)
end = dt.datetime.today()

# looping over tickers and creating a dataframe with close prices
for ticker in tickers:
    ohlc_mon[ticker] = yf.download(ticker,start,end,interval='1mo')
    ohlc_mon[ticker].dropna(inplace=True,how="all")

tickers = ohlc_mon.keys()


ohlc_dict = copy.deepcopy(ohlc_mon)
return_df = pd.DataFrame()
for ticker in tickers:
    print("calculating monthly return for ",ticker)
    ohlc_dict[ticker]["mon_ret"] = ohlc_dict[ticker]["Adj Close"].pct_change()
    return_df[ticker] = ohlc_dict[ticker]["mon_ret"]
    


def pfolio(DF,m,x):
    number = 0
    df = DF.copy()
    portfolio = []
    monthly_ret = [0]
    for i in range(1,len(df)):
        if(len(portfolio)>0):
            monthly_ret.append(df[portfolio].iloc[i,:].mean())
            bad_stocks = df[portfolio].iloc[i,:].sort_values(ascending=True)[:x].index.values.tolist()
            portfolio = [t for t in portfolio if t not in bad_stocks]
        fill = m - len(portfolio)
        new_picks = df.iloc[i,:].sort_values(ascending=False)[:fill].index.values.tolist()
        portfolio = portfolio + new_picks
        number = number + 1
        
       # print(number, ": ", portfolio)
    monthly_retdf = pd.DataFrame(np.array(monthly_ret),columns=["mon_ret"])
    return monthly_retdf


#calculating overall strategy's KPIs
print("\
      Portfolio: CAGR = ", CAGR(pfolio(return_df,6,3)))
print("Sharpe = ", sharpe(pfolio(return_df,6,3),0.063))
print("MaxDrawdown = ", maxdraw(pfolio(return_df,6,3))) 


nse = yf.download("^NSEI",dt.date.today()-dt.timedelta(3650),dt.date.today(),interval='1mo')
nse["mon_ret"] = nse["Adj Close"].pct_change()   
print("NSE: CAGR = ", CAGR(nse))
print("Sharpe = ", sharpe(nse,0.063))
print("MaxDD = ", maxdraw(nse))

fig, ax = plt.subplots()
plt.plot((1+pfolio(return_df,6,3)).cumprod())
plt.plot((1+nse["mon_ret"][2:].reset_index(drop=True)).cumprod())
plt.title("Index Return vs Strategy Return")
plt.ylabel("cumulative return")
plt.xlabel("months")
ax.legend(["Strategy Return","Index Return"])

    