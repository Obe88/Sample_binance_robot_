import websocket, json, numpy, tulipy 
import csv
import input_config
import account_info
import get_data
import threading 
import time
from datetime import datetime



SOCKET = input_config.SOCKET

RSI_PERIOD = 7
EMA1_PERIOD = 10
EMA2_PERIOD = 27
STOCH_PERIOD = 7
SLOW_K=3
SLOW_D=3
ATR_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
GLOBAL_SYMBOL = input_config.GLOBAL_SYMBOL

# dataopen, datahigh, datalow, dataclose, datatime =([]for i in range(5))
class initial_registry(object):
    def __init__(self, *args):
        self.is_secure_profit_order_on = False
        self.position_now_qtty=0.0
        self.is_safety_hard_stop_on = False
        
i_registry=initial_registry()



# rsi, ema1, ema2, slowk, slowd =([]for i in range(5))

# prices_low_spikes=[]
# rsis_low_spikes=[]
# prices_high_spikes=[]
# rsis_high_spikes=[]

order_history=[]
order_SL_history=[]
order_TP_history=[]
Pos_Sizing_Reg=[]
# Barrel=[]


aa=0
bb=0
cc=0
dd=0

# PARAMETERS TO CONTROL THE BOT WITHOUT SCROLLING DOWN TOO MUCH
class   params: 

        Manual_filter_override=False
        NewBar=0
        lenbarrel=None
        rsiperiod= 7
        atrperiod= 14
        atr_stop_factor= 20 #divide by 10 ie: 12/10 = 1.2 times the ATR = 120% of the ATR --- 12 is the best for the daily
        Minimal_percentage_change= 0.25 #divide by 10 ie: 11/10 = 1.1% --- 10-11 are the best for the daily
        
        # PARAMETERS TO CONTROL POSITION SIZING AND MONEY MANAGEMENT
        percentage_to_risk=10
        # GRANULARITY IS INSTRUMENTAL TO CONTROL SIZE OF POSITION AND AVOID LIQUIDATION
        granularity=0.00002#0.00001
        # POSITION SIZE LIMITS
        position_upper_limit=0.05
        position_lower_limit=0.001

        hard_stop_price=37000.00#32100.00#38700.00

CSV_ON=False
logING_ON=True

#CSV SAVE<<<<--------------------------------------------------
if CSV_ON:
    dir1 = get_data.dir_data
    filename1 = (dir1+'/Binance_Bot_Registry.csv')
    print('>>>registry 1 path: '+filename1)
    Registry = open(filename1, 'w', newline='')
    TradeTestResults = csv.writer(Registry, delimiter=',')

    dir2 = get_data.dir_data
    filename2 = (dir2+'/Binance_Bot_TRADE_ONLY_Registry.csv')
    print('>>>registry 2 path: '+filename2)
    OrdersRegistry = open(filename2, 'w', newline='')
    OrdersResults = csv.writer(OrdersRegistry, delimiter=',')

# LOGGING FUNCTION TO SAVE ALGORITHM TRADE MECHANICS 
def log(txt, dolog=(logING_ON)):
        ''' Logging function for this strategy'''
        if dolog:
            
            print(str(txt))
            if CSV_ON:
                #CSV SAVE<<<<--------------------------------------------------
                TradeTestResults.writerow([(txt)])
                Registry.flush()

# LOGGING FUNCTION TO SAVE FUNCTION EXECUTION
def log2(txt, dolog=False):
        ''' Logging function for this strategy'''
        if dolog:
            
            #print(txt)
            if CSV_ON:
                #CSV SAVE<<<<--------------------------------------------------
                OrdersResults.writerow([(txt)])
                OrdersRegistry.flush()

# LOGGING FUNCTION TO SAVE ACTUAL TRADE MOVEMENTS
def log3(txt, dolog=(logING_ON)):
        ''' Logging function for this strategy'''
        if dolog:
            
            #print(txt)
            if CSV_ON:
                #CSV SAVE<<<<--------------------------------------------------
                OrdersResults.writerow([(txt)])
                OrdersRegistry.flush()

############################################################################

class Indicators_calculations(object):
#calculations with indicators
    def atr(x):
        np_highs=numpy.array(x.high)
        np_lows=numpy.array(x.low)
        np_closes = numpy.array(x.close)
        atr = tulipy.atr(high=np_highs,low=np_lows,close=np_closes,period=ATR_PERIOD)
        return atr
    def rsi(x):
        np_closes = numpy.array(x.close)
        rsi = tulipy.rsi(np_closes, RSI_PERIOD)
        return rsi
    def stochastic(x):
        np_highs=numpy.array(x.high)
        np_lows=numpy.array(x.low)
        np_closes = numpy.array(x.close)
        slowk, slowd = tulipy.stoch(np_highs,np_lows,np_closes,pct_k_period=STOCH_PERIOD,pct_k_slowing_period=SLOW_K,pct_d_period=SLOW_D)
        return slowk, slowd
    def slowk(x):
        slowk=Indicators_calculations.stochastic(x)[0]
        return slowk
    def slowd(x):
        slowd=Indicators_calculations.stochastic(x)[1]
        return slowd
    def ema1(x):
        np_closes = numpy.array(x.close)
        ema1 = tulipy.ema(np_closes, period=EMA1_PERIOD)
        return ema1
    def ema2(x):
        np_closes = numpy.array(x.close)
        ema2 = tulipy.ema(np_closes, period=EMA2_PERIOD)
        return ema2    


