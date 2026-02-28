import matplotlib.pyplot as plt
import pandas as pd

def plot_results(data, history, trades, params):
    # Crear figura con 3 subplots (Precio, RSI, PnL)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(15, 12), 
                                         gridspec_kw={'height_ratios': [3, 1, 1]})

    # --- SUBPLOT 1: PRECIO Y MA ---
    ax1.plot(data.index, data['Close'], label='BTC Close', color='black', alpha=0.5)
    ax1.plot(data.index, data['ma'], label=f'MA ({params["ma_window"]})', color='blue', linestyle='--')
    
    # --- NUEVA LÓGICA: Separar los trades por tipo antes de graficar ---
    buys_x = [t['time'] for t in trades if t['type'] == 'buy']
    buys_y = [t['price'] for t in trades if t['type'] == 'buy']
    
    sells_x = [t['time'] for t in trades if t['type'] == 'sell']
    sells_y = [t['price'] for t in trades if t['type'] == 'sell']
    
    exit_l_x = [t['time'] for t in trades if t['type'] == 'exit_long']
    exit_l_y = [t['price'] for t in trades if t['type'] == 'exit_long']
    
    exit_s_x = [t['time'] for t in trades if t['type'] == 'exit_short']
    exit_s_y = [t['price'] for t in trades if t['type'] == 'exit_short']

    # Graficar cada grupo una sola vez (si es que existen)
    if buys_x:
        ax1.scatter(buys_x, buys_y, marker='^', color='green', s=100, label='Buy/Long')
    if sells_x:
        ax1.scatter(sells_x, sells_y, marker='v', color='red', s=100, label='Sell/Short')
    if exit_l_x:
        ax1.scatter(exit_l_x, exit_l_y, marker='x', color='darkgreen', s=80, label='Exit Long')
    if exit_s_x:
        ax1.scatter(exit_s_x, exit_s_y, marker='x', color='darkred', s=80, label='Exit Short')

    ax1.set_title("Estrategia Multi-Indicador: Precio y Ejecución")
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # --- SUBPLOT 2: RSI ---
    ax2.plot(data.index, data['rsi'], label='RSI', color='purple')
    ax2.axhline(params['rsi_upper'], color='red', linestyle='--', alpha=0.5) # Sobrecompra
    ax2.axhline(params['rsi_lower'], color='green', linestyle='--', alpha=0.5) # Sobreventa
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)

    # --- SUBPLOT 3: PORTFOLIO VALUE (PnL) ---
    ax3.plot(data.index, history, label='Valor Cartera', color='gold', linewidth=2)
    ax3.fill_between(data.index, history, 1000000, where=(pd.Series(history) > 1000000), color='green', alpha=0.1)
    ax3.fill_between(data.index, history, 1000000, where=(pd.Series(history) < 1000000), color='red', alpha=0.1)
    ax3.set_ylabel("USD")
    ax3.set_title("Evolución del Capital (P&L)")
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('resultado_backtest.png')
    print("Gráfico guardado como 'resultado_backtest.png'")
    plt.show()

# ... (Aquí sigue tu función display_optimal_table sin cambios)

def display_optimal_table(df_results):
    print("\n" + "="*50)
    print("   RESULTADOS ÓPTIMOS POR VENTANA (WALK-FORWARD)")
    print("="*50)
    # Usamos to_string para que se vea bien en la terminal de VS Code
    print(df_results.to_string(index=False))
    print("="*50 + "\n")
    
    # Opcional: Guardar a CSV para el reporte
    df_results.to_csv("parametros_optimos_wf.csv", index=False)
    print("Tabla guardada en 'parametros_optimos_wf.csv'")