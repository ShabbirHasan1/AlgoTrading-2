# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 01:01:01 2020

@author: Shaswat
"""

import datetime as dt
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
ohlcv=pd.DataFrame()
stock = "TCS.NS"
start = dt.datetime.today()-dt.timedelta(1825)
end = dt.datetime.today()
ohlcv = yf.download(stock,start,end)
df=ohlcv.copy()
def RSI(DF,n):
    df=DF.copy()
    df["Delta"] = df["Adj Close"]-df["Adj Close"].shift(1)
    df["Gain"] = np.where(df["Delta"]>=0, df["Delta"],0)
    df["Loss"] = np.where(df["Delta"]<=0, abs(df["Delta"]),0)
    avggain=[]
    avgloss=[]
    gain = df["Gain"].tolist()
    loss = df["Loss"].tolist()
    for i in range(len(df)):
        if i<n:
            avggain.append(np.NaN)
            avgloss.append(np.NaN)
        elif i==n:
            avggain.append(df["gain"].rolling(n).mean().tolist()[n])
            avgloss.append(df["loss"].rolling(n).mean().tolist()[n])
        elif i>n:
            avggain.append(((n-1)*avggain[i-1] + gain[i])/n)
            avgloss.append(((n-1)*avggain[i-1] + loss[i])/n)
    
    df["avggain"] = np.array(avggain)
    df["avgloss"] = np.array(avgloss)
    df["RS"] = df["avggain"]/df["avgloss"]
    df["RSI"] = 100 - (100/(1+df["RS"]))
    return df["RSI"]



         
            
            
    