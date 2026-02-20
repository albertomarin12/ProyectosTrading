import optuna
from my_backtesting import SingleSlotBacktester
from signals import generate_signals

def objective(trial, data):
    params = {
        "rsi_window": trial.suggest_int("rsi_window", 5, 30),
        "rsi_lower": trial.suggest_int("rsi_lower", 20, 40),
        "rsi_upper": trial.suggest_int("rsi_upper", 60, 80),
        "ma_window": trial.suggest_int("ma_window", 10, 100),
        "n_shares": trial.suggest_int("n_shares", 1, 5), # Adjust based on capital
        "take_profit": trial.suggest_float("take_profit", 0.01, 0.10),
        "stop_loss": trial.suggest_float("stop_loss", 0.01, 0.10),
    }

    # Generate signals based on current trial parameters
    data_with_signals = generate_signals(data, params)
    
    bt = SingleSlotBacktester()
    history = bt.run(data_with_signals, params)
    
    # Return final return for optimization
    return (history[-1] / history[0]) - 1

def optimize_backtesting(data):
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, data), n_trials=50)
    return study.best_params