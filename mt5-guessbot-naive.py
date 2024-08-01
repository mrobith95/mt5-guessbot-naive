from datetime import datetime
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import sys
import csv

## rounding function for rounding
def repair_number(number, poin, digit, tipe):
    aja = 0
    if tipe == 'floor':
        aja = np.round(np.floor(number/poin)*poin, decimals=digit)
    if tipe == 'ceil':
        aja = np.round(np.ceil(number/poin)*poin, decimals=digit)
    if tipe == 'round':
        aja = np.round(number, decimals=digit)
    
    return aja

## rounding + display for error
def repair_error(number, poin):
    return str(int(np.round(number/poin)))+" point(s)"

## reading files
namafile = 'mt5-guessbot-naive.xlsx'
tabel_acc = pd.read_excel(namafile,'Login and Settings')
tabel_pair = pd.read_excel(namafile,'Pair Table')
 
# connect to MetaTrader 5
account=tabel_acc['Acc. Number'][0]
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    mt5.shutdown()
    quit()
 
### request connection status and parameters
##print(mt5.terminal_info())
##print(" ")
### get data on MetaTrader 5 version
##print(mt5.version())
##print(" ")

# now connect to trading account specifying the password and server
authorized=mt5.login(int(account),password=tabel_acc['Password'][0], server=tabel_acc['Server'][0])
if authorized:
##    ## don't display account info data
##    # display trading account data 'as is'
##    print(mt5.account_info())
##    # display trading account data in the form of a list
##    print("Show account_info()._asdict():")
##    account_info_dict = mt5.account_info()._asdict()
##    for prop in account_info_dict:
##        print("  {}={}".format(prop, account_info_dict[prop]))
    print("login successfull!")
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))

## determine how many symbol/timeframe combo
n_pair = len(tabel_pair)

# determine sets
simbolset = tabel_pair['simbol'] ## symbol name
simbolset = simbolset.to_numpy() ## why to numpy? not sure
poinset = [] ## point for each symbol
digitset = [] ## digit for each symbol
waktuframeset = [] ## timeframe for timer
waktuframetemp = tabel_pair['timeframe']
for k in range(0,n_pair):
    infosimbol = mt5.symbol_info(simbolset[k])
    poinset.append(np.float_power(10,-1*infosimbol.digits)) ## adding point
    digitset.append(infosimbol.digits) ## adding digit
    if waktuframetemp[k] == 'M1': ## adding timeframe
        waktuframeset.append(mt5.TIMEFRAME_M1)  
    elif waktuframetemp[k] == 'M5':
        waktuframeset.append(mt5.TIMEFRAME_M5)
    elif waktuframetemp[k] == 'M15':
        waktuframeset.append(mt5.TIMEFRAME_M15)
    elif waktuframetemp[k] == 'M30':
        waktuframeset.append(mt5.TIMEFRAME_M30)
    elif waktuframetemp[k] == 'H1':
        waktuframeset.append(mt5.TIMEFRAME_H1)
    elif waktuframetemp[k] == 'H4':
        waktuframeset.append(mt5.TIMEFRAME_H4)
    elif waktuframetemp[k] == 'D1':
        waktuframeset.append(mt5.TIMEFRAME_D1)
    elif waktuframetemp[k] == 'W1':
        waktuframeset.append(mt5.TIMEFRAME_W1)
    elif waktuframetemp[k] == 'MN':
        waktuframeset.append(mt5.TIMEFRAME_MN)
    else:
        print('Timeframe only receive standard MT5 timeframe. Timeframe settings become MN') 
        waktuframeset.append(mt5.TIMEFRAME_MN)

##ambildata = 1000 ## number of candles to consider. Might useful later

saatini = [] ## time of latest candle
namanama = [] ## name of records/models
datas = []
## memory
pred = np.zeros((n_pair))
lowerl = np.zeros((n_pair))
upperl = np.zeros((n_pair))
galat = np.zeros((n_pair))

