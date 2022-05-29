
# import operations

############################################################################################
class   Check_Buy_Conditions(object):
    def __init__(self, GLOBAL_SYMBOL, asset_selected, enabled_assets, params,
                i_registry, buysignal,sellsignal,Bull_trend_loss_signal) -> None:
        
        self.GLOBAL_SYMBOL=GLOBAL_SYMBOL
        
        self.asset_selected=asset_selected
        self.enabled_assets=enabled_assets
        
        self.params=params

        self.i_registry=i_registry
        self.buysignal=buysignal
        self.sellsignal=sellsignal
        self.Bull_trend_loss_signal=Bull_trend_loss_signal

    def enter_buy_position(self):  # CONDITIONS
    # Check if we are in the market
    # ENTER FIRST BUY POSITION
        try:
            if self.i_registry.in_a_long_position == False and  self.i_registry.open_buy_orders == 0:
                self.i_registry.log2("Standard buy condition 1 true")
                
                ### TO BUY
                if  self.buysignal:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.i_registry.log("Standard Buy")
                    self.i_registry.log2("Standard Buy")
                    self.i_registry.is_secure_profit_order_on=False
                    self.i_registry.operations.Global_Buy_operation()
            else:
                self.i_registry.log2("VALUES WHY ENTER BUY FUNCTION IS NOT PASSING: ")
                self.i_registry.log2("self.i_registry.in_a_long_position: "+ str(self.i_registry.in_a_long_position))
                self.i_registry.log2("self.i_registry.open_buy_orders: "+ str(self.i_registry.open_buy_orders))
                
        except Exception as e:
            self.i_registry.log(e)

    def increase_buy_position(self):  # CONDITIONS
    # Check if we are in the market
    # INCREASE POSITION SIZE BY BUYING
    ### TO BUY
        try:
            price_diff=float(self.i_registry.long_p_entry_price_now-self.asset_selected.close[-1])
            price_diff=round(price_diff,ndigits=1)
            for z in self.enabled_assets:
                if z.interval=='1h'and z.symbol==self.asset_selected.symbol:
                    minimal_price_diff=z.atr[-1]/2#in reserve

            if self.i_registry.in_a_long_position == True and self.i_registry.long_position_now_qtty > 0.0: 
                if self.i_registry.open_buy_orders == 0 and self.i_registry.long_position_now_qtty<self.params.position_upper_limit:
                    self.i_registry.log2("increase buy condition 1 True")
                    
                    if price_diff>self.params.minimal_price_diff_to_enter and self.i_registry.current_delta<self.i_registry.target_delta:
                        self.i_registry.log2("increase buy condition 2 True")
                        ### TO BUY
                        if  self.buysignal:
                            # BUY, BUY, BUY!!! (with all possible default parameters)
                            self.i_registry.log("Standard Buy")
                            self.i_registry.log2("Standard Buy")
                            self.i_registry.operations.Global_Buy_operation()
            else:
                self.i_registry.log2("VALUES WHY INCREASE BUY FUNCTION IS NOT PASSING: ")
                self.i_registry.log2("self.i_registry.in_a_long_position: "+ str(self.i_registry.in_a_long_position))
                self.i_registry.log2("self.i_registry.long_position_now_qtty: "+ str(self.i_registry.long_position_now_qtty))
                self.i_registry.log2("self.i_registry.open_buy_orders: "+ str(self.i_registry.open_buy_orders))
                self.i_registry.log2("self.params.position_upper_limit: "+ str(self.params.position_upper_limit))
                self.i_registry.log2("price_diff: "+ str(price_diff))
                self.i_registry.log2("self.params.minimal_price_diff_to_enter: "+ str(self.params.minimal_price_diff_to_enter))
                self.i_registry.log2("self.i_registry.current_delta: "+ str(self.i_registry.current_delta))
                self.i_registry.log2("self.i_registry.target_delta: "+ str(self.i_registry.target_delta))

        except Exception as e:
            self.i_registry.log(e)                                                        

    def exit_buy_position(self):  # CONDITIONS  
        #   IT'S A SELL
        ### CLOSE ACTIVE BUY POSITION BY SELLING
        try:
            self.i_registry.log2("exit_buy_position function start")
            if self.i_registry.in_a_long_position == True and \
            self.i_registry.long_position_now_qtty > 0.0 and \
            self.i_registry.open_sell_orders == 0:
                #IF PASSES ENTER THIS:
                self.i_registry.log2("exit condition 1 true") 
                self.i_registry.log2(self.asset_selected.close[-1])
                
                def minimal_exit_price():
                    for z in self.enabled_assets:
                            if z.interval=='1h'and z.symbol==self.asset_selected.symbol:
                                minimal_price_diff=z.atr[-1]/2#in reserve
                    minimal_exit_price=self.i_registry.long_p_entry_price_now+(minimal_price_diff)
                    return minimal_exit_price
                mep=minimal_exit_price()

                def defining_goal():
                    if self.params.exit_by_goal=="fees":
                        goal=(self.i_registry.total_fees_so_far+self.params.minimum_cash_profit)
                    else:
                        goal=(self.params.minimum_cash_profit)
                    return goal
                goal=defining_goal()

                self.i_registry.log2(mep)
                
                # if self.asset_selected.close[-1]>mep and self.i_registry.total_unreal_profit>goal:
                if self.i_registry.total_unreal_profit>goal and self.i_registry.long_unreal_profit>self.i_registry.short_unreal_profit:
                    self.i_registry.log2("exit condition 2 true")
                    # if self.sellsignal or self.Bull_trend_loss_signal:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.i_registry.log2("trying to cancel and close starting...")
                    self.i_registry.operations.cancel_all_orders()
                    self.i_registry.operations.close_active_position()
                    self.i_registry.log('SELL-CLOSE CREATE @ PRICE, %.2f' % self.asset_selected.close[-1])
        except Exception as e:
            self.i_registry.log(e)
    
    def abort_entering_buy_position(self):  # CONDITIONS
    # Check if we are in the market
    # ABORT ENTRY OF FIRST BUY POSITION
        try:
            if self.i_registry.in_a_long_position == False and  self.i_registry.open_buy_orders > 0:
                self.i_registry.log2("ABORT buy condition 1 true")
                
                ### TO ABORT BUY
                if  self.sellsignal:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.i_registry.log("ABORTING Buy")
                    self.i_registry.log2("ABORTING Buy")
                    self.i_registry.operations.cancel_all_orders()
        except Exception as e:
            self.i_registry.log(e)

    def MACD_buy_filter(self) -> bool: # CONDITIONS
        try:
            for x in self.enabled_assets:
                if x.interval=='15m' and x.symbol==self.asset_selected.symbol:
                    if x.histogram_macd[-1]<0:
                        self.i_registry.log2(x.symbol+' in '+x.interval+' candles is MACD bullish')
                        return True

                            # for z in self.enabled_assets:
                            #     if z.interval=='1m'and len(z.Barrel)>=1 and z.symbol==self.asset_selected.symbol:
                            #         # if z.Barrel[-2]=='Bottom' and z.Barrel[-1]=='Bottom':
                            #         if z.Barrel[-1]=='Bottom':
                            #             self.i_registry.log2(z.symbol+' in '+z.interval+' candles is showing at least 1 bottoms in the barrel')
                            #             return True
            else:
                return False
        except Exception as e:
            self.i_registry.log(e)

