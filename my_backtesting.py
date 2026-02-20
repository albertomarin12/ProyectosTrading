import pandas as pd
import numpy as np

class SingleSlotBacktester:
    def __init__(self, initial_cash=1_000_000, commission=0.00125):
        self.initial_cash = initial_cash
        self.com = commission
        self.reset()

    def reset(self):
        self.cash = self.initial_cash
        self.state = "IDLE"  # IDLE, LONG, SHORT
        self.position = None # Dictionary to store entry_price and n_shares
        self.history = []

    def run(self, data: pd.DataFrame, params: dict):
        self.reset()
        
        # Unpack params
        n_shares = params['n_shares']
        tp = params['take_profit']
        sl = params['stop_loss']
        
        # We assume indicators (signals) are already pre-calculated in the dataframe
        # Signal: 1 (Long), -1 (Short), 0 (Neutral)
        for i, row in data.iterrows():
            current_price = row.Close
            
            # 1. Update Portfolio Value
            floating_pnl = 0
            if self.state == "LONG":
                floating_pnl = (current_price - self.position['entry_price']) * self.position['n_shares']
            elif self.state == "SHORT":
                floating_pnl = (self.position['entry_price'] - current_price) * self.position['n_shares']
            
            # Note: Strategy Value = Cash + (Asset Value if Long) + (PnL if Short)
            # For Long: Cash + (n_shares * current_price)
            # For Short: Cash + Floating PnL
            if self.state == "LONG":
                current_val = self.cash + (self.position['n_shares'] * current_price)
            else:
                current_val = self.cash + floating_pnl
                
            # 2. Check Exits (Take Profit / Stop Loss)
            if self.state != "IDLE":
                entry_price = self.position['entry_price']
                price_change = (current_price / entry_price) - 1 if self.state == "LONG" else (entry_price / current_price) - 1
                
                if price_change >= tp or price_change <= -sl:
                    if self.state == "LONG":
                        # Close Long: Sell asset, get cash, pay commission
                        self.cash += (self.position['n_shares'] * current_price) * (1 - self.com)
                    elif self.state == "SHORT":
                        # Close Short: Realize PnL, pay commission on the notional closed
                        self.cash += floating_pnl - (self.position['n_shares'] * current_price * self.com)
                    
                    self.state = "IDLE"
                    self.position = None

            # 3. Check Entries (Only if IDLE)
            elif self.state == "IDLE":
                if row.signal == 1: # Long Signal
                    cost = current_price * n_shares * (1 + self.com)
                    if self.cash >= cost:
                        self.cash -= cost
                        self.state = "LONG"
                        self.position = {'entry_price': current_price, 'n_shares': n_shares}
                
                elif row.signal == -1: # Short Signal
                    # Short Entry: Deduct only commission from cash
                    comm_cost = current_price * n_shares * self.com
                    if self.cash >= comm_cost:
                        self.cash -= comm_cost
                        self.state = "SHORT"
                        self.position = {'entry_price': current_price, 'n_shares': n_shares}

            self.history.append(current_val)

        return self.history