## time info
now = datetime.now()
dt_string = now.strftime("%Y%m%d%H%M%S")

for k in range(0,n_pair):
    simbol = simbolset[k]
    waktuframe = waktuframeset[k]
    infosimbol = mt5.symbol_info(simbol)
    poin = np.float_power(10,-1*infosimbol.digits)
    timer_rates = mt5.copy_rates_from_pos(simbol, waktuframe, 1, 1) ## get recent finished candle
    timer_frame = pd.DataFrame(timer_rates)
    timer_frame['time']=pd.to_datetime(timer_frame['time'], unit='s')
    saatini.append(timer_frame["time"][0]) ## save it's time
    namanama.append(simbol+'_'+str(waktuframe)+'_record_'+dt_string+'.csv') ## record file name
    datas.append([]) ## write csv of record
    datas[k].append(["Timestamp", "prediction", "close"])
    with open(namanama[k], 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "prediction", "close"])

    ## model data added later

print("Ready to Predict!") ## no hello :(
while True:
    for k in range(0,n_pair):
        ## prepare data
        simbol = simbolset[k]
        infosimbol = mt5.symbol_info(simbol)
        poin = np.float_power(10,-1*infosimbol.digits)
        waktuframe = waktuframeset[k]
        
        ## get candles, for timer
        timer_rates  = mt5.copy_rates_from_pos(simbol, waktuframe, 1, 1)
        timer_frame = pd.DataFrame(timer_rates)
        timer_frame['time']=pd.to_datetime(timer_frame['time'], unit='s')
        
        ## check if new candle just finished
        if timer_frame.iloc[-1]["time"] != saatini[k]:
            saatini[k] = timer_frame.iloc[-1]["time"] # renew timer
            print("================================")
            print("Time       :", saatini[k])

            ## Get data, not including unfinished candle
            eurgbp_rates = mt5.copy_rates_from_pos(simbol, waktuframe, 1, 31)
            ## the above rates give "untabulated" value, unsuitable to read. Use pandas for this purpose.

            # create DataFrame out of the obtained data
            rates_frame = pd.DataFrame(eurgbp_rates)
            # convert time in seconds into the datetime format
            rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
             
            # remove real_volume since always zeros for forex(?)
            rates_frame.drop(columns=['real_volume'], inplace=True)
        
            rates_frame.dropna(inplace=True) # dropna

            # make numpy array for storing because why not
            open_np   = rates_frame['open'].to_numpy()
            high_np   = rates_frame['high'].to_numpy()
            low_np    = rates_frame['low'].to_numpy()
            close_np  = rates_frame['close'].to_numpy()
            adadata = open_np.shape[0]

            print("Symbol     :", simbol)
            ## if a prediction was performed, do comparison with actual and log it
            if pred[k] > 0:
                galat[k] = np.abs(pred[k] - close_np[30])
                datas[k].append([saatini[k], pred[k], close_np[30]])
                t1 = repair_number(pred[k], poinset[k], digitset[k], "round")
                t2 = repair_number(close_np[30], poinset[k], digitset[k], "round")
                with open(namanama[k], 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([saatini[k], t1, t2])
                    
                print("Error      : "+repair_error(galat[k], poinset[k]))

            ## analyze distrbution. Model is Random Walk
            diff      = close_np[1:31] - close_np[0:30]
            pred[k]   = close_np[30]
            lowerl[k] = np.percentile(diff, 2.5) ## 2.5% percentile
            upperl[k] = np.percentile(diff, 97.5) ## 97.5% percentile
            ## thus 95% confidence

            ## printing stuff
            print("Prediciton :", repair_number(pred[k], poinset[k], digitset[k], 'round'))
            print("Lower Limit:", repair_number(pred[k]+lowerl[k], poinset[k], digitset[k], 'ceil'))
            print("Upper Limit:", repair_number(pred[k]+upperl[k], poinset[k], digitset[k], 'floor'))

