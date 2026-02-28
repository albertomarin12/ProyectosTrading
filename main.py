from data import load_data, preprocess_data
from optimization import run_walk_forward
from visualization import plot_results, display_optimal_table
from signals import generate_signals
from my_backtesting import SingleSlotBacktester

def main():
    print("Cargando y preprocesando datos...")
    # 1. Cargar y Preprocesar
    data_train, _ = load_data()
    data_train = preprocess_data(data_train)

    # 2. Ejecutar Walk-Forward
    df_optimal_params = run_walk_forward(data_train)

    if df_optimal_params.empty:
        print("Error: No se pudieron generar ventanas de optimización. Revisa el rango de fechas.")
        return

    # 3. Mostrar Tabla
    display_optimal_table(df_optimal_params)

    # 4. Preparar parámetros finales para graficar
    last_best = df_optimal_params.iloc[-1]
    rsi_vals = last_best['RSI Low/Up'].split('/')
    
    last_best_params = {
        "rsi_window": int(last_best['RSI Win']),
        "ma_window": int(last_best['MA Win']),
        "rsi_lower": int(rsi_vals[0]),
        "rsi_upper": int(rsi_vals[1]),
        "n_shares": int(last_best['Shares']),
        "take_profit": float(last_best['TP (%)']) / 100,
        "stop_loss": float(last_best['SL (%)']) / 100,
    }

    print("Generando simulación final y gráficos...")
    data_best = generate_signals(data_train, last_best_params)
    bt = SingleSlotBacktester()
    history, trades = bt.run(data_best, last_best_params)
    
    # --- NUEVO: CÁLCULO DEL RESUMEN FINAL ---
    initial_cap = bt.initial_cash
    final_cap = history[-1]
    profit_usd = final_cap - initial_cap
    profit_pct = (profit_usd / initial_cap) * 100
    
    # Calcular comisiones y conteo de operaciones
    # La comisión es 0.125% + IVA = 0.145% (0.00145)
    com_rate = 0.00125 * 1.16 
    n_shares = last_best_params['n_shares']
    total_commissions = 0
    total_operations = 0
    
    for t in trades:
        # Cada 'buy' o 'sell' es la apertura de una nueva operación
        if t['type'] in ['buy', 'sell']:
            total_operations += 1
            
        # Cobramos comisión en entradas y salidas (excepto en un margin call puro que no liquida)
        if t['type'] in ['buy', 'sell', 'exit_long', 'exit_short']:
            total_commissions += t['price'] * n_shares * com_rate

    # --- IMPRIMIR RESUMEN ---
    print("\n" + "="*50)
    print("   RESUMEN FINAL DE LA ESTRATEGIA")
    print("="*50)
    print(f"Capital Inicial:      ${initial_cap:,.2f}")
    print(f"Capital Final:        ${final_cap:,.2f}")
    print(f"Ganancia Neta (USD):  ${profit_usd:,.2f}")
    print(f"Rendimiento Neto (%): {profit_pct:.2f}%")
    print(f"Operaciones Abiertas: {total_operations}")
    print(f"Total en Comisiones:  ${total_commissions:,.2f}")
    print("="*50 + "\n")

    # Mostrar la gráfica
    plot_results(data_best, history, trades, last_best_params)

if __name__ == "__main__":
    main()