class Strategy(object):
    def HighSpikesUpdate(asset_selected):
        # log("trying high spike update")
        if len(asset_selected.rsi)>1 and asset_selected.rsi[-1]<=30.00:  #len(prices_high_spikes)> 4 and len(rsis_high_spikes)> 4:
            asset_selected.prices_high_spikes.clear()   
            asset_selected.rsis_high_spikes.clear()
        
        # MINIMAL PERCENTAGE CHANGE TO ENTER HIGH SPIKES TO THE SAVED LIST / NOT USED RIGHT NOW
        # if  ((abs(asset_selected.close[-1]-asset_selected.close[-2])) > (asset_selected.close[-1]*params.Minimal_percentage_change*1/100) 
        #     and (abs(asset_selected.close[-3]-asset_selected.close[-2])) > (asset_selected.close[-1]*params.Minimal_percentage_change*1/100)):
        
        if  asset_selected.close[-1]<asset_selected.close[-2] and asset_selected.close[-2]>asset_selected.close[-3]  and asset_selected.rsi[-2]>70.00:
            asset_selected.prices_high_spikes.insert(0,asset_selected.close[-2])
            asset_selected.rsis_high_spikes.insert(0,asset_selected.rsi[-2])
    

    def LowSpikesUpdate(asset_selected):
        # log("trying low spike update")
        if len(asset_selected.rsi)>1 and asset_selected.rsi[-1]>=70.00: #len(prices_low_spikes)> 4 and len(rsis_low_spikes)> 4: 
            asset_selected.prices_low_spikes.clear()   
            asset_selected.rsis_low_spikes.clear()
        
        # MINIMAL PERCENTAGE CHANGE TO ENTER LOW SPIKES TO THE SAVED LIST / NOT USED RIGHT NOW
        # if  ((abs(asset_selected.close[-1]-asset_selected.close[-2])) > (asset_selected.close[-1]*params.Minimal_percentage_change*1/100) 
        #     and (abs(asset_selected.close[-3]-asset_selected.close[-2])) > (asset_selected.close[-1]*params.Minimal_percentage_change*1/100)):
        
        if asset_selected.close[-1]>asset_selected.close[-2] and asset_selected.close[-2]<asset_selected.close[-3] and asset_selected.rsi[-2]<50.00:
            asset_selected.prices_low_spikes.insert(0,asset_selected.close[-2])
            asset_selected.rsis_low_spikes.insert(0,asset_selected.rsi[-2])

    def buy_signal(asset_selected):
        # FUNCTION TO FIND BOTTOMS BY LOOKING FOR CONVERGENCES BETWEEN PRICE GOING DOWN AND RSI GOING UP
        log("buy_signal function initiated")
        if len(asset_selected.prices_low_spikes)>2 and len(asset_selected.rsis_low_spikes)>2 and len(asset_selected.prices_low_spikes) == len(asset_selected.rsis_low_spikes):
            if asset_selected.prices_low_spikes[0]==asset_selected.close[-2]:
                for x in asset_selected.prices_low_spikes:
                    if asset_selected.prices_low_spikes[0]<x:
                        z =asset_selected.rsis_low_spikes[asset_selected.prices_low_spikes.index(x)]
                        if asset_selected.rsis_low_spikes[0]>z:
                            buycriteria=('P-LOW-0 %.2f, P-LOW-1 %.2f, RSI-LOW-0 %.2f, RSI-LOW-1 %.2f' % (asset_selected.prices_low_spikes[0], x, asset_selected.rsis_low_spikes[0], z))
                            log(buycriteria)
                            log2(str(buycriteria))
                            #log('%s' % buycriteria)
                            # if len(asset_selected.Barrel)>3:
                            #     log("trying to clean barrel")
                            #     asset_selected.Barrel.clear()
                            #     log("clean barrel completed")
                            asset_selected.Barrel.append('Bottom')
                            return  True
                else: 
                            return False
            else: 
                            return False
        else: 
                            return False

    def sell_signal(asset_selected):
        # FUNCTION TO FIND TOPS BY LOOKING FOR DIVERGENCES BETWEEN PRICE GOING UP AND RSI GOING DOWN
        log("sell_signal function initiated")
        if len(asset_selected.prices_high_spikes)>2 and len(asset_selected.rsis_high_spikes)>2:
            if asset_selected.prices_high_spikes[0]==asset_selected.close[-2]:
                for x in asset_selected.prices_high_spikes:
                    if asset_selected.prices_high_spikes[0]>x:
                        z=asset_selected.rsis_high_spikes[asset_selected.prices_high_spikes.index(x)]
                        if asset_selected.rsis_high_spikes[0]<z:
                            sellcriteria=('P-HIGH-0 %.2f,  P-HIGH-1 %.2f, RSI-HIGH-0 %.2f, RSI-HIGH-1 %.2f' % (asset_selected.prices_high_spikes[0], x, asset_selected.rsis_high_spikes[0], z))
                            log(sellcriteria)
                            log2(str(sellcriteria))
                            #log('%s' % sellcriteria)
                            # if len(asset_selected.Barrel)>3:
                            #     log("trying to clean barrel")
                            #     asset_selected.Barrel.clear()
                            #     log("clean barrel completed")
                            asset_selected.Barrel.append('Top')
                            return  True
                else: 
                    return False
            else: 
                            return False
        else: 
                            return False
