### ACCOUNT INPUT CONFIGURATION

trading_account="TEST_FUTURES"
GLOBAL_SYMBOL='BTCUSDT'

###########################################################################
symbol_name=GLOBAL_SYMBOL.lower()

###########################################################################
if trading_account=="REAL_FUTURES":
    ### REAL FUTURES ACCOUNT LISTENING KEYS
    APIK='YOUR REAL FUTURES ACCOUNT APIK HERE'
    APIS='YOUR REAL FUTURES ACCOUNT APIS HERE'
    ## HTTP BASE ENDPOINTS
    server_url='https://fapi.binance.com' #BINANCE REAL/LIVE FUTURES
    ## WEBSOCKET
    BASE="wss://fstream.binance.com"#BASE_FUTURES_REAL

###########################################################################
elif trading_account=="TEST_FUTURES":
    ## TEST FUTURES ACCOUNT LISTENING KEYS
    APIK='YOUR TEST FUTURES ACCOUNT APIK HERE'
    APIS='YOUR TEST FUTURES ACCOUNT APIS HERE'
    ## HTTP BASE ENDPOINTS
    server_url='https://testnet.binancefuture.com' #BINANCE TESTNET FUTURES
    ## WEBSOCKET
    BASE="wss://stream.binancefuture.com"#BASE_FUTURES_TESTNET

###########################################################################
# elif trading_account=="REAL_SPOT": ### SPOT TRADING IS DONE VIA BINANCE CONNECTOR, THIS IS NOT THE SAME API <---------
#     ### REAL SPOT ACCOUNT LISTENING KEYS
#     APIK='YOUR REAL SPOT ACCOUNT APIK HERE'
#     APIS='YOUR REAL SPOT ACCOUNT APIS HERE'
#     ## HTTP BASE ENDPOINTS
#     server_url="https://api.binance.com"#BINANCE REAL/LIVE SPOT
#     ## WEBSOCKET
#     BASE="wss://stream.binance.com:9443"#BASE_SPOT_REAL

###########################################################################
elif trading_account=="HISTORY_DATA_TEST":
    ### REAL FUTURES ACCOUNT LISTENING KEYS
    APIK=None
    APIS=None
    ## HTTP BASE ENDPOINTS
    server_url='https://fapi.binance.com' #BINANCE REAL/LIVE FUTURES
    ## WEBSOCKET
    BASE="wss://fstream.binance.com"#BASE_FUTURES_REAL

# STREAM = "/ws/"+symbol_name+"@kline_1m"
# STREAM = "/stream?streams="+symbol_name+"@kline_1m/"+symbol_name+"@kline_1h/"+symbol_name+"@kline_4h/"+symbol_name+"@kline_1d" ### BINANCE FUTURES
STREAM = "/stream?streams="+symbol_name+"@kline_1m/"+symbol_name+"@kline_15m/"+symbol_name+"@kline_1h/"+symbol_name+"@kline_1d" ### BINANCE FUTURES

SOCKET = BASE+STREAM