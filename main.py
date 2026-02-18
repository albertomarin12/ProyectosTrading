from backtest import run_single_backtest
from data import load_data, preprocess_data
from optimization import optimize_strategy

#Entrypoint
def main():
    print("Starting...")
    data_train, data_test = load_data()

    data_train = preprocess_data(data_train)    
    data_test = preprocess_data(data_test)

    #print(data_train.head())
    #print(data_test.head())

    strategy_value, num_operations = run_single_backtest(data_train)
    print(f"Final strategy value: {strategy_value[-1]:.2f}")
    print(f"Number of operations: {num_operations}")

if __name__ == "__main__":
    main()