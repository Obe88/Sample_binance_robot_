import logging
from types import SimpleNamespace
import input_config
from binance_f import RequestClient
from binance_f import SubscriptionClient
from binance_f.constant.test import *
from binance_f.model import *  
from binance_f.exception.binanceapiexception import BinanceApiException

from binance_f.base.printobject import *

import threading 
import time
from time import sleep

import types



server_url=input_config.server_url
APIK=input_config.APIK
APIS=input_config.APIS
GLOBAL_SYMBOL=input_config.GLOBAL_SYMBOL
BASE=input_config.BASE
print("PRINTING CONNECTION PARAMETERS")
print(BASE)
print(server_url)

############################################################################
# Start user data stream
client = RequestClient(api_key=APIK, secret_key=APIS, url=server_url)
listen_key = client.start_user_data_stream()
print("listenKey: ", listen_key)

# Keep user data stream
result = client.keep_user_data_stream()
print("Result: ", result)

logger = logging.getLogger("binance-client")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

uri_address=BASE+"/ws/"+listen_key 
# uri_address="wss://fstream.binance.com/ws/"+listen_key### REAL FUTURES ACCOUNT LISTENING STREAM
# uri_address="wss://stream.binancefuture.com/ws/"+listen_key
sub_client = SubscriptionClient(api_key=APIK, secret_key=APIS, uri=uri_address, is_auto_connect=True, receive_limit_ms=60*60*1000)

class account_empty_registry(object):
    def __init__(self):
        self.Has_user_stream_updated_balance=False
        
        self.balance_by_stream=0.0        
        
        self.Has_user_stream_updated_positions=False
        
        self.long_position_object_by_stream=SimpleNamespace()
        self.short_position_object_by_stream=SimpleNamespace()
        
        self.is_quantity_of_trades_updated=False
        
        self.o_orders=[]

        self.global_balance=[]

        self.long_position_object_by_request=SimpleNamespace()
        self.short_position_object_by_request=SimpleNamespace()
        # self.args = args

    def change_leverage_until_no_error(self,tries=1):   
        try:
            client.change_initial_leverage(symbol=GLOBAL_SYMBOL, leverage=10)
        except Exception as excep :
            print(excep)
            if tries<3:
                print("Trying to change leverage again... TRY NUMBER= "+str(tries))
                sleep(3*tries)
                self.change_leverage_until_no_error(tries+1)
            else:
                print("LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE")
                print("WARNING WARNING WARNING! FAILED to change leverage!!!")
                print("WARNING WARNING WARNING! FAILED to change leverage!!!")
                print("LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE LEVERAGE")
            pass
    
    def Starting_Cash(self):
        if  self.Has_user_stream_updated_balance == False:
            balance_object=client.get_balance_v2()
            for x in balance_object:
                if x.asset=="USDT":
                    self.global_balance = x
    
    def Total_Cash(self):
        if  self.Has_user_stream_updated_balance == False:
            Total_cash_in_account=float(self.global_balance.balance) #global_balance[1] is USDT asset [0] is BNB [2] is BUSD
            # PrintMix.print_data(Total_cash_in_account)
        else:
            Total_cash_in_account=self.balance_by_stream
        return Total_cash_in_account    

