import csv
import os
from datetime import datetime
import  types
# import datetime

dir_data=os.path.dirname(__file__)

CSV_ON=False
logING_ON=True

#CSV SAVE<<<<--------------------------------------------------
if CSV_ON:
    dir1 = dir_data
    filename1 = (dir1+'/Binance_Bot_Registry.csv')
    print('>>>registry 1 path: '+filename1)
    Registry = open(filename1, 'w', newline='')
    TradeTestResults = csv.writer(Registry, delimiter=',')

    dir2 = dir_data
    filename2 = (dir2+'/Binance_Bot_TRADE_ONLY_Registry.csv')
    print('>>>registry 2 path: '+filename2)
    OrdersRegistry = open(filename2, 'w', newline='')
    OrdersResults = csv.writer(OrdersRegistry, delimiter=',')

class internal_registry(object):
    def __init__(self,  *args):
        self.is_secure_profit_order_on = False
        
        self.is_safety_hard_stop_on = False
        
        self.open_buy_orders=0
        self.open_sell_orders=0

        self.last_total_cash = 0
        
        self.long_position_now_qtty=0.0
        self.in_a_long_position=False
        self.long_p_entry_price_now=0.0
        self.long_unreal_profit=0.0
        self.fee_to_open_longs=0.0
        self.fee_to_close_longs=0.0
        
        self.short_position_now_qtty=0.0
        self.in_a_short_position=False
        self.short_p_entry_price_now=0.0
        self.short_unreal_profit=0.0
        self.fee_to_open_shorts=0.0
        self.fee_to_close_shorts=0.0
        
        self.total_opening_fees=0.0
        self.total_closing_fees=0.0
        self.total_fees_so_far=0.0
        
        self.total_unreal_profit=0.0
        self.current_delta = 0.0
        self.target_delta = 0.0

        self.order_history=[]
        self.order_SL_history=[]
        self.order_TP_history=[]
        self.Pos_Sizing_Reg=[]

        self.buysignal=False
        self.sellsignal=False

        self.redo_safety_stop=False

        self.buy_conditions=types.SimpleNamespace()
        self.sell_conditions=types.SimpleNamespace()
        self.operations=types.SimpleNamespace()
        self.signals=types.SimpleNamespace()
    
    def total_fees_to_open(self, fee_rate=0.04):
        # if  self.in_a_long_position:
        self.fee_to_open_longs=self.long_p_entry_price_now*self.long_position_now_qtty*fee_rate/100
        # if self.in_a_short_position:
        self.fee_to_open_shorts=self.short_p_entry_price_now*abs(self.short_position_now_qtty)*fee_rate/100
        self.total_opening_fees= self.fee_to_open_longs+self.fee_to_open_shorts
        
    def total_fees_to_close(self, price_to_evaluate, fee_rate=0.04):
        # if self.in_a_long_position:
        self.fee_to_close_longs=price_to_evaluate*self.long_position_now_qtty*fee_rate/100
        # if self.in_a_short_position:
        self.fee_to_close_shorts=price_to_evaluate*abs(self.short_position_now_qtty)*fee_rate/100
        self.total_closing_fees=self.fee_to_close_longs+self.fee_to_close_shorts

    def total_all_fees(self):
        tf=self.total_opening_fees+self.total_closing_fees
        self.total_fees_so_far=tf

    def total_unrealized_profit(self):
        self.total_unreal_profit=self.long_unreal_profit+self.short_unreal_profit

    def delta_calculation(self):
        d=self.long_position_now_qtty+self.short_position_now_qtty
        self.current_delta=d

    def position_registry_repairer(self):
        if len(self.Pos_Sizing_Reg) == 0 or len(self.Pos_Sizing_Reg) == None:
            if  self.long_position_now_qtty> 0.0 or self.short_position_now_qtty<0.0:
                
                if  self.long_position_now_qtty>abs(self.short_position_now_qtty):
                    repair_with_qtty=abs(self.long_position_now_qtty)/1.5
                    repair_with_qtty=str(repair_with_qtty)
                    self.Pos_Sizing_Reg.append(repair_with_qtty)
                
                elif  self.long_position_now_qtty<abs(self.short_position_now_qtty):
                    repair_with_qtty=abs(self.short_position_now_qtty)/1.5
                    repair_with_qtty=str(repair_with_qtty)
                    self.Pos_Sizing_Reg.append(repair_with_qtty)

    def are_we_in_a_position(self): #ACCOUNT INFO
            # ACCOUNT INFO TO KNOW IF WE ARE IN A POSITION
            if  self.long_position_now_qtty> 0.0:
                self.log2(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")+" WE ARE IN A LONG POSITION ALREADY")
                self.log2("Long Position size now: "+str(self.long_position_now_qtty))
                self.in_a_long_position = True
                
            if  self.short_position_now_qtty< 0.0:
                self.log2(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")+" WE ARE IN A SHORT POSITION ALREADY")
                self.log2("Short Position size now: "+str(self.short_position_now_qtty))
                self.in_a_short_position = True
            
            if  self.long_position_now_qtty== 0.0:
                self.log2(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")+" NO LONG POSITION NOW")
                self.in_a_long_position = False

            if  self.short_position_now_qtty== 0.0:
                self.log2(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%A, %B %d, %Y %H:%M:%S")+" NO SHORT POSITION NOW")
                self.in_a_short_position = False

    def clean_positions_slate(self):  #ACCOUNT INFO
        # CLEANING POSITION SIZING REGISTRY IN CASE THERE ARE NO OPEN POSITIONS OR ORDERS
        self.log2("Trying to clean slate")
        if self.in_a_long_position == False and self.in_a_short_position == False and self.open_buy_orders == 0 and self.open_sell_orders == 0:
            self.log2("Slate cleaned succesfully part 1")
            self.Pos_Sizing_Reg.clear()
            self.log2("Slate cleaned succesfully part 2")
        else:
            self.log2("No need to clean slate")

    ############################################################################
    
    # LOGGING FUNCTION TO SAVE ALGORITHM TRADE MECHANICS 
    def log(self, txt):
            ''' Logging function for this strategy'''
            '''LOGGING FUNCTION TO SAVE ALGORITHM TRADE MECHANICS'''
            dolog=logING_ON
            if dolog:
                
                print(str(txt))
                if CSV_ON:
                    #CSV SAVE<<<<--------------------------------------------------
                    TradeTestResults.writerow([(txt)])
                    Registry.flush()

    # LOGGING FUNCTION TO SAVE FUNCTION EXECUTION
    def log2(self, txt):
            ''' Logging function for this strategy'''
            '''LOGGING FUNCTION TO SAVE FUNCTION EXECUTION'''
            dolog=False
            if dolog:
                
                print(str(txt))
                if CSV_ON:
                    #CSV SAVE<<<<--------------------------------------------------
                    OrdersResults.writerow([(txt)])
                    OrdersRegistry.flush()

    # LOGGING FUNCTION TO SAVE ACTUAL TRADE MOVEMENTS
    def log3(self, txt):
            ''' Logging function for this strategy'''
            '''LOGGING FUNCTION TO SAVE ACTUAL TRADE MOVEMENTS'''
            dolog=logING_ON
            if dolog:
                
                #print(txt)
                if CSV_ON:
                    #CSV SAVE<<<<--------------------------------------------------
                    OrdersResults.writerow([(txt)])
                    OrdersRegistry.flush()
    
    def Number_of_consecutive_positions(self):  #ACCOUNT INFO  

            Position_counter=len(self.Pos_Sizing_Reg)

            if Position_counter==None:
                Position_counter=int(0)
            else:
                Position_counter=Position_counter

            self.log2("Position_counter: "+str(Position_counter))
            return  Position_counter
        