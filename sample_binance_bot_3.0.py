BOT_VERSION="3.1.25"
BOT_LAST_CHANGE_DONE="several errors finding x13, exit and enter conditions x2, MACD NEW PERIODS, INPUT CONFIG 15min, conditions try except LOGGING"
import websocket, json, numpy, tulipy 
import input_config
print("BOT VERSION : "+str(BOT_VERSION))
print("BOT_LAST_CHANGE_DONE : "+str(BOT_LAST_CHANGE_DONE))
import account_info
import get_data
import threading 
import time
from datetime import datetime

import internal_registry
import trade_conditions
import operations
import signals

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
BB_PERIOD = 7
GLOBAL_SYMBOL = input_config.GLOBAL_SYMBOL
MACD_FAST=12#9
MACD_SLOW=26#17
MACD_SIGNAL_SMOOTHING=9

i_registry=internal_registry.internal_registry()

# PARAMETERS TO CONTROL THE BOT WITHOUT SCROLLING DOWN TOO MUCH
class   control_params(object): 
    def __init__(self, *args):
        self.Manual_filter_override=False
        self.NewBar=0
        self.lenbarrel=None
        self.rsiperiod= 7
        self.atrperiod= 14
        
        self.atr_stop_factor= 10 #divide by 10 ie: 12/10 = 1.2 times the ATR = 120% of the ATR --- 12 is the best for the daily
        
        # ((params.atr_stop_factor*0.1*asset_selected.atr[-1])*100)/asset_selected.close[-1]
        
        self.Minimal_percentage_change= 0.25 #divide by 10 ie: 11/10 = 1.1% --- 10-11 are the best for the daily
        
        #MAX FEE RATE USED BY BINANCE 0.02 maker/ 0.04 taker ALWAYS USING TAKER
        self.fee_rate=0.04 # TAKER RATE

        # MONEY MANAGEMENT
        self.is_position_size_fixed="yes"
        self.fixed_position_size=0.001 #POSITION SIZING

        #EXITING POSITIONS BY MINIMAL FEES OR MINIMAL RAW CASH IN PROFIT
        self.exit_by_goal="fees" #"cash"
        # MINIMUM CASH IN PROFIT TO HEDGE THE POSITION TO NEUTRAL
        self.minimum_cash_profit=0.5
        self.minimal_price_diff_to_enter=5.0
        # TARGET DIFFERENCE BETWEEN LONG AND SHORT POSITIONS
        self.delta_bias="neutral" #"negative" #"positive" 
        self.control_target_delta=0.000 #DELTA NEUTRAL
        self.max_delta=0.005
        
        # POSITION SIZE LIMITS
        self.position_upper_limit=1.000
        self.position_lower_limit=0.001
        
        #UNUSED
        # PARAMETERS TO CONTROL POSITION SIZING AND MONEY MANAGEMENT
        self.percentage_to_risk=10#UNUSED
        # GRANULARITY IS INSTRUMENTAL TO CONTROL SIZE OF POSITION AND AVOID LIQUIDATION
        self.granularity=0.00002#0.00001#UNUSED
        # self.hard_stop_price=32100.00#38700.00 #NOT BEING USED ANYMORE (RIGHT NOW)

