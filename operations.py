import datetime
from datetime import datetime
# import account_info

class All_Operations_Available(object):
    def __init__(self, GLOBAL_SYMBOL, account_info, enabled_assets, asset_selected, params, i_registry, increment_factor=1.0) -> None:
        
        self.GLOBAL_SYMBOL=GLOBAL_SYMBOL
        self.account_info=account_info
        self.enabled_assets=enabled_assets
        self.asset_selected=asset_selected
        
        self.params=params
        
        self.i_registry=i_registry
        
        # self.increment_factor=increment_factor
    ###############################################################################################
    def Global_Sell_operation(self, increment_factor=1.0) -> None:  # MAIN OPERATION
        # ACTUAL EXECUTION OF TRAIL SELL ORDER USED TO ENTER SHORT/SELL POSITIONS
        try:
            def position_size_calculation() -> float:
                position_now_qtty=abs(self.i_registry.short_position_now_qtty)

                Cash_to_risk=self.i_registry.last_total_cash*self.params.percentage_to_risk/100

                if increment_factor>1.0:
                    PositionSize=float(increment_factor)*float(self.i_registry.Pos_Sizing_Reg[-1])
                else:
                    PositionSize=self.params.granularity*Cash_to_risk    #<<<--- GRANULARITY DETERMINES THE FIRST POSITION SIZE

                if  PositionSize>self.params.position_upper_limit-position_now_qtty:
                    PositionSize=self.params.position_upper_limit-position_now_qtty
                
                if  PositionSize<self.params.position_lower_limit:
                    PositionSize=self.params.position_lower_limit
                return PositionSize
            
            if self.params.is_position_size_fixed=="yes":
                PositionSize=self.params.fixed_position_size
            else:
                PositionSize= position_size_calculation()
            
            PositionSize=round(PositionSize, ndigits=3)
            PositionSize=str(PositionSize)
            self.i_registry.Pos_Sizing_Reg.append(PositionSize)  
            
            price_to_use=round(self.asset_selected.close[-1],ndigits=2)
            price_to_use=str(price_to_use)  
            
            self.i_registry.log('SELL CREATE, %.2f' % self.asset_selected.close[-1])
            self.i_registry.log('SELL SIZE, ' + self.i_registry.Pos_Sizing_Reg[-1])
            
            self.i_registry.log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
            self.i_registry.log3('SELL CREATE, %.2f' % self.asset_selected.close[-1])
            self.i_registry.log3('SELL SIZE, ' + self.i_registry.Pos_Sizing_Reg[-1])
            
            sell_order= self.account_info.client.post_order(symbol=self.GLOBAL_SYMBOL, 
                                                    side=self.account_info.OrderSide.SELL,
                                                    positionSide="SHORT",
                                                    ordertype=self.account_info.OrderType.LIMIT, ### <--LIMIT ORDER
                                                    timeInForce=self.account_info.TimeInForce.GTC,
                                                    # callbackRate=stoppricebyatr_rate,
                                                    price=price_to_use, 
                                                    quantity=self.i_registry.Pos_Sizing_Reg[-1]
                                                    )
            self.i_registry.order_history.append(vars(sell_order))
            
            self.i_registry.log('SELL SIZE END, ' + self.i_registry.Pos_Sizing_Reg[-1])
            self.i_registry.log3('SELL SIZE END, ' + self.i_registry.Pos_Sizing_Reg[-1])
        except Exception as e:
            self.i_registry.log(e)
            self.i_registry.log3(e)

    ###############################################################################################
    def Global_Buy_operation(self, increment_factor=1.0) -> None:  # MAIN OPERATION
        # ACTUAL EXECUTION OF TRAIL BUY ORDER USED TO ENTER LONG/BUY POSITIONS
        try:
            def position_size_calculation() -> float:
                Cash_to_risk=self.i_registry.last_total_cash*self.params.percentage_to_risk/100

                if increment_factor>1.0:
                    PositionSize=float(increment_factor)*float(self.i_registry.Pos_Sizing_Reg[-1])
                else:
                    PositionSize=self.params.granularity*Cash_to_risk    #<<<--- GRANULARITY DETERMINES THE FIRST POSITION SIZE

                if  PositionSize>self.params.position_upper_limit-self.i_registry.position_now_qtty:
                    PositionSize=self.params.position_upper_limit-self.i_registry.position_now_qtty
                
                if  PositionSize<self.params.position_lower_limit:
                    PositionSize=self.params.position_lower_limit
                return PositionSize

            if self.params.is_position_size_fixed=="yes":
                PositionSize=self.params.fixed_position_size
            else:
                PositionSize= position_size_calculation()

            PositionSize=round(PositionSize, ndigits=3)
            PositionSize=str(PositionSize)
            self.i_registry.Pos_Sizing_Reg.append(PositionSize)
            
            price_to_use=round(self.asset_selected.close[-1],ndigits=2)
            price_to_use=str(price_to_use)  
            
            self.i_registry.log('BUY CREATE, %.2f' % self.asset_selected.close[-1])
            self.i_registry.log('BUY SIZE, ' + self.i_registry.Pos_Sizing_Reg[-1])
            
            self.i_registry.log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
            self.i_registry.log3('BUY CREATE, %.2f' % self.asset_selected.close[-1])
            self.i_registry.log3('BUY SIZE, ' + self.i_registry.Pos_Sizing_Reg[-1])
            
            buy_order= self.account_info.client.post_order(symbol=self.GLOBAL_SYMBOL, 
                                                    side=self.account_info.OrderSide.BUY,
                                                    positionSide="LONG",
                                                    ordertype=self.account_info.OrderType.LIMIT, ### <--LIMIT ORDER
                                                    timeInForce=self.account_info.TimeInForce.GTC,
                                                    # callbackRate=stoppricebyatr_rate,
                                                    price=price_to_use, 
                                                    quantity=self.i_registry.Pos_Sizing_Reg[-1]
                                                    )
            self.i_registry.order_history.append(vars(buy_order))
            
            self.i_registry.log('BUY SIZE END, ' + self.i_registry.Pos_Sizing_Reg[-1])
            self.i_registry.log3('BUY SIZE END, ' + self.i_registry.Pos_Sizing_Reg[-1])
        except Exception as e:
            self.i_registry.log(e)
            self.i_registry.log3(e)

    ###############################################################################################

    def cancel_all_orders(self) -> None:  # MAIN OPERATION
        # CANCEL UNFULFILLED ORDERS
        self.i_registry.log('CANCELLING ALL ORDERS')
        self.account_info.client.cancel_all_orders(symbol=self.GLOBAL_SYMBOL)
        self.i_registry.log('ORDERS CANCELLED')

    def close_active_position(self) -> None:  # MAIN OPERATION
        # CLOSE ACTIVE POSITION BY SELLING OR BUYING AT MARKET PRICE
        if self.i_registry.long_unreal_profit>self.i_registry.short_unreal_profit:
            try:
                price_to_use=round(self.asset_selected.close[-1],ndigits=2)
                price_to_use=str(price_to_use-5)
                self.i_registry.log('Closing Long position')
                self.i_registry.log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                self.i_registry.log3('Closing Long position')
                
                ### THATS HOWS DONE
                self.account_info.client.post_order(symbol=self.GLOBAL_SYMBOL, 
                                                    side="SELL",
                                                    positionSide="LONG", #THIS CLOSES THE LONG
                                                    ordertype="STOP_MARKET",###TAKE_PROFIT_MARKET <--- THIS IS A STOP MARKET ORDER  
                                                    # price=price_to_use,
                                                    stopPrice=price_to_use,
                                                    # quantity=(0.001),
                                                    # reduceOnly="True",
                                                    timeInForce="GTC", 
                                                    closePosition="True",
                                                    workingType="MARK_PRICE"
                                                    
                                                    )
                self.account_info.client.post_order(symbol=self.GLOBAL_SYMBOL, 
                                                    side="BUY",
                                                    positionSide="SHORT", #THIS CLOSES THE SHORT
                                                    ordertype="TAKE_PROFIT_MARKET",###STOP_MARKET <--- THIS IS A STOP MARKET ORDER  
                                                    # price=price_to_use,
                                                    stopPrice=price_to_use,
                                                    # quantity=(0.001),
                                                    # reduceOnly="True",
                                                    timeInForce="GTC", 
                                                    closePosition="True",
                                                    workingType="MARK_PRICE"
                                                    
                                                    )
                self.i_registry.log('Finished Closing positions with Long as Take Profit')
                self.i_registry.log3('Finished Closing positions with Long as Take Profit')
            except Exception as e:
                self.i_registry.log(e)
        
        elif self.i_registry.short_unreal_profit>self.i_registry.long_unreal_profit:
            try:
                price_to_use=round(self.asset_selected.close[-1],ndigits=2)
                price_to_use=str(price_to_use+5)
                self.i_registry.log('Closing Short position')
                self.i_registry.log3(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S"))
                self.i_registry.log3('Closing Short position')
                self.account_info.client.post_order(symbol=self.GLOBAL_SYMBOL, 
                                                    side="SELL",
                                                    positionSide="LONG", #THIS CLOSES THE LONG
                                                    ordertype="TAKE_PROFIT_MARKET",###STOP_MARKET <--- THIS IS A STOP MARKET ORDER  
                                                    # price=price_to_use,
                                                    stopPrice=price_to_use,
                                                    # quantity=(0.001),
                                                    # reduceOnly="True",
                                                    timeInForce="GTC", 
                                                    closePosition="True",
                                                    workingType="MARK_PRICE"
                                                    
                                                    )
                self.account_info.client.post_order(symbol=self.GLOBAL_SYMBOL, 
                                                    side="BUY",
                                                    positionSide="SHORT", #THIS CLOSES THE SHORT
                                                    ordertype="STOP_MARKET",###TAKE_PROFIT_MARKET <--- THIS IS A STOP MARKET ORDER  
                                                    # price=price_to_use,
                                                    stopPrice=price_to_use,
                                                    # quantity=(0.001),
                                                    # reduceOnly="True",
                                                    timeInForce="GTC", 
                                                    closePosition="True",
                                                    workingType="MARK_PRICE"
                                                    
                                                    )
                
                self.i_registry.log('Finished Closing positions with Short as Take Profit')
                self.i_registry.log3('Finished Closing positions with Short as Take Profit')
            except Exception as ex:
                self.i_registry.log(ex)
                self.i_registry.log3(ex)