############################################################################################################################################################    
###----------------------------------------------------------------------ORDERS--------------------------------------------------------------------------###
############################################################################################################################################################ 
    def get_open_orders_until_no_error(self, tries=1):   
        try:
            self.o_orders=client.get_open_orders(symbol=GLOBAL_SYMBOL)
            self.is_quantity_of_trades_updated=True
            # return self.o_orders
        except Exception as excep :
            print(excep)
            if tries<=5:
                print("Trying to fetch orders again... TRY NUMBER= "+str(tries))
                sleep(5*tries)
                self.get_open_orders_until_no_error(tries+1)
            else:
                print("********==========______________==========********")
                print("WARNING WARNING WARNING! FAILED to fetch orders!!!")
                print("WARNING WARNING WARNING! FAILED to fetch orders!!!")
                print("WARNING WARNING WARNING! FAILED to fetch orders!!!")
                self.o_orders=[false_order]
                print("WARNING WARNING WARNING! FALSE ORDER ACTIVATED")
                print("WARNING WARNING WARNING! FALSE ORDER ACTIVATED")
                print("WARNING WARNING WARNING! FALSE ORDER ACTIVATED")
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                # return self.o_orders
            pass

    # def trades_updated_to_false():
    #     account_registry.is_quantity_of_trades_updated=False
    
    def open_orders(self, side="buy"):
        if self.is_quantity_of_trades_updated:
            self.get_open_orders_until_no_error()
        i=0
        if side=="buy":
            for x   in  self.o_orders:
                if  x.symbol==GLOBAL_SYMBOL and x.side=="BUY":
                    i+=1
        elif side=="sell":
            for x   in  self.o_orders:
                if  x.symbol==GLOBAL_SYMBOL and x.side=="SELL":
                    i+=1
        print ("--->>>Number of open "+side+" Orders: "+str(i))
        self.is_quantity_of_trades_updated=False
        # Orders.trades_updated_to_false()
        return i

############################################################################################################################################################    
###---------------------------------------------------------------------POSITION-------------------------------------------------------------------------###
############################################################################################################################################################ 
    
    def request_position_object(self):
        result = client.get_position()
        for x in result:
            if x.positionSide=='LONG' and x.symbol==GLOBAL_SYMBOL:
                self.long_position_object_by_request=x
                # long_pos_amount=x.positionAmt
                # long_unreal_profit=x.unrealizedProfit
                break
        for y in result:
            if y.positionSide=='SHORT' and y.symbol==GLOBAL_SYMBOL:
                self.short_position_object_by_request=y
                # short_pos_amount=y.positionAmt
                # short_unreal_profit=y.unrealizedProfit
                break    

    def get_actual_position(self,quality="amount"):
        if  self.Has_user_stream_updated_positions == False:
            if quality=="amount":
                return [self.long_position_object_by_request.positionAmt,self.short_position_object_by_request.positionAmt]
            if quality=="entryprice":
                return [self.long_position_object_by_request.entryPrice,self.short_position_object_by_request.entryPrice]
            if quality=="leverage":
                return [self.long_position_object_by_request.leverage,self.short_position_object_by_request.leverage]
            if quality=="unreal_profit":
                return [self.long_position_object_by_request.unrealizedProfit,self.short_position_object_by_request.unrealizedProfit]
        else:
            if quality=="amount":
                return [self.long_position_object_by_stream.amount,self.short_position_object_by_stream.amount]
            if quality=="entryprice":
                return [self.long_position_object_by_stream.entryPrice,self.short_position_object_by_stream.entryPrice]
            if quality=="leverage":
                return [self.long_position_object_by_request.leverage,self.short_position_object_by_request.leverage]
            if quality=="unreal_profit":
                return [self.long_position_object_by_stream.unrealizedPnl,self.short_position_object_by_stream.unrealizedPnl]

account_registry=account_empty_registry()
account_registry.change_leverage_until_no_error()
account_registry.get_open_orders_until_no_error()
account_registry.Starting_Cash() 
account_registry.request_position_object()        

class false_order_class(object):
    def __init__(self, symbol=GLOBAL_SYMBOL, side="BUY"):
        self.symbol=symbol
        self.side=side
false_order=false_order_class(symbol=GLOBAL_SYMBOL, side="BUY")