params=control_params()


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
    def B_bands(x):
        np_closes = numpy.array(x.close)
        bollinger_bands= tulipy.bbands(np_closes, period=BB_PERIOD, stddev=2)
        return bollinger_bands
    def Upper_B_band(x):
        Upper_B_band=Indicators_calculations.B_bands(x)[2]
        return Upper_B_band
    def Mid_B_band(x):
        Mid_B_band=Indicators_calculations.B_bands(x)[1]
        return Mid_B_band
    def Lower_B_band(x):
        Lower_B_band=Indicators_calculations.B_bands(x)[0]
        return Lower_B_band
    def MACD(x):
        np_closes = numpy.array(x.close)
        macd=tulipy.macd(np_closes,short_period=MACD_FAST, long_period=MACD_SLOW, signal_period=MACD_SIGNAL_SMOOTHING)
        macd=list(numpy.around(macd,1))
        return macd
    def fast_macd(x):
        fast_one=x.macd[0]
        return fast_one
    def slow_macd(x):
        slow_one=x.macd[1]
        return slow_one
    def histogram_macd(x):
        histogram=x.macd[2]
        return histogram



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

        upper_bband, lower_bband = ([]for i in range(2))
        
        self.upper_bband=upper_bband
        self.lower_bband=lower_bband
        
        macd, fast_macd, slow_macd, histogram_macd= ([]for i in range(4))
        
        self.macd=macd
        self.fast_macd=fast_macd
        self.slow_macd=slow_macd
        self.histogram_macd=histogram_macd


        # lists to be updated for spikes and barrel (bottom of the barrel or top)

        prices_high_spikes, rsis_high_spikes, prices_low_spikes, rsis_low_spikes=([]for i in range(4))

        self.prices_high_spikes=prices_high_spikes   
        self.rsis_high_spikes=rsis_high_spikes
        self.prices_low_spikes=prices_low_spikes
        self.rsis_low_spikes=rsis_low_spikes

        Barrel=[]

        self.Barrel=Barrel

        self.args=args

    def asset_list_cleaner(self): # ASSET INFO
        try:
            #CHECK IF ANY ASSET LIST IS ABOVE 91 ELEMENTS AND ERASE THE OLDEST (FIRST IN THE LIST) TO SAVE MEMORY
            # for x in enabled_assets:
            #     asset_properties=[x.open_time, x.open, x.high, x.low, x.close, x.volume]
            #     for y in asset_properties:
            #         if len(y)>=91:
            #             y.remove(y[0])
            
            asset_properties=[self.open_time, 
                              self.open, 
                              self.high, 
                              self.low, 
                              self.close, 
                              self.volume,
                              self.Barrel]
            for y in asset_properties:
                if len(y)>=91:
                    y.remove(y[0])
        except Exception as e:
                    i_registry.log(e)

def all_indis_update(x):
        x.atr=Indicators_calculations.atr(x)
        x.rsi=Indicators_calculations.rsi(x)
        x.slowk=Indicators_calculations.slowk(x)
        x.slowd=Indicators_calculations.slowd(x)
        x.ema1=Indicators_calculations.ema1(x)
        x.ema2=Indicators_calculations.ema2(x)        
        x.upper_bband=Indicators_calculations.Upper_B_band(x)
        x.lower_bband=Indicators_calculations.Lower_B_band(x)
        x.macd=Indicators_calculations.MACD(x)
        x.fast_macd=Indicators_calculations.fast_macd(x)
        x.slow_macd=Indicators_calculations.slow_macd(x)
        x.histogram_macd=Indicators_calculations.histogram_macd(x)

def strategy_data_update(x):
        i_registry.signals=signals.Sample_Signals(x, i_registry=i_registry)
        i_registry.signals.buy_signal()
        i_registry.signals.sell_signal()


BTC_USDT_1minute=Crypto_pair('BTCUSDT', '1m')
BTC_USDT_15min=Crypto_pair('BTCUSDT', '15m')
BTC_USDT_1hour=Crypto_pair('BTCUSDT', '1h')
# BTC_USDT_4hour=Crypto_pair('BTCUSDT', '4h')
BTC_USDT_daily=Crypto_pair('BTCUSDT', '1d')

### ASSETS OR PAIRS THAT CAN BE USED TO TRADE
enabled_assets=[
                BTC_USDT_1minute,
                BTC_USDT_15min,
                BTC_USDT_1hour,
                # BTC_USDT_4hour,
                BTC_USDT_daily
                ]

############################################################################

