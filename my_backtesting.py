import pandas as pd
import numpy as np

class SingleSlotBacktester:
    def __init__(self, initial_cash=1_000_000, commission=0.00125):
        self.initial_cash = initial_cash
        self.com_rate = commission * 1.16  # Comisión con IVA (16%)
        self.margin_initial = 0.50         # 50% para abrir
        self.margin_maintenance = 0.30     # 30% mínimo
        self.reset()

    def reset(self):
        self.cash = self.initial_cash
        self.state = "IDLE" 
        self.position = None 
        self.history = []
        self.trades = []

    def run(self, data: pd.DataFrame, params: dict):
        self.reset()
        n_shares = params['n_shares']
        
        # Recuperamos el TP y SL de los parámetros
        tp = params['take_profit']
        sl = params['stop_loss']
        
        for i, row in data.iterrows():
            current_price = row.Close
            current_val = self.cash
            
            # --- 1. ACTUALIZACIÓN DE VALOR Y GESTIÓN DE MARGEN ---
            if self.state == "SHORT":
                liability = self.position['n_shares'] * current_price
                floating_pnl = (self.position['entry_price'] - current_price) * self.position['n_shares']
                current_val = self.cash + floating_pnl
                
                current_margin = (self.position['margin_deposit'] + floating_pnl) / liability
                
                # MARGIN CALL
                if current_margin < self.margin_maintenance:
                    required_equity = liability * self.margin_initial
                    shortfall = required_equity - (self.position['margin_deposit'] + floating_pnl)
                    
                    if self.cash >= shortfall:
                        self.cash -= shortfall
                        self.position['margin_deposit'] += shortfall
                        self.trades.append({'time': i, 'price': current_price, 'type': 'margin_call'})
                    else:
                        self.state = "IDLE"
                        self.cash += floating_pnl - (liability * self.com_rate)
                        self.position = None
                        self.trades.append({'time': i, 'price': current_price, 'type': 'exit_short'})
                        current_val = self.cash
            
            elif self.state == "LONG":
                current_val = self.cash + (self.position['n_shares'] * current_price)


            # --- 2. LÓGICA DE SALIDAS (Take Profit / Stop Loss / Reversión) ---
            if self.state != "IDLE":
                entry_price = self.position['entry_price']
                price_change = (current_price / entry_price) - 1 if self.state == "LONG" else (entry_price / current_price) - 1
                
                # Detectar si hay una señal contraria a nuestra posición actual
                reversal_signal = False
                if self.state == "LONG" and row.signal == -1:
                    reversal_signal = True
                elif self.state == "SHORT" and row.signal == 1:
                    reversal_signal = True
                    
                # Si tocamos TP, SL, o los indicadores nos dicen que la tendencia cambió -> CERRAMOS
                if price_change >= tp or price_change <= -sl or reversal_signal:
                    if self.state == "LONG":
                        self.cash += (self.position['n_shares'] * current_price) * (1 - self.com_rate)
                        self.trades.append({'time': i, 'price': current_price, 'type': 'exit_long'})
                    elif self.state == "SHORT":
                        liability = self.position['n_shares'] * current_price
                        floating_pnl = (self.position['entry_price'] - current_price) * self.position['n_shares']
                        self.cash += self.position['margin_deposit'] + floating_pnl - (liability * self.com_rate)
                        self.trades.append({'time': i, 'price': current_price, 'type': 'exit_short'})
                    
                    # Liberamos la cuenta
                    self.state = "IDLE"
                    self.position = None
                    current_val = self.cash


            # --- 3. LÓGICA DE ENTRADAS ---
            # Nota: Usamos 'if' en lugar de 'elif' para que si cierra una posición arriba, pueda abrir la contraria en el mismo instante
            if self.state == "IDLE":
                if row.signal == -1: # SHORT ENTRY
                    notional = current_price * n_shares
                    margin_required = notional * self.margin_initial
                    comm_cost = notional * self.com_rate
                    
                    if self.cash >= (margin_required + comm_cost):
                        self.cash -= (margin_required + comm_cost)
                        self.state = "SHORT"
                        self.position = {
                            'entry_price': current_price, 
                            'n_shares': n_shares,
                            'margin_deposit': margin_required
                        }
                        self.trades.append({'time': i, 'price': current_price, 'type': 'sell'})

                elif row.signal == 1: # LONG ENTRY
                    cost = current_price * n_shares * (1 + self.com_rate)
                    if self.cash >= cost:
                        self.cash -= cost
                        self.state = "LONG"
                        self.position = {'entry_price': current_price, 'n_shares': n_shares}
                        self.trades.append({'time': i, 'price': current_price, 'type': 'buy'})

            self.history.append(current_val)
            
        return self.history, self.trades