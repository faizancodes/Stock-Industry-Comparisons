import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import sys
import tweepy
import time
import os


symbols = []
stockCounter = 0
c = 0


def getSymbols(inURL):
    
    global symbols
    global stockCounter
    global c

    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    symbs = soup.find_all('a', {'class' : 'screener-link-primary'})

    for x in range(len(symbs)):
        if '&amp;b=1' in str(symbs[x]):
            symbols.append(str(symbs[x])[str(symbs[x]).find('&amp;b=1') + 10 : str(symbs[x]).find('/a') - 1])
            stockCounter = stockCounter + 1

        if stockCounter % 20 == 0:
            c = c + 20
            getSymbols('https://finviz.com/screener.ashx?v=111&f=idx_sp500' + '&r=' + str(c))
        
        if stockCounter >= 800:
            break


def convertString(stng):

    output = ''

    for x in range(len(stng)):
        if stng[x] == '.' or stng[x].isdigit():
            output += stng[x]

    try:
        return float(output)
    except: 
        return "Error"


def bubbleSort(subList): 
    
    l = len(subList) 

    for i in range(0, l): 
        
        for j in range(0, l-i-1): 
            
            if (subList[j][3] < subList[j + 1][3]): 
                tempo = subList[j] 
                subList[j]= subList[j + 1] 
                subList[j + 1] = tempo 

    return subList 


def bubbleSort2(subList): 
    
    l = len(subList) 

    for i in range(0, l): 
        
        for j in range(0, l-i-1): 
            
            if (subList[j][9] < subList[j + 1][9]): 
                tempo = subList[j] 
                subList[j]= subList[j + 1] 
                subList[j + 1] = tempo 

    return subList 