def history():
    
    candlestick_lists = [
                    get_data.One_Minute_candlesticks,
                    get_data.MIN_15_candlesticks,
                    get_data.One_H_candlesticks, 
                    # get_data.Four_H_candlesticks, 
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
    i_registry.log('opened connection')
    i_registry.log(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))

def on_close(ws):
    i_registry.log('closed connection')

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
    
    def Trade_logic_as_per_selected_asset(asset_selected:Crypto_pair):
        ##################################################
        # PIECE OF CODE TO TEST ASSET LISTS AND VARIABLES
        # asset_selected=BTC_USDT_1minute
        ##################################################
        i_registry.log(">>>>>>>>>>>>>>> BOT VERSION : "+str(BOT_VERSION)+ " <<<<<<<<<<<<<<<")
        i_registry.log("BOT_LAST_CHANGE_DONE : "+str(BOT_LAST_CHANGE_DONE))
        i_registry.log(">>>> NEW CANDLE CLOSED @ {} <<<<".format(close))
        i_registry.log(">>>"+asset_selected.symbol+"<<<")
        i_registry.log(">>>"+asset_selected.interval+"<<<")
        i_registry.log(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
        # log("minimal change % " + str(params.Minimal_percentage_change*1/100))
        asset_selected.open_time.append(int(Time_open))
        asset_selected.open.append(float(open))
        asset_selected.high.append(float(high))
        asset_selected.low.append(float(low))
        asset_selected.close.append(float(close))
        asset_selected.volume.append(float(volume))
        
        i_registry.log("APPENDING SUCCESSFUL")
        
        all_indis_update(asset_selected)
        
        i_registry.operations=operations.All_Operations_Available(GLOBAL_SYMBOL=GLOBAL_SYMBOL, 
                                                                  account_info=account_info,
                                                                  enabled_assets=enabled_assets, 
                                                                  asset_selected=asset_selected, 
                                                                  params=params, 
                                                                  i_registry=i_registry)
        
        # i_registry.log("minimal change % " + str(params.Minimal_percentage_change*1/100))

        # SNIPPET TO ACTIVATE HIGH AND LOW SPIKE LISTS UPDATE
        
        i_registry.log("trying to update spikes! start")
        i_registry.signals=signals.Sample_Signals(asset_selected=asset_selected, i_registry=i_registry)
        
        # ACTIVATION OF BUY AND SELL SIGNALS FOR TOP AND BOTTOMS
        
        i_registry.buysignal=i_registry.signals.buy_signal()
        i_registry.log("BUY SIGNAL = "+str(i_registry.buysignal))
        
        i_registry.sellsignal=i_registry.signals.sell_signal()
        i_registry.log("SELL SIGNAL = "+str(i_registry.sellsignal))
        
        i_registry.log("Barrel")
        i_registry.log(asset_selected.Barrel)           
        
        ######################################################################################
        i_registry.last_total_cash=account_info.account_registry.Total_Cash()

        i_registry.long_position_now_qtty=account_info.account_registry.get_actual_position("amount")[0]
        i_registry.long_p_entry_price_now=account_info.account_registry.get_actual_position("entryprice")[0]
        # i_registry.long_unreal_profit=account_info.account_registry.get_actual_position("unreal_profit")[0]
        #(CALCULATED UNREAL LONG PROFIT)
        l_u_profit=i_registry.long_position_now_qtty*(asset_selected.close[-1]-i_registry.long_p_entry_price_now)
        l_u_profit=round(l_u_profit,ndigits=4)
        i_registry.long_unreal_profit=l_u_profit

        i_registry.short_position_now_qtty=account_info.account_registry.get_actual_position("amount")[-1]
        i_registry.short_p_entry_price_now=account_info.account_registry.get_actual_position("entryprice")[-1]
        # i_registry.short_unreal_profit=account_info.account_registry.get_actual_position("unreal_profit")[-1]
        #(CALCULATED UNREAL SHORT PROFIT)
        s_u_profit=abs(i_registry.short_position_now_qtty)*(i_registry.short_p_entry_price_now-asset_selected.close[-1])
        s_u_profit=round(s_u_profit,ndigits=4)
        i_registry.short_unreal_profit=s_u_profit
        
        i_registry.are_we_in_a_position()
        i_registry.total_unrealized_profit()
        i_registry.delta_calculation()
        i_registry.position_registry_repairer()
        i_registry.total_fees_to_open(fee_rate=params.fee_rate)
        i_registry.total_fees_to_close(price_to_evaluate=asset_selected.close[-1],fee_rate=params.fee_rate)
        i_registry.total_all_fees()
        
        i_registry.open_buy_orders=account_info.account_registry.open_orders("buy")
        i_registry.open_sell_orders=account_info.account_registry.open_orders("sell")

        n=1
        print("CONTROL "+str(n))
        n=n+1
        i_registry.buy_conditions=trade_conditions.Check_Buy_Conditions(GLOBAL_SYMBOL=GLOBAL_SYMBOL,
                                                                        asset_selected=asset_selected,
                                                                        enabled_assets=enabled_assets,
                                                                        params=params,
                                                                        i_registry=i_registry,
                                                                        buysignal=i_registry.buysignal,
                                                                        sellsignal=i_registry.sellsignal,
                                                                        Bull_trend_loss_signal=i_registry.Bull_trend_loss_signal)
        
        i_registry.sell_conditions=trade_conditions.Check_Sell_Conditions(GLOBAL_SYMBOL=GLOBAL_SYMBOL,
                                                                        asset_selected=asset_selected,
                                                                        enabled_assets=enabled_assets,
                                                                        params=params,
                                                                        i_registry=i_registry,
                                                                        sellsignal=i_registry.sellsignal,
                                                                        buysignal=i_registry.buysignal,
                                                                        Bear_trend_loss_signal=i_registry.Bear_trend_loss_signal)

                #    EXECUTION OF BUY OR SELL CONDITIONS
        print("CONTROL "+str(n))
        n=n+1
        def delta_destabilizer(buyfilter, sellfilter):
            # print("DELTA DESTAB START")
            if params.exit_by_goal=="fees":
                goal=(i_registry.total_fees_so_far+params.minimum_cash_profit)
            if params.exit_by_goal=="cash":
                goal=(params.minimum_cash_profit)
            
            i_registry.log("TOTAL LONG UNREALIZED = "+str(i_registry.long_unreal_profit))
            i_registry.log("TOTAL SHORT UNREALIZED = "+str(i_registry.short_unreal_profit))
            i_registry.log("TOTAL UNREALIZED = "+str(i_registry.total_unreal_profit))
            i_registry.log("WHAT IS THE GOAL RIGHT NOW? = "+str(goal))
            i_registry.log("TOTAL FEES IN AND OUT : "+str(i_registry.total_fees_so_far))
            
            if i_registry.total_unreal_profit>goal:
                i_registry.target_delta=params.control_target_delta
                i_registry.log("TOTAL UNREALIZED IS ABOVE GOAL")
            
            if buyfilter and i_registry.total_unreal_profit<goal:
                if params.delta_bias=="neutral":
                    i_registry.target_delta=params.max_delta
                if params.delta_bias=="negative":
                    i_registry.target_delta=params.control_target_delta
                if params.delta_bias=="positive":
                    i_registry.target_delta=params.max_delta
                i_registry.log("TOTAL UNREALIZED IS BELOW GOAL")
            
            if sellfilter and i_registry.total_unreal_profit<goal:
                negative_delta=(params.max_delta)*-1
                if params.delta_bias=="neutral":
                    i_registry.target_delta=negative_delta
                if params.delta_bias=="negative":
                    i_registry.target_delta=negative_delta
                if params.delta_bias=="positive":
                    i_registry.target_delta=params.control_target_delta
                i_registry.log("TOTAL UNREALIZED IS BELOW GOAL")
        # delta_destabilizer()
        #########################################################################################
        print("CONTROL "+str(n))
        n=n+1      
        asset_selected.asset_list_cleaner()
        print("CONTROL "+str(n))
        n=n+1
        i_registry.clean_positions_slate()
        buy_m_t_f=i_registry.buy_conditions.MACD_buy_filter()
        sell_m_t_f=i_registry.sell_conditions.MACD_sell_filter()
        delta_destabilizer( buyfilter=buy_m_t_f, sellfilter=sell_m_t_f)
        # ONLY EXECUTE TRADES IF INTERVAL IS 1 MINUTE
        for x in enabled_assets:
            if x.interval=='15m' and x.symbol==GLOBAL_SYMBOL:
                i_registry.log(">>>>> 15min Histogram: "+str(x.histogram_macd[-1]))
        if asset_selected.interval=='1m':
            print("CONTROL "+str(n))
            n=n+1
            i_registry.log("1 minute candle study start")
            i_registry.buy_conditions.abort_entering_buy_position()
            i_registry.sell_conditions.abort_entering_sell_position()
            print("CONTROL "+str(n))
            n=n+1
            i_registry.log("Finding if higher timeframes give a green light: (MACD_buy_filter function): "+str(buy_m_t_f))
            if buy_m_t_f:
                i_registry.buy_conditions.increase_buy_position()
                i_registry.log("increase_buy_position")
            print("CONTROL "+str(n))
            n=n+1
            
            i_registry.log("Finding if higher timeframes give a green light: (MACD_sell_filter function): "+str(sell_m_t_f))
            if sell_m_t_f:
                i_registry.sell_conditions.increase_sell_position()
                i_registry.log("increase_sell_position")
            print("CONTROL "+str(n))
            n=n+1
            i_registry.buy_conditions.exit_buy_position()
            i_registry.sell_conditions.exit_sell_position()
            print("CONTROL "+str(n))
            n=n+1
            if True:#buy_m_t_f:
                i_registry.buy_conditions.enter_buy_position()
            print("CONTROL "+str(n))
            n=n+1
            if True:#sell_m_t_f:
                i_registry.sell_conditions.enter_sell_position()
            
            i_registry.log("LONG POSITION SIZE RIGHT NOW: "+str(i_registry.long_position_now_qtty))
            i_registry.log("SHORT POSITION SIZE RIGHT NOW: "+str(i_registry.short_position_now_qtty))
            i_registry.log("CURRENT DELTA: "+str(i_registry.current_delta))
            i_registry.log("TARGET DELTA: "+str(i_registry.target_delta))
            i_registry.log("1 MINUTE ASSET CLOSE LENGHT OF LIST: "+str(len(asset_selected.close)))
            # i_registry.log("OLDEST 1 MINUTE OPENING TIME: "+str(datetime.fromtimestamp(asset_selected.open_time[0])))
            # i_registry.log("OLDEST 1 MINUTE CLOSING PRICE: "+str(asset_selected.close[0]))
        
        ############################################################################################
    
    
    for x in enabled_assets:
        if is_candle_closed and message_symbol==x.symbol and message_interval==x.interval:
                z=x
                try:
                    Trade_logic_as_per_selected_asset(z)
                except Exception as e:
                    print(e)
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


                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_message=on_message) #on_close=on_close,

def Keep_alive_websocket():
    ws.close()
    kaw_message=">>>>>Websocket client restarted!!!!! "
    print(kaw_message)
    print(kaw_message)
    print(kaw_message)
    i_registry.log(kaw_message)
    i_registry.log(kaw_message)
    i_registry.log(kaw_message)
    i_registry.log2(kaw_message)
    i_registry.log2(kaw_message)
    i_registry.log2(kaw_message)   
    ws.run_forever(ping_interval=30)

rt_websocket = RepeatedTimer2(60*60*23, Keep_alive_websocket) # it auto-starts, no need of rt.start()

ws.run_forever(ping_interval=30)

