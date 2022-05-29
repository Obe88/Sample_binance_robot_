import os
import time
from datetime import datetime
import input_config
from binance_f import RequestClient
from binance_f.model.constant import *

server_url=input_config.server_url
APIK=input_config.APIK
APIS=input_config.APIS
GLOBAL_SYMBOL=input_config.GLOBAL_SYMBOL


candles_of_data=90
limit=candles_of_data+1


dir_data = os.path.dirname(__file__)

time_right_now_millisec_utc=int(round(datetime.now().timestamp()*1000))

DAYS_in_the_past=int(candles_of_data*24*3600*1000)

# FOURHOURS_in_the_past=int(candles_of_data*4*3600*1000)

HOURS_in_the_past=int(candles_of_data*3600*1000)

FIFTEEN_min_in_the_past=int(candles_of_data*15*60*1000)

minutes_in_the_past=int(candles_of_data*60*1000)

client = RequestClient(api_key=APIK, secret_key=APIS, url=server_url)#Client(None, None)server_url="https://fapi.binance.com")#

print(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
print("WAITING "+str(60-(time.time()%60)+1)+ " SECONDS")
time.sleep(60-(time.time()%60)+1)

print("STARTING HISTORICAL CANDLES RETRIEVAL")

def object_processor(object):
    test=False
    
    daily_data=[]
    liste=object.__dict__
    
    for keys, values in liste.items():
        if test==True:#IF TRUE GIVE ME THE NAMES OF THE VALUES IE KEYS
            daily_data.append(keys)
        if test==False:#IF FALSE CONTINUE APPENDING VALUES
            if type(values)==str:
                values=float(values)
            daily_data.append(values)

    return daily_data
    
def candle_appender_fixer(result,interval_list):
    
    for x in result:
        one_bar=list(object_processor(x))###HOLY FKING SHIT THIS LITTLE FUCKER LIST FUNCTION IS EVERYTHING
        interval_list.append(one_bar)
    
    for y in interval_list:
        if type(y[0])is not str:
            y[0]=y[0]/1000
    interval_list.remove(interval_list[-1])

def candlesticks_list_extractor(params,interval_list):
    try:        
        result=client.get_candlestick_data(*params)
        candle_appender_fixer(result,interval_list)
    except Exception as e:
        print(e)
        
    # pprint.pprint(interval_list)# THIS IS JUST FOR TESTING/VERIFICATION

# candlestick_data=[]#UNUSED THIS IS JUST FOR TESTING

extparams=GLOBAL_SYMBOL, CandlestickInterval.DAY1, time_right_now_millisec_utc-DAYS_in_the_past, None, int(limit)
D_candlesticks=[]
interval_list=D_candlesticks
candlesticks_list_extractor(extparams,interval_list)

# extparams=GLOBAL_SYMBOL, CandlestickInterval.HOUR4, time_right_now_millisec_utc-FOURHOURS_in_the_past, None, int(limit)
# Four_H_candlesticks=[]
# interval_list=Four_H_candlesticks
# candlesticks_list_extractor(extparams,interval_list)

extparams=GLOBAL_SYMBOL, CandlestickInterval.HOUR1, time_right_now_millisec_utc-2*HOURS_in_the_past, None, int(2*limit)
One_H_candlesticks=[]
interval_list=One_H_candlesticks
candlesticks_list_extractor(extparams,interval_list)

extparams=GLOBAL_SYMBOL, CandlestickInterval.MIN15, time_right_now_millisec_utc-FIFTEEN_min_in_the_past, None, int(limit)
MIN_15_candlesticks=[]
interval_list=MIN_15_candlesticks
candlesticks_list_extractor(extparams,interval_list)

extparams=GLOBAL_SYMBOL, CandlestickInterval.MIN1, time_right_now_millisec_utc-minutes_in_the_past, None, int(limit)
One_Minute_candlesticks=[]
interval_list=One_Minute_candlesticks
candlesticks_list_extractor(extparams,interval_list)

print("FINISHED SAVING HISTORICAL CANDLES")

#[0]   'openTime',
#[1]   'open',
#[2]   'high',
#[3]   'low',
#[4]   'close',
#[5]   'volume',
if len(D_candlesticks)>0:

    print("LAST CANDLE TIMESTAMP: ", datetime.fromtimestamp(D_candlesticks[-1][0]).strftime("%A, %B %d, %Y %H:%M:%S")) 
    print("TIME NOW TIMESTAMP: ", datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")) 

    print("LAST CANDLE: ", D_candlesticks[-1])
else:
    print("CANDLE EXTRACTION FAILED!")
