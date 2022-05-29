
class   Sample_Signals(object):
    def __init__(self, asset_selected, i_registry) -> None:
        self.asset_selected=asset_selected
        self.i_registry=i_registry

    def buy_signal(self):
        # SAMPLE BUY SIGNAL FUNCTION, INPUT YOUR OWN STRATEGY TO ENTER POSITIONS HERE
        self.i_registry.log2("buy_signal function initiated")
        if self.asset_selected.slowk[-1]>self.asset_selected.slowd[-1] and self.asset_selected.slowk[-2]<self.asset_selected.slowd[-2]:
            self.asset_selected.Barrel.append('Bottom')
            return  True
        else: 
            return False

    def sell_signal(self):
        # SAMPLE SELL SIGNAL FUNCTION, INPUT YOUR OWN STRATEGY TO ENTER POSITIONS HERE
        self.i_registry.log2("sell_signal function initiated")
        if self.asset_selected.slowk[-1]<self.asset_selected.slowd[-1] and self.asset_selected.slowk[-2]>self.asset_selected.slowd[-2]:
            self.asset_selected.Barrel.append('Top')
            return  True
        else: 
            return False