class Crypto_pair(object):
    def __init__(self, symbol, interval, *args):
        # symbol and timeframe
        
        self.symbol=symbol
        self.interval=interval
        
        # price data and time of candle open

        open_time,open,high,low,close,volume=([]for i in range(6))

        self.open_time=open_time
        self.open=open
        self.high=high
        self.low=low
        self.close=close
        self.volume=volume

        # indicators lists to be updated everytime
        
        atr, rsi, slowk, slowd, ema1, ema2 = ([]for i in range(6))

        self.atr=atr
        self.rsi=rsi
        self.slowk=slowk
        self.slowd=slowd
        self.ema1=ema1
        self.ema2=ema2


        # lists to be updated for spikes and barrel (bottom of the barrel or top)

        prices_high_spikes, rsis_high_spikes, prices_low_spikes, rsis_low_spikes=([]for i in range(4))

        self.prices_high_spikes=prices_high_spikes   
        self.rsis_high_spikes=rsis_high_spikes
        self.prices_low_spikes=prices_low_spikes
        self.rsis_low_spikes=rsis_low_spikes

        Barrel=[]

        self.Barrel=Barrel

        self.args=args

def all_indis_update(x):
        x.atr=Indicators_calculations.atr(x)
        x.rsi=Indicators_calculations.rsi(x)
        x.slowk=Indicators_calculations.slowk(x)
        x.slowd=Indicators_calculations.slowd(x)
        x.ema1=Indicators_calculations.ema1(x)
        x.ema2=Indicators_calculations.ema2(x)        

def strategy_data_update(x):
        Strategy.HighSpikesUpdate(x)
        Strategy.LowSpikesUpdate(x)
        Strategy.buy_signal(x)
        Strategy.sell_signal(x)


BTC_USDT_1minute=Crypto_pair('BTCUSDT', '1m')
BTC_USDT_1hour=Crypto_pair('BTCUSDT', '1h')
BTC_USDT_4hour=Crypto_pair('BTCUSDT', '4h')
BTC_USDT_daily=Crypto_pair('BTCUSDT', '1d')

### ASSETS OR PAIRS THAT CAN BE USED TO TRADE
enabled_assets=[
                BTC_USDT_1minute,
                BTC_USDT_1hour,
                BTC_USDT_4hour,
                BTC_USDT_daily
                ]

############################################################################

def history():
    
    candlestick_lists = [
                    get_data.One_Minute_candlesticks, 
                    get_data.One_H_candlesticks, 
                    get_data.Four_H_candlesticks, 
                    get_data.D_candlesticks
                    ]
    
    def appender(n=0):
        for candles in candlestick_lists[n]:
                enabled_assets[n].open_time.append(float(candles[0])),
                enabled_assets[n].open.append(float(candles[1])),
                enabled_assets[n].high.append(float(candles[2])),
                enabled_assets[n].low.append(float(candles[3])),
                enabled_assets[n].close.append(float(candles[4])),
                enabled_assets[n].volume.append(float(candles[5])),
                # print("-----------------------")            
                if  len(enabled_assets[n].close)>=30:
                    all_indis_update(enabled_assets[n])
                    strategy_data_update(enabled_assets[n])
        return
    
    def cleaner():
        for lists in candlestick_lists:
            lists.clear()
        print("HISTORICAL DATA APPENDED AND CLEANED FROM GET_DATA LISTS")
        return

    for i in range(len(enabled_assets)):
        print(i)
        appender(i)
    
    cleaner()
    
history()

def on_open(ws):
    log('opened connection')
    log(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))

def on_close(ws):
    log('closed connection')