def industryComparisons(s):
    
    getSymbols('https://finviz.com/screener.ashx?v=111&f=idx_sp500')
    
    global symbols

    if s == 'net margin':
        margins = []

        for x in range(len(symbols)):
            page = requests.get('https://csimarket.com/stocks/Profitability.php?code=' + symbols[x])
            soup = str(BeautifulSoup(page.text, 'html.parser'))
            rawNetMargin = soup[soup.find('"period": "Net Margin"') + 25 : soup.find('"period": "Net Margin"') + 100].strip()
            netMargin = rawNetMargin[rawNetMargin.find('visits') + 9 : rawNetMargin.find(',') - 1].strip()
            n = rawNetMargin[rawNetMargin.find(',') + 1 : ]
            industryNetMargin = n[n.find('visits1') + 10 : n.find(',')].strip()

            if len(netMargin) < 10 and len(industryNetMargin) < 10 and float(netMargin) > float(industryNetMargin):
                margins.append([symbols[x], netMargin, industryNetMargin, float(netMargin) - float(industryNetMargin)])
            
        bubbleSort(margins)

        for x in range(len(margins)):
            print(margins[x][0])
            print('Net Margin:', str(margins[x][1]) + '%')
            print('Industry Net Margin:', str(margins[x][2]) + '%')
            print()


    if s == 'roe':
        roes = []

        for x in range(len(symbols)):
            page = requests.get('https://csimarket.com/stocks/' + symbols[x] + '-Management-Effectiveness-Comparisons.html')
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawRoe = soup[soup.find('"period": "ROE"') + 25 : soup.find('"period": "ROE"') + 100]
            roe = rawRoe[rawRoe.find(':') + 2 : rawRoe.find(',') - 1]
            r = rawRoe[rawRoe.find(',') + 1 : ]
            industryROE = r[r.find(':') + 2 : r.find(',') - 1]

            if len(roe) < 10 and len(industryROE) < 10 and float(roe) > float(industryROE):
                roes.append([symbols[x], float(roe), float(industryROE), float(roe) - float(industryROE)])

        bubbleSort(roes)
        
        for x in range(len(roes)):
            print(roes[x][0])
            print('ROE:', str(roes[x][1]) + '%')
            print('Industry ROE:', str(roes[x][2]) + '%')
            print()


    if s == 'pe':
        
        pes = []

        for x in range(len(symbols)):
            page = requests.get('https://csimarket.com/stocks/' + symbols[x] + '-Valuation-Comparisons.html')
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawPE = soup[soup.find('href="/Industry/industry_valuation_ttm.php?pe&amp;sp5">S&amp;P 500<') + 300 : soup.find('href="/Industry/industry_valuation_ttm.php?pe&amp;sp5">S&amp;P 500<') + 700]
            
            pe = convertString(rawPE[rawPE.find('"gorub s ddd">') : rawPE.find('"gorub s ddd">') + 70])
            indPE = convertString(rawPE[rawPE.find('<td class="gorub ddd">') : rawPE.find('<td class="gorub ddd">') + 70])

            if pe != "Error" and indPE != "Error" and pe < indPE:
                pes.append([symbols[x], pe, indPE, indPE - pe])

        bubbleSort(pes)

        for x in range(len(pes)):
            print(pes[x][0])
            print('PE:', pes[x][1])
            print('Industry PE:', pes[x][2])
            print()


    if s == 'growth':

        growth = []

        for x in range(len(symbols)):
            
            page = requests.get('https://csimarket.com/stocks/growthrates.php?code=' + symbols[x])
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawRevGrowth = soup[soup.find('"period": "Revenue<br>Growth Y/Y TTM",') : soup.find('"period": "Revenue<br>Growth Y/Y TTM",') + 255]
            revGrowth = convertString(rawRevGrowth[rawRevGrowth.find('"visits":') : rawRevGrowth.find('"visits":') + 23])
            indRevGrowth = convertString(rawRevGrowth[rawRevGrowth.find('"visits2":') + 9 : rawRevGrowth.find('"visits2":') + 20])

            if revGrowth != "Error" and indRevGrowth != "Error" and revGrowth > indRevGrowth:
                growth.append([symbols[x], revGrowth, indRevGrowth, revGrowth - indRevGrowth])


        bubbleSort(growth)

        for x in range(len(growth)):
            print(growth[x][0])
            print('Revenue Growth:', str(growth[x][1]) + '%')
            print('Industry Revenue Growth:', str(growth[x][2]) + '%')
            print()


    if s == 'all':

        margins = []
        roes = []
        pes = []
        allStats = []
        growth = []

        for x in range(len(symbols)):
            
            page = requests.get('https://csimarket.com/stocks/Profitability.php?code=' + symbols[x])
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawNetMargin = soup[soup.find('"period": "Net Margin"') + 25 : soup.find('"period": "Net Margin"') + 100].strip()
            netMargin = rawNetMargin[rawNetMargin.find('visits') + 9 : rawNetMargin.find(',') - 1].strip()
            n = rawNetMargin[rawNetMargin.find(',') + 1 : ]
            industryNetMargin = n[n.find('visits1') + 10 : n.find(',')].strip()


            page = requests.get('https://csimarket.com/stocks/' + symbols[x] + '-Management-Effectiveness-Comparisons.html')
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawRoe = soup[soup.find('"period": "ROE"') + 25 : soup.find('"period": "ROE"') + 100]
            roe = rawRoe[rawRoe.find(':') + 2 : rawRoe.find(',') - 1]
            r = rawRoe[rawRoe.find(',') + 1 : ]
            industryROE = r[r.find(':') + 2 : r.find(',') - 1]

            
            page = requests.get('https://csimarket.com/stocks/' + symbols[x] + '-Valuation-Comparisons.html')
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawPE = soup[soup.find('href="/Industry/industry_valuation_ttm.php?pe&amp;sp5">S&amp;P 500<') + 300 : soup.find('href="/Industry/industry_valuation_ttm.php?pe&amp;sp5">S&amp;P 500<') + 700]
            
            pe = convertString(rawPE[rawPE.find('"gorub s ddd">') : rawPE.find('"gorub s ddd">') + 70])
            indPE = convertString(rawPE[rawPE.find('<td class="gorub ddd">') : rawPE.find('<td class="gorub ddd">') + 70])


            page = requests.get('https://csimarket.com/stocks/growthrates.php?code=' + symbols[x])
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawRevGrowth = soup[soup.find('"period": "Revenue<br>Growth Y/Y TTM",') : soup.find('"period": "Revenue<br>Growth Y/Y TTM",') + 255]
            revGrowth = convertString(rawRevGrowth[rawRevGrowth.find('"visits":') : rawRevGrowth.find('"visits":') + 23])
            indRevGrowth = convertString(rawRevGrowth[rawRevGrowth.find('"visits2":') + 9 : rawRevGrowth.find('"visits2":') + 20])


            if len(roe) < 10 and len(industryROE) < 10 and float(roe) > float(industryROE) and pe != "Error" and indPE != "Error" and pe < indPE and len(netMargin) < 10 and len(industryNetMargin) < 10 and float(netMargin) > float(industryNetMargin) and revGrowth != "Error" and indRevGrowth != "Error" and revGrowth > indRevGrowth:
                allStats.append([symbols[x], pe, indPE, roe, industryROE, netMargin, industryNetMargin, revGrowth, indRevGrowth, ((float(indPE) - float(pe)) + (float(roe) - float(industryROE)) + (float(netMargin) - float(industryNetMargin)) + (revGrowth - indRevGrowth))])


            print(symbols[x])


        bubbleSort2(allStats)

        for x in range(len(allStats)):
            print(allStats[x][0])
            print('PE:', allStats[x][1])
            print('Industry PE:', allStats[x][2])
            print()
            print('ROE:', str(allStats[x][3]) + '%')
            print('Industry ROE:', str(allStats[x][4]) + '%')
            print()
            print('Net Margin:', str(allStats[x][5]) + '%')
            print('Industry Net Margin:', str(allStats[x][6]) + '%')
            print()
            print('Revenue Growth:', str(allStats[x][7]) + '%')
            print('Industry Revenue Growth', str(allStats[x][8]) + '%')
            print()
            print('Difference Score', allStats[x][9])
            print()
        
        
industryComparisons('all')