############################################################################################
class   Check_Sell_Conditions(object):
    def __init__(self, GLOBAL_SYMBOL, asset_selected, enabled_assets, params,
                i_registry, sellsignal, buysignal, Bear_trend_loss_signal) -> None:
        
        self.GLOBAL_SYMBOL=GLOBAL_SYMBOL
        
        self.asset_selected=asset_selected
        self.enabled_assets=enabled_assets
        
        self.params=params

        self.i_registry=i_registry
        self.sellsignal=sellsignal
        self.buysignal=buysignal
        self.Bear_trend_loss_signal=Bear_trend_loss_signal

    def enter_sell_position(self):  # CONDITIONS
    # Check if we are in the market
    # ENTER FIRST SELL POSITION
        try:
            if self.i_registry.in_a_short_position == False and  self.i_registry.open_sell_orders == 0:
                self.i_registry.log2("Standard sell condition 1 true")
                
                ### TO SELL
                if  self.sellsignal:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.i_registry.log("Standard Sell")
                    self.i_registry.log2("Standard Sell")
                    self.i_registry.is_secure_profit_order_on=False
                    self.i_registry.operations.Global_Sell_operation()
            else:
                self.i_registry.log2("VALUES WHY ENTER SELL FUNCTION IS NOT PASSING: ")
                self.i_registry.log2("self.i_registry.in_a_short_position: "+ str(self.i_registry.in_a_short_position))
                self.i_registry.log2("self.i_registry.open_sell_orders: "+ str(self.i_registry.open_sell_orders))
                
        except Exception as e:
            self.i_registry.log(e)               

    def increase_sell_position(self):  # CONDITIONS
    # Check if we are in the market
    # INCREASE POSITION SIZE BY SELLING
    ### TO SELL
        try:
            price_diff=float(self.i_registry.short_p_entry_price_now-self.asset_selected.close[-1])
            price_diff=round(price_diff,ndigits=1)                
            for z in self.enabled_assets:
                if z.interval=='1h'and z.symbol==self.asset_selected.symbol:
                    minimal_price_diff=z.atr[-1]/2#in reserve

            if self.i_registry.in_a_short_position == True and self.i_registry.short_position_now_qtty < 0.0: 
                if self.i_registry.open_sell_orders == 0 and abs(self.i_registry.short_position_now_qtty)<self.params.position_upper_limit:
                    self.i_registry.log("increase sell condition 1 True")
                    
                    if price_diff<self.params.minimal_price_diff_to_enter*-1 and self.i_registry.current_delta>self.i_registry.target_delta:
                        self.i_registry.log("increase sell condition 2 True")
                        ### TO SELL
                        if  self.sellsignal:
                            # SELL, SELL, SELL!!! (with all possible default parameters)
                            self.i_registry.log("Standard Sell")
                            self.i_registry.log2("Standard Sell")
                            self.i_registry.operations.Global_Sell_operation()
            else:
                self.i_registry.log2("VALUES WHY INCREASE SELL FUNCTION IS NOT PASSING: ")
                self.i_registry.log2("self.i_registry.in_a_short_position: "+ str(self.i_registry.in_a_short_position))
                self.i_registry.log2("self.i_registry.short_position_now_qtty: "+ str(self.i_registry.short_position_now_qtty))
                self.i_registry.log2("self.i_registry.open_sell_orders: "+ str(self.i_registry.open_sell_orders))
                self.i_registry.log2("self.params.position_upper_limit: "+ str(self.params.position_upper_limit))
                self.i_registry.log2("price_diff: "+ str(price_diff))
                self.i_registry.log2("self.params.minimal_price_diff_to_enter: "+ str(self.params.minimal_price_diff_to_enter))
                self.i_registry.log2("self.i_registry.current_delta: "+ str(self.i_registry.current_delta))
                self.i_registry.log2("self.i_registry.target_delta: "+ str(self.i_registry.target_delta))

        except Exception as e:
            self.i_registry.log(e)

    def exit_sell_position(self):  # CONDITIONS  
        #   IT'S A BUY
        ### CLOSE ACTIVE SELL POSITION BY BUYING
        try:
            self.i_registry.log2("exit_sell_position function start")
            if self.i_registry.in_a_short_position == True and \
            self.i_registry.short_position_now_qtty < 0.0 and\
            self.i_registry.open_buy_orders == 0:
            
                #IF PASSES ENTER THIS:
                self.i_registry.log2("exit condition 1 true") 
                self.i_registry.log2(self.asset_selected.close[-1])
                
                def minimal_exit_price():
                    for z in self.enabled_assets:
                            if z.interval=='1h'and z.symbol==self.asset_selected.symbol:
                                minimal_price_diff=z.atr[-1]/2#in reserve
                    minimal_exit_price=self.i_registry.short_p_entry_price_now-(minimal_price_diff)
                    return minimal_exit_price
                mep=minimal_exit_price()

                def defining_goal():
                    if self.params.exit_by_goal=="fees":
                        goal=(self.i_registry.total_fees_so_far+self.params.minimum_cash_profit)
                    else:
                        goal=(self.params.minimum_cash_profit)
                    return goal
                goal=defining_goal()

                self.i_registry.log2(mep)
                
                # if self.asset_selected.close[-1]<mep and self.i_registry.total_unreal_profit>goal:
                if self.i_registry.total_unreal_profit>goal and self.i_registry.short_unreal_profit>self.i_registry.long_unreal_profit:
                    self.i_registry.log2("exit condition 2 true")
                    # if self.buysignal or self.Bear_trend_loss_signal:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.i_registry.log2("trying to cancel and close starting...")
                    self.i_registry.operations.cancel_all_orders()
                    self.i_registry.operations.close_active_position()
                    self.i_registry.log('SELL-CLOSE CREATE @ PRICE, %.2f' % self.asset_selected.close[-1])
        except Exception as e:
            self.i_registry.log(e)
    
    def abort_entering_sell_position(self):  # CONDITIONS
    # Check if we are in the market
    # ABORT ENTRY OF FIRST SELL POSITION
        try:
            if self.i_registry.in_a_short_position == False and  self.i_registry.open_sell_orders > 0:
                self.i_registry.log2("ABORT sell condition 1 true")
                
                ### TO ABORT BUY
                if  self.buysignal:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.i_registry.log("ABORTING Sell")
                    self.i_registry.log2("ABORTING Sell")        
                    self.i_registry.operations.cancel_all_orders()
        except Exception as e:
            self.i_registry.log(e)                    

    def MACD_sell_filter(self) -> bool: # CONDITIONS
        try:
            for x in self.enabled_assets:
                if x.interval=='15m' and x.symbol==self.asset_selected.symbol:
                    if x.histogram_macd[-1]>0:
                        self.i_registry.log2(x.symbol+' in '+x.interval+' candles is MACD bearish')
                        return True

                            # for z in self.enabled_assets:
                            #     if z.interval=='1m'and len(z.Barrel)>=1 and z.symbol==self.asset_selected.symbol:
                            #         # if z.Barrel[-2]=='Top' and z.Barrel[-1]=='Top':
                            #         if z.Barrel[-1]=='Top':
                            #             self.i_registry.log2(z.symbol+' in '+z.interval+' candles is showing at least 1 top in the barrel')
                            #             return True
            else:
                return False
        except Exception as e:
            self.i_registry.log(e)                    
############################################################################################

### RESERVE
# IF 1D AND 4H AND 1H ASSET SHOWS TWO BOTTOMS IN A ROW RETURN TRUE/GREEN LIGHT TO TRADE
        # for x in self.enabled_assets:
        #     if x.interval=='1d' and len(x.Barrel)>=2 and x.symbol==self.asset_selected.symbol:
        #         if x.Barrel[-1]=='Bottom' and x.Barrel[-2]=='Bottom':
        #             self.i_registry.log2(x.symbol+' in '+x.interval+' candles is showing 2 bottoms in the barrel')
                    
        #             for y in self.enabled_assets:
        #                 if y.interval=='4h' and len(y.Barrel)>=2 and y.symbol==self.asset_selected.symbol:
        #                     if y.Barrel[-1]=='Bottom' and y.Barrel[-2]=='Bottom':
        #                         self.i_registry.log2(y.symbol+' in '+y.interval+' candles is showing 2 bottoms in the barrel')
                            
        #                         for z in self.enabled_assets:
        #                             if z.interval=='1h' and len(z.Barrel)>=2 and z.symbol==self.asset_selected.symbol:
        #                                 if z.Barrel[-1]=='Bottom' and z.Barrel[-2]=='Bottom':
        #                                     self.i_registry.log2(z.symbol+' in '+z.interval+' candles is showing 2 bottoms in the barrel')
        #                                     return True