def callback(data_type: 'SubscribeMessageType', event: 'any'):
    
    if data_type == SubscribeMessageType.RESPONSE:
        print("Event type: ", (event))
    elif  data_type == SubscribeMessageType.PAYLOAD:
        if(event.eventType == "ACCOUNT_UPDATE"):
            print("  ")
            print("========++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++========")
            print("=== Balances ===")
            print("Event time: ", event.eventTime)
            # PrintMix.print_data(event.balances)
            account_registry.balance_by_stream=event.balances[-1].crossWallet
            print("BALANCE BY STREAM: ", str(account_registry.balance_by_stream))
            account_registry.Has_user_stream_updated_balance=True
            print("Has_user_stream_updated_balance VARIABLE", str(account_registry.Has_user_stream_updated_balance))
            print("crossWallet USDT: ", account_registry.balance_by_stream)
            print("================")
            
            if event.positions is not None:
                print("=== Positions ===")
                # PrintMix.print_data(event.positions)
                print("========+++++++++++++++++++++++++++++++========")
                print("Event time: ", event.eventTime)
                try:
                    for x in event.positions:
                        if str(x.symbol)==GLOBAL_SYMBOL and x.positionSide=="LONG":
                            account_registry.long_position_object_by_stream=x
                            print("Long Position Symbol: ",x.symbol)
                            print("Long Position Amount: ", x.amount)
                            print("Long Position Entry Price: ", x.entryPrice)
                            print("Long Position unrealizedPnl: ",x.unrealizedPnl)
                            break
                    print("  ")
                    for y in event.positions:
                        if str(y.symbol)==GLOBAL_SYMBOL and y.positionSide=="SHORT":
                            account_registry.short_position_object_by_stream=y
                            print("Short Position Symbol: ",y.symbol)
                            print("Short Position Amount: ", y.amount)
                            print("Short Position Entry Price: ", y.entryPrice)
                            print("Long Position unrealizedPnl: ",y.unrealizedPnl)
                            break
                    account_registry.Has_user_stream_updated_positions=True
                except Exception as e:
                    print(e)
                account_registry.get_actual_position()
                print("========+++++++++++++++++++++++++++++++========+++++++++++++++++++++++++")

        elif(event.eventType == "ORDER_TRADE_UPDATE"):
            account_registry.is_quantity_of_trades_updated=True
            print("Event time: ", event.eventTime)
            print("Client Order Id: ", event.clientOrderId)
            print("Order Type: ", event.type)
            print("Side: ", event.side)
            print("Original Quantity: ", event.origQty)
            print("Symbol: ", event.symbol)
            print("Average Price: ", event.avgPrice)
            print("Stop Price: ", event.stopPrice)
            print("Is this Close-All: ", event.isClosePosition)
            print("Order Id: ", event.orderId)
            print("================")
            print("Order Status: ", event.orderStatus)

            ### PROBABLY NEEDED IN THE FUTURE
            print("================")
            print("Commission Asset: ", event.commissionAsset)
            print("Commissions: ", event.commissionAmount)

            ### NOT NEEDED RIGHT NOW
            # # 
            # # print("Time in Force: ", event.timeInForce)
            
            # # print("Execution Type: ", event.executionType)
            # # print("Order Last Filled Quantity: ", event.lastFilledQty)
            # # print("Order Filled Accumulated Quantity: ", event.cumulativeFilledQty)
            # # print("Last Filled Price: ", event.lastFilledPrice)
            
            # # print("Is this reduce only: ", event.isReduceOnly)
            # # print("stop price working type: ", event.workingType)
            # # 
            
            if not event.activationPrice is None:
                print("Activation Price for Trailing Stop: ", event.activationPrice)
            if not event.callbackRate is None:
                print("Callback Rate for Trailing Stop: ", event.callbackRate)
        
        elif(event.eventType == "listenKeyExpired"):
            print("Event: ", event.eventType)
            print("Event time: ", event.eventTime)
            print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
            print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
            print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
    else:
        print("Unknown Data:")
    # print()

def error(e: 'BinanceApiException'):
    print(e.error_code + e.error_message)

sub_client.subscribe_user_data_event(listen_key, callback, error)

class RepeatedTimer(object):
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

def Keep_alive_client():
    result = client.keep_user_data_stream()
    print("Result: ", result)   

rt = RepeatedTimer(60*30, Keep_alive_client) # it auto-starts, no need of rt.start()
# rt2= RepeatedTimer(10,Orders.open_orders)
