# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 20:47:02 2020

@author: Shaswat
The program takes about 30 minutes to run and uses the Markowitz efficient frontier model.
"""
"""
Answer output from program = 

Combination with lowest risk is:('MSFT'- 3.91%, 'AMZN' - 23.09%, 'JNJ' - 13.90%, 'VZ' - 49.12%, 'PFE' - 9.98%)
Their weights respectively are: [0.03911324 0.23097232 0.13895623 0.49120624 0.09975197]
Returns generated from this portfolio:  26.84%
Volatility of portfolio:  24.09%
"""

import pandas as pd
import datetime as dt
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from itertools import combinations
#import cvxopt as opt  
#from cvxopt import blas, solvers

delta = 365 #lookback period
start = dt.datetime.today() - dt.timedelta(delta)
end = dt.datetime.today()
tickers = ["MSFT", "AAPL", "AMZN", "GOOG","GOOGL", "FB", "BRK-B", "JNJ", "V", "PG", "JPM", "UNH", "MA", "INTC", "VZ", "HD", "T", "PFE", "MRK", "PEP"]

comb = combinations(tickers, 5)
combinations_list = list(comb)

ohlc = {}
sec_ret = {}
sec_vol = {}
returns_mod = pd.DataFrame()

for ticker in tickers: #downloading market data for the 20 stocks
    ohlc[ticker] = yf.download(ticker, start, end)
    ohlc[ticker]["Daily_Ret"] = ohlc[ticker]["Adj Close"].pct_change()
    returns_mod[ticker] = ohlc[ticker]["Daily_Ret"]
  
def CAGR(DF): #CAGR is used as my measure of return instead of log returns
    df = DF.copy()
    
    df["cum_ret"] = 1+(df["Daily_Ret"]).cumsum()
    n = len(df)/252
    CAGR = (df["cum_ret"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF): #Annualized stdeviation is the measure of volatility for each stock
    df = DF.copy()
    vola = df["Daily_Ret"].std() * np.sqrt(252)
    return vola

for ticker in tickers: #Extracting the CAGR values of all the stocks
    sec_ret[ticker] = CAGR(ohlc[ticker])
    sec_vol[ticker] = volatility(ohlc[ticker])


returns = pd.DataFrame(sec_ret.items(), columns=['Ticker', 'CAGR'])
risk = pd.DataFrame(sec_vol.items(), columns=['Ticker', 'Volatility'])
returns.set_index("Ticker", inplace = True) 
risk.set_index("Ticker", inplace = True)

#comb=[]

multiply_ret = returns["CAGR"] #Used to make it possible to multiplt CAGR with weight
multiply_vol = risk["Volatility"] 



num_iterations = 200 #Number of iterations per portfolio for Markowitz Optimization

def five(portfolio): #Function to find the weights for portfolio with minimum risk for given set of 5 stocks
    
    pf_returns = []
    pf_risk = []
    minrisk=0
    minreturn=0
    returns_mod1 = pd.DataFrame()
    multiply_ret1 = list(multiply_ret[ticker] for ticker in portfolio)
    
    for ticker in portfolio:
        returns_mod1[ticker] = ohlc[ticker]["Daily_Ret"]
    for i in range(num_iterations): #Markowitz portfolio simulation with random weights
       
       weights = np.random.random(5)
       weights /= np.sum(weights)
       pf_returns.append(np.sum(weights*multiply_ret1))
       pf_risk.append(np.sqrt(np.dot(weights.T,np.dot(returns_mod1.cov()*252,weights))))
       if (i == 0):
           minw = weights
           minrisk = pf_risk[i]
           minreturn = pf_returns[i]
       elif(pf_risk[i]<pf_risk[i-1]):
           minw = weights
           minrisk = pf_risk[i]
           minreturn = pf_returns[i]
           
    return minw,minrisk,minreturn


i = 0   

weights = {} #contains all weights for the minimum risk portfolio
risks = {} #contains all the volatility of the minimum risk portfolios
gains = {} #contains all the CAGR values for the minimum risk portfolios
combis = {} 
    
i=0   
for portfolios in combinations_list: #iterating through all possible combinations of 5 stocks
    weights[i], risks[i], gains[i] = five(portfolios)
    i = i + 1
    if (i == 1):
        print("Iterations through various portfolio combinations started, please wait(20 seconds per 100 portfolios)...")
    if (i%100 == 0):
        print ("Number of portfolios complete = ", i)
        
        
answer = min(risks.values()) #Least risk of the low risk portfolios
location = None
for a,b in risks.items(): #finds the location of the least risk portfolio
    if(b==answer):
        location = a
        break

    
print("Combination with lowest risk is: ", combinations_list[location])
print("Their weights respectively are: ", weights[location])
print("CAGR generated from this portfolio: ", round(gains[location]*100,2), "%")  
print("Volatility of portfolio: ", round(risks[location]*100,2), "%")  

#Efficient frontier bullet of the least risky portfolio of stocks
pf_returns = []
pf_risk = []
returns_mod1 = pd.DataFrame()
multiply_ret1 = list(multiply_ret[ticker] for ticker in list(combinations_list[location]) )
for ticker in list(combinations_list[location]):
    returns_mod1[ticker] = ohlc[ticker]["Daily_Ret"]
    
for i in range(1000):
   
   weights = np.random.random(5)
   weights /= np.sum(weights)
   pf_returns.append(np.sum(weights*multiply_ret1))
   pf_risk.append(np.sqrt(np.dot(weights.T,np.dot(returns_mod1.cov()*252,weights))))
  

portfolios = pd.DataFrame({'Return': pf_returns, 'Volatility': pf_risk})
portfolios.plot(x='Volatility', y='Return', kind='scatter', figsize=(10, 6));
plt.xlabel('Expected Volatility')
plt.ylabel('Expected Return')
plt.title("Efficient Frontier Bullet")