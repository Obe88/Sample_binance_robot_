# sample_binance_robot_private_230522

Hello and welcome to my overly complicated Binance cex trading bot, before stating my explanation for all this bunch of published code first know this:

THIS IS AN UNTESTED UNSAFE TRADING BOT PUBLISHED FOR THE SOLE PURPOSE OF SHOWING/PREVIEWING WHAT CAN I DO/CODE WITH PYTHON,
I DO NOT RECOMMEND IN ANY SHAPE, WAY OR FORM IN USING THIS FOR TRADING IN FINANTIAL MARKETS OF ANY KIND, USE THIS AT YOUR OWN RISK, 
THE USE OF THIS BOT WILL LIKELY PRODUCE HEAVY MONETARY LOSSES AND I AM NOT RESPONSIBLE FOR THE NEGATIVE OR POSITIVE RETURNS OR RESULTS IT MAY YIELD, USE THIS AT YOUR OWN RISK,
I AM NOT A FINANTIAL ADVISOR OF ANY KIND, USE THIS AT YOUR OWN RISK.

Having said all that we can continue.

This is my sample trading robot which can operate in Binance Futures testnet as well as livenet (or realnet as i call it), 
to operate in any of these nets you need the API key and secret for your trading account, to operate in testnet as an example you have to go to https://testnet.binancefuture.com/en/futures/BTCUSDT,
create an account and then surf to the BTCUSDT perpetual futures and look for the API Key tab below the candlestick/prices chart, copy those keys and paste them in the input_config.py file,
this will give full access and control so that the bot can extract your account information and buy/sell perpetual leveraged contracts automatically in your account (as if it was you yourself doing it),
this means you need to always keep your keys secure and secret at all times as losing or sharing these would result in you losing ALL your funds.

The bot was built using https://binance-docs.github.io/apidocs/futures/en/#change-log API documentation written by Binance for the use of it's API, 
Python SDK https://github.com/Binance-docs/Binance_Futures_python which seems to me will be deprecated soon for the new Python connector https://github.com/binance/binance-futures-connector-python,
and Python libraries numpy, tulipy and websocket_client, all of which can be installed via pip, it's important to note however that **the bot needs Python version 3.7.6 or it will not work** 
"why?" you may ask, well because numpy can only operate with certain versions of Python and this one is the one i found which is compatible with the rest of the libraries and the SDK.
**You need these libraries installed for it to work**, i guess you could edit the code so that the bot doesn't need these libraries but because i built it with the purpose of trading with technical indicators (technical analysis)
you would need these libraries so it can trade as it normally would. 
I used tulipy instead of TAlib because TAlib is a pain to install and couldn't reproduce the installation when tried to operate the bot in a cloud linux VM as i usually code in a windows OS, so there, tulipy.

The bot was built and operates with the idea of mixing two pillars of information, the price action and historical information (open time, open price, high, low, close price and volume), 
and the account information extracted with your keys that allows to get all types of data (account leverage, account hedge mode or one way mode, 
isolated positions or cross, open positions, open orders, historical/closed orders, assets balance, etc).

Firstly, the bot attempts to gather all the data needed from your account, leverage number, account balance, open positions right now, open orders right now. Followed by connecting to your own account websocket data stream so it can keep itself updated with any changes in your account in real time.
Secondly, the bot gathers the historical data of the asset pair (which is hardcoded as "BTCUSDT" as i have only used this pair) that is time, open, high, low, close and volume. And then attempts to connect to the websocket price data feed/stream so everytime there is a change in the data of the asset pair
(any price tick) it gets automatically updated in the asset pair Python object attribute created to store all this information.
As soon as the bot receives the update that the last price tick is a closing data point it appends all this data to the object attribute list to form a list of values which can be used as a means to evaluate whether the price action is telling us (or the bot perse) that is a good time to enter or exit a position.

