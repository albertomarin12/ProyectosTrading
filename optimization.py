import pandas as pd
import optuna
from datetime import timedelta
from my_backtesting import SingleSlotBacktester
from signals import generate_signals

def objective(trial, data):
    params = {
        "rsi_window": trial.suggest_int("rsi_window", 14, 50), # Antes 5 a 30
        "rsi_lower": trial.suggest_int("rsi_lower", 20, 40),
        "rsi_upper": trial.suggest_int("rsi_upper", 60, 80),
        "ma_window": trial.suggest_int("ma_window", 50, 200),  # Antes 10 a 100
        # Reducimos un poco el tamaño de posición para bajar el impacto
        "n_shares": trial.suggest_float("n_shares", 0.5, 2.0),
        "take_profit": trial.suggest_float("take_profit", 0.02, 0.15), # 2% a 15%
        "stop_loss": trial.suggest_float("stop_loss", 0.02, 0.10),
    }

    data_signals = generate_signals(data, params)
    bt = SingleSlotBacktester()
    history, _ = bt.run(data_signals, params)
    
    return (history[-1] / history[0]) - 1

def run_walk_forward(data):
    train_size = pd.Timedelta(days=30)
    step_size = pd.Timedelta(days=7)
    
    start_date = data.index.min()
    end_date = data.index.max()
    current_train_start = start_date
    wf_results = []

    print(f"Analizando datos desde {start_date} hasta {end_date}...")

    while current_train_start + train_size <= end_date:
        train_end = current_train_start + train_size
        train_data = data.loc[current_train_start:train_end].copy()
        
        if len(train_data) < 100:
            current_train_start += step_size
            continue

        print(f"Optimizando ventana: {current_train_start.date()} al {train_end.date()}...")
        
        # Ocultar el output de Optuna para que no ensucie la terminal
        optuna.logging.set_verbosity(optuna.logging.WARNING) 
        study = optuna.create_study(direction="maximize")
        study.optimize(lambda trial: objective(trial, train_data), n_trials=50)
        
        best = study.best_params
        wf_results.append({
            "Mes Inicio": current_train_start.strftime('%Y-%m-%d'),
            "RSI Win": best['rsi_window'],
            "RSI Low/Up": f"{best['rsi_lower']}/{best['rsi_upper']}",
            "MA Win": best['ma_window'],
            "TP (%)": round(best['take_profit']*100, 2),
            "SL (%)": round(best['stop_loss']*100, 2),
            "Shares": best['n_shares']
        })
        current_train_start += step_size
        
    return pd.DataFrame(wf_results)