def on_message(ws, message):
    json_message = json.loads(message)
    # pprint.pprint(json_message)
    
    data=json_message['data']
    candle = data['k']
    # candle = json_message['k']

    is_candle_closed = candle['x']
    
    Time_open = candle['t']
    message_symbol = candle['s']
    message_interval = candle['i']

    open = candle['o']
    high = candle['h']
    low = candle['l']
    close = candle['c']
    volume = candle['v']
    
    def Trade_logic_as_per_selected_asset(asset_selected):
        ##################################################
        # PIECE OF CODE TO TEST ASSET LISTS AND VARIABLES
        # asset_selected=BTC_USDT_1minute
        ##################################################

        log(">>>>>>>>>>>>>>> NEW CANDLE CLOSED @ {} <<<<<<<<<<<<<<<".format(close))
        log(">>>"+asset_selected.symbol+"<<<")
        log(">>>"+asset_selected.interval+"<<<")
        log(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
        # log("minimal change % " + str(params.Minimal_percentage_change*1/100))
        asset_selected.open_time.append(int(Time_open))
        asset_selected.open.append(float(open))
        asset_selected.high.append(float(high))
        asset_selected.low.append(float(low))
        asset_selected.close.append(float(close))
        asset_selected.volume.append(float(volume))
        log("APPENDING SUCCESSFUL")
        all_indis_update(asset_selected)
        
        # log(asset_selected.close)
        
        # SNIPPET TO ACTIVATE HIGH AND LOW SPIKE LISTS UPDATE
        if len(asset_selected.close)>3 and len(asset_selected.rsi)>3:
            log("trying to update spikes! start")
            log("minimal change % " + str(params.Minimal_percentage_change*1/100))

            Strategy.HighSpikesUpdate(asset_selected)
            
            log("High Prices")
            log(asset_selected.prices_high_spikes) 
            log("High RSIs")
            log(asset_selected.rsis_high_spikes)
            
            Strategy.LowSpikesUpdate(asset_selected)
            
            log("Low Prices")
            log(asset_selected.prices_low_spikes)
            log("Low RSIs")
            log(asset_selected.rsis_low_spikes)
            
            log("trying to update spikes! end")
        
        # ACTIVATION OF BUY AND SELL SIGNALS FOR TOP AND BOTTOMS
        buysignal=Strategy.buy_signal(asset_selected)
        log(buysignal)
        sellsignal=Strategy.sell_signal(asset_selected)
        log(sellsignal)
        log("Barrel")
        log(asset_selected.Barrel)

        # log("Data for daily")
        # log(BTC_USDT_daily.open_time)
        # log(BTC_USDT_daily.close)
        # log("Data for 4 hr")
        # log(BTC_USDT_4hour.open_time)
        # log(BTC_USDT_4hour.close)
        # log("Data for 1 hr")
        # log(BTC_USDT_1hour.open_time)
        # log(BTC_USDT_1hour.close)
        # log("Data for 1 minute")
        # log(BTC_USDT_1minute.open_time)
        # log(BTC_USDT_1minute.close)

        # SNIPPED TO KEEP TRACK OF BARREL LIST LENGTH        
        # if  len(asset_selected.Barrel)>1 and len(asset_selected.Barrel) != params.lenbarrel:
        #     params.lenbarrel = len(asset_selected.Barrel)
            


        def Loss_trend_signal():  #  STRATEGY SIGNAL
            # FUNCTION IN CASE LOSS OF TREND TO EXIT POSITION
            if  (asset_selected.ema1[-2]>asset_selected.ema2[-2] and asset_selected.ema1[-1]<asset_selected.ema2[-1]) or (asset_selected.ema1[-2]==asset_selected.ema2[-2] and asset_selected.ema1[-1]<asset_selected.ema2[-1]):
                log2("LOSS TREND SIGNAL SHOWS TRUE***")
                return True

        def continuation_buy_signal():  #  STRATEGY SIGNAL
            # FUNCTION TO ENTER BUY POSITION IN A TREND CONTINUATION 
            if  len(asset_selected.Barrel)>1 and asset_selected.Barrel[-2] == 'Bottom' and asset_selected.Barrel[-1] == 'Bottom':
                # if  ema1[-1]<ema2[-1] and ema1[0]>ema2[0] or (ema1[-1]==ema2[-1] and ema1[0]>ema2[0]):
                #     return True
                if asset_selected.slowk[-1]>asset_selected.slowd[-1] and asset_selected.slowk[-2]<asset_selected.slowd[-2] and asset_selected.ema1[-1]>asset_selected.ema2[-1]:
                    log2("CONTINUATION BUY SIGNAL SHOWS TRUE***")
                    log2("CONTINUATION BUY SIGNAL IS DISABLED***")
                    return False
                else: 
                    log2("***CONTINUATION BUY SIGNAL SHOWS FALSE")
                    return False
        
        i_registry.position_now_qtty=account_info.Position.get_actual_position("amount")
        p_entry_price_now=account_info.Position.get_actual_position("entryprice")
        last_total_cash=account_info.Total_Cash()

        ###############################################################################################
        def Global_Buy_operation(increment_factor=1.0):  # MAIN OPERATION
            # ACTUAL EXECUTION OF TRAIL BUY ORDER USED TO ENTER LONG/BUY POSITIONS
            try:
                stoppricebyatr=asset_selected.close[-1]-(params.atr_stop_factor*0.1*asset_selected.atr[-1])
                
                stoppricebyatr_rate=((params.atr_stop_factor*0.1*asset_selected.atr[-1])*100)/asset_selected.close[-1]
                stoppricebyatr_rate=round(stoppricebyatr_rate,ndigits=1)
                
                
                if stoppricebyatr_rate < 0.1:
                    stoppricebyatr_rate=0.1
                if stoppricebyatr_rate > 5.0:
                    stoppricebyatr_rate=5.0
                
                stoppricebyatr_rate=str(stoppricebyatr_rate)
                
                takeprofitprice=asset_selected.close[-1]+(asset_selected.close[-1]*10/100)
                
                Cash_to_risk=last_total_cash*params.percentage_to_risk/100

                if increment_factor>1.0:
                    PositionSize=float(increment_factor)*float(Pos_Sizing_Reg[-1])
                else:
                    PositionSize=params.granularity*Cash_to_risk    #<<<--- GRANULARITY DETERMINES THE FIRST POSITION SIZE

                if  PositionSize>params.position_upper_limit-i_registry.position_now_qtty:
                    PositionSize=params.position_upper_limit-i_registry.position_now_qtty
                
                if  PositionSize<params.position_lower_limit:
                    PositionSize=params.position_lower_limit
                PositionSize=round(PositionSize, ndigits=3)

                PositionSize=str(PositionSize)
                Pos_Sizing_Reg.append(PositionSize)

                price_to_use=round(asset_selected.close[-1],ndigits=2)
                price_to_use=str(price_to_use)  
                Type_of_Stop='S'
                
                log('BUY CREATE, %.2f' % asset_selected.close[-1])
                log('BUY SIZE, ' + Pos_Sizing_Reg[-1])
                log('Cash_to_risk, %.2f' % Cash_to_risk)
                log('self.atr[-1], %.2f' % asset_selected.atr[-1])
                
                log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                log3('BUY CREATE, %.2f' % asset_selected.close[-1])
                log3('BUY SIZE, ' + Pos_Sizing_Reg[-1])
                log3('Cash_to_risk, %.2f' % Cash_to_risk)
                log3('stoppricebyatr_rate, ' + stoppricebyatr_rate)
                
                buy_order= account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                                                        side=account_info.OrderSide.BUY,
                                                        ordertype=account_info.OrderType.LIMIT, ### <--LIMIT ORDER
                                                        timeInForce=account_info.TimeInForce.GTC,
                                                        price=price_to_use,
                                                        # callbackRate=stoppricebyatr_rate, 
                                                        quantity=Pos_Sizing_Reg[-1]
                                                        )
                # buy_order= account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                #                                         side=account_info.OrderSide.BUY,
                #                                         ordertype=account_info.OrderType.TRAILING_STOP_MARKET, ### <--TRAIL STOP MARKET
                #                                         timeInForce=account_info.TimeInForce.GTC,
                #                                         callbackRate=stoppricebyatr_rate, 
                #                                         quantity=Pos_Sizing_Reg[-1]
                #                                         )
                order_history.append(buy_order)
                log('BUY PRICE PARAMETER, ' + price_to_use)
                log3('BUY PRICE PARAMETER, ' + price_to_use)

                log('BUY SIZE END, ' + Pos_Sizing_Reg[-1])
                log3('BUY SIZE END, ' + Pos_Sizing_Reg[-1])
            except Exception as e:
                log(e)
                log3(e)

        ###############################################################################################
        def trailing_stop_to_secure_profits_operation():  # SUPPORT OPERATION
            # ACTUAL EXECUTION OF TRAIL STOP SELL ORDER
            try:
                stoppricebyatr=asset_selected.close[-1]-(params.atr_stop_factor*0.1*asset_selected.atr[-1])
                
                stoppricebyatr_rate=((params.atr_stop_factor*0.1*asset_selected.atr[-1])*100)/asset_selected.close[-1]
                stoppricebyatr_rate=round(stoppricebyatr_rate,ndigits=1)
                
                if stoppricebyatr_rate < 0.1:
                    stoppricebyatr_rate=0.1
                if stoppricebyatr_rate > 5.0:
                    stoppricebyatr_rate=5.0
                stoppricebyatr_rate=str(stoppricebyatr_rate)

                log('TRAILING STOP CREATE, %.2f' % asset_selected.close[-1])
                log('self.atr[-1], %.2f' % asset_selected.atr[-1])
                
                log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                log3('TRAILING STOP CREATE, %.2f' % asset_selected.close[-1])
                log3('stoppricebyatr_rate, ' + stoppricebyatr_rate)
            
                trailing_sell_order = account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                                                        side=account_info.OrderSide.SELL, 
                                                        ordertype=account_info.OrderType.TRAILING_STOP_MARKET, ### <--TRAIL STOP MARKET
                                                        timeInForce=account_info.TimeInForce.GTC,
                                                        callbackRate=stoppricebyatr_rate, 
                                                        quantity=str(i_registry.position_now_qtty), 
                                                        )
                order_SL_history.append(trailing_sell_order)
                
                log('TRAILING STOP SIZE, ' + str(i_registry.position_now_qtty))
                log3('TRAILING STOP SIZE, ' + str(i_registry.position_now_qtty))
            except Exception as e:
                log(e)
                log3(e)

        ###############################################################################################
        def Hard_stop_order_operation():  # SUPPORT OPERATION
            # ACTUAL EXECUTION OF HARD STOP ORDER USED AS EXIT SAFETY ORDER
            try:
                hs_price=params.hard_stop_price

                log('HARD STOP CREATE, %.2f' % hs_price)
                
                log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                log3('HARD STOP CREATE, %.2f' % hs_price)
                
                if i_registry.position_now_qtty>0.0:
                    hard_stop= account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                                                        side=account_info.OrderSide.SELL,
                                                        ordertype=account_info.OrderType.STOP_MARKET, ### <--STOP MARKET
                                                        timeInForce=account_info.TimeInForce.GTC,
                                                        stopPrice=hs_price,
                                                        closePosition='true'
                                                        )
                elif i_registry.position_now_qtty<0.0:
                    hard_stop= account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                                                        side=account_info.OrderSide.BUY,
                                                        ordertype=account_info.OrderType.STOP_MARKET, ### <--STOP MARKET
                                                        timeInForce=account_info.TimeInForce.GTC,
                                                        stopPrice=hs_price,
                                                        closePosition='true'
                                                        )
                
                
                order_SL_history.append(hard_stop)
                
                log('HARD STOP CREATED SUCCESSFULLY')
                
                log3('HARD STOP CREATED SUCCESSFULLY')
            except Exception as e:
                log(e)
                log3(e)

        ###############################################################################################

        def cancel_all_orders():  # MAIN OPERATION
            # CANCEL UNFULFILLED ORDERS
            log('CANCELLING ALL ORDERS')
            account_info.client.cancel_all_orders(symbol=GLOBAL_SYMBOL)
            log('ORDERS CANCELLED')

        def close_active_position():  # MAIN OPERATION
            # CLOSE ACTIVE POSITION BY SELLING OR BUYING AT MARKET PRICE
            if i_registry.position_now_qtty>0.0:
                try:
                    log('Closing Long position')
                    log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                    log3('Closing Long position')
                    account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                                                    side=account_info.OrderSide.SELL, 
                                                    ordertype=account_info.OrderType.MARKET,### <--- THIS IS A STOP MARKET ORDER 
                                                    quantity=str(round(account_info.Position.get_actual_position("amount"),ndigits=3)),
                                                    reduceOnly="True" 
                                                    )
                    log('Finished Closing Long position')
                    log3('Finished Closing Long position')
                except Exception as e:
                    log(e)
            
            elif i_registry.position_now_qtty<0.0:
                try:
                    log('Closing Short position')
                    log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                    log3('Closing Short position')
                    account_info.client.post_order(symbol=GLOBAL_SYMBOL, 
                                                    side=account_info.OrderSide.BUY, 
                                                    ordertype=account_info.OrderType.MARKET,### <--- THIS IS A STOP MARKET ORDER  
                                                    quantity=str(round(account_info.Position.get_actual_position("amount"),ndigits=3)),
                                                    reduceOnly="True" 
                                                    )
                    log('Finished Closing Short position')
                    log3('Finished Closing Short position')
                except Exception as ex:
                    log(ex)
                    log3(ex)


        # def OneTradePerBar():
        #     # NOT USED RIGHT NOW/ INACTIVE -- THIS DOESNT WORK DUE TO asset_list_cleaner FUNCTION
        #     if len(asset_selected.close) != params.NewBar:
        #         params.NewBar=len(asset_selected.close)
        #         return True
        #     else:
        #         return False

        def are_we_in_a_position(): #ACCOUNT INFO
            # ACCOUNT INFO TO KNOW IF WE ARE IN A POSITION
            if  i_registry.position_now_qtty> 0.0 or i_registry.position_now_qtty<0.0:
                log2(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")+" WE ARE IN A POSITION ALREADY")
                log2("Position size now: "+str(i_registry.position_now_qtty))
                return True

            else:
                log2(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")+" NO WE ARE NOT IN A POSITION")
                log2("Position size now: "+str(i_registry.position_now_qtty))
                return False
            
        def clean_buy_slate():  #ACCOUNT INFO
            # CLEANING POSITION SIZING REGISTRY IN CASE THERE ARE NO OPEN POSITIONS OR ORDERS
            log2("Trying to clean slate")
            if in_a_position == False and  account_info.Orders.open_orders("buy") == 0:
                log2("Slate cleaned succesfully part 1")
                Pos_Sizing_Reg.clear()
                log2("Slate cleaned succesfully part 2")
            else:
                log2("No need to clean slate")
                
        
        def Number_of_consecutive_positions():  #ACCOUNT INFO  

            Position_counter=len(Pos_Sizing_Reg)

            if Position_counter==None:
                Position_counter=int(0)
            else:
                Position_counter=Position_counter

            log2("Position_counter: "+str(Position_counter))
            return  Position_counter
        
        in_a_position=are_we_in_a_position()

                #    EXECUTION OF BUY OR SELL CONDITIONS

        #########################################################################################
        
        def enter_buy_position():  # CONDITIONS
            # Check if we are in the market
            # ENTER FIRST BUY POSITION
            if in_a_position == False and  account_info.Orders.open_orders("buy") == 0:
                log2("Standard buy condition 1 true")
                
                ### TO BUY
                if  buysignal:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    log("Standard Buy")
                    log2("Standard Buy")
                    i_registry.is_secure_profit_order_on=False
                    i_registry.is_safety_hard_stop_on=False
                    Global_Buy_operation()    
                
                ### TO BUY
                elif  continuation_buy_signal():
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    log("continuation_buy")
                    log2("continuation_buy")
                    i_registry.is_secure_profit_order_on=False
                    i_registry.is_safety_hard_stop_on=False
                    Global_Buy_operation()
        
        ############################################################################################
        
        def increase_buy_position():  # CONDITIONS
            # Check if we are in the market
            # INCREASE POSITION SIZE BY BUYING
            ### TO BUY
            if in_a_position == True: 
                if account_info.Orders.open_orders("buy") == 0 and i_registry.position_now_qtty<params.position_upper_limit:
                    log2("continuation buy condition 1 True")
                    if asset_selected.close[-1]<p_entry_price_now:
                        log2("continuation buy condition 2 True")
                        ### TO BUY
                        if  buysignal:
                            # BUY, BUY, BUY!!! (with all possible default parameters)
                            log("Standard Buy")
                            log2("Standard Buy")
                            log("FINDING WTF HAPPEND")
                            log(Pos_Sizing_Reg[-1])
                            log(asset_selected.close[-1])
                            log(asset_selected.atr[-1])
                            log("EVERYTHING PRINTED")
                            Global_Buy_operation(increment_factor=2.0)    
                        
                        ### TO BUY
                        elif  continuation_buy_signal():
                            # BUY, BUY, BUY!!! (with all possible default parameters)
                            log("continuation_buy")
                            log2("continuation_buy")
                            Global_Buy_operation(increment_factor=2.0)

        ############################################################################################
        
        def secure_buy_profits(): # CONDITIONS
            #   IT'S A SELL
            ### CLOSE ACTIVE BUY POSITION BY SETTING A TRAIL STOP SELL
            if in_a_position == True: 
                if account_info.Orders.open_orders("sell") == 0 or i_registry.is_secure_profit_order_on == False:
                    log2("secure buy profits condition 1 True")
                    if i_registry.position_now_qtty > 0.0:
                        log2("secure buy profits condition 2 True")
                        ### TO SELL
                        if  asset_selected.rsi[-1]>70.0 and asset_selected.close[-1]>p_entry_price_now+(asset_selected.atr[-1]*2.5):
                            # SELL, SELL, SELL!!! (with all possible default parameters)
                            log("Securing buy profits")
                            log2("Securing buy profits")
                            cancel_all_orders()
                            trailing_stop_to_secure_profits_operation()
                            i_registry.is_secure_profit_order_on=True    

        ############################################################################################
        
        def safety_stop_conditions():  # CONDITIONS
            ### PUT A SAFETY ORDER TO CLOSE POSITION IN CASE OF A BIG MOVE
            if in_a_position == True: 
                if account_info.Orders.open_orders("sell") == 0 or i_registry.is_safety_hard_stop_on == False:
                    log2("hard stop condition 1 True")
                    if i_registry.position_now_qtty > 0.0:
                        log2("hard stop condition 2 True")
                        ### TO SELL
                        Hard_stop_order_operation()
                        i_registry.is_safety_hard_stop_on=True    

        ############################################################################################
        
        def exit_buy_position():  # CONDITIONS  
            #   IT'S A SELL
            ### CLOSE ACTIVE BUY POSITION BY SELLING
            log2("exit_buy_position function start")
            log2(in_a_position)
            if in_a_position == True:
                log2("exit condition 1 true") 
                log2(asset_selected.close[-1])
                log2(p_entry_price_now+(p_entry_price_now*0.0005))
                if asset_selected.close[-1]>p_entry_price_now+(p_entry_price_now*0.0005):
                    log2("exit condition 2 true")
                    if sellsignal or Loss_trend_signal():
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                        log2("trying to cancel and close starting...")
                        cancel_all_orders()
                        close_active_position()
                        log('SELL-CLOSE CREATE @ PRICE, %.2f' % asset_selected.close[-1])
        

        def multi_timeframe_filter(): # CONDITIONS
            # IF 1D AND 4H AND 1H ASSET SHOWS TWO BOTTOMS IN A ROW RETURN TRUE/GREEN LIGHT TO TRADE
            for x in enabled_assets:
                if x.interval=='1d' and len(x.Barrel)>=2 and x.symbol==asset_selected.symbol:
                    if x.Barrel[-1]=='Bottom' and x.Barrel[-2]=='Bottom':
                        log2(x.symbol+' in '+x.interval+' candles is showing 2 bottoms in the barrel')
                        
                        for y in enabled_assets:
                            if y.interval=='4h' and len(y.Barrel)>=2 and y.symbol==asset_selected.symbol:
                                if y.Barrel[-1]=='Bottom' and y.Barrel[-2]=='Bottom':
                                    log2(y.symbol+' in '+y.interval+' candles is showing 2 bottoms in the barrel')    
                                
                                    for z in enabled_assets:
                                        if z.interval=='1h' and len(z.Barrel)>=2 and z.symbol==asset_selected.symbol:
                                            if z.Barrel[-1]=='Bottom' and z.Barrel[-2]=='Bottom':
                                                log2(z.symbol+' in '+z.interval+' candles is showing 2 bottoms in the barrel')
                                                return True
            else:
                return False
        
        def asset_list_cleaner(): # ASSET INFO
            #CHECK IF ANY ASSET LIST IS ABOVE 91 ELEMENTS AND ERASE THE OLDEST (FIRST IN THE LIST) TO SAVE MEMORY
            # for x in enabled_assets:
            #     asset_properties=[x.open_time, x.open, x.high, x.low, x.close, x.volume]
            #     for y in asset_properties:
            #         if len(y)>=91:
            #             y.remove(y[0])
            
            asset_properties=[asset_selected.open_time, 
                              asset_selected.open, 
                              asset_selected.high, 
                              asset_selected.low, 
                              asset_selected.close, 
                              asset_selected.volume,
                              asset_selected.Barrel]
            for y in asset_properties:
                while len(y)>=91:
                    y.remove(y[0])
                    
        asset_list_cleaner()
        clean_buy_slate()
        
        # ONLY EXECUTE TRADES IF INTERVAL IS 1 MINUTE
        if asset_selected.interval=='1m':
            safety_stop_conditions()
            m_t_f=multi_timeframe_filter()
            log("Finding if higher timeframes give a green light: (multi_timeframe_filter function):")
            log(m_t_f)
            log("Is Manual filter override on:")
            log(params.Manual_filter_override)
            if m_t_f or params.Manual_filter_override:
                increase_buy_position()
            secure_buy_profits()
            exit_buy_position()
            if m_t_f or params.Manual_filter_override:
                enter_buy_position()
            print("1 MINUTE ASSET CLOSE LENGHT OF LIST: "+str(len(asset_selected.close)))
            print("OLDEST 1 MINUTE OPENING TIME: "+str(datetime.fromtimestamp(asset_selected.open_time[0])))
            print("OLDEST 1 MINUTE CLOSING PRICE: "+str(asset_selected.close[0]))
            print("1 HOUR CANDLES WITH 2*90 THE LIMIT IN GET DATA")
        if asset_selected.interval=='1h':
            print("1 HOUR ASSET CLOSE LENGHT OF LIST: "+str(len(asset_selected.close)))
        ############################################################################################
    
    
    for x in enabled_assets:
        if is_candle_closed and message_symbol==x.symbol and message_interval==x.interval:
                z=x
                Trade_logic_as_per_selected_asset(z)
        else:
            continue

class RepeatedTimer2(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

def Keep_alive_websocket():
    ws.close()
    kaw_message=">>>>>Websocket client restarted!!!!! "
    print(kaw_message)
    print(kaw_message)
    print(kaw_message)
    log(kaw_message)
    log(kaw_message)
    log(kaw_message)
    log2(kaw_message)
    log2(kaw_message)
    log2(kaw_message)   
    ws.run_forever(ping_interval=30)

rt_websocket = RepeatedTimer2(60*60*23, Keep_alive_websocket) # it auto-starts, no need of rt.start()

ws.run_forever(ping_interval=30)

