from data_loader import load_machine_data, load_order_data
from preprocessing import preprocess_machine_data, preprocess_order_data, merge_data
from categorization import classify_damage_types
from analysis import analyze_priorities, correlate_downtime, print_damage_stats
from visualization import plot_boxplot_priorities
from downtime_matching import visualize_matched_downtime_orders
from sap_damage_type_analysis import analyze_sap_damage_types
from data_loader import load_notification_data, load_failurecode_data
from downtime_from_machine_damage_types import analyze_machine_damage_types
from damage_comparison import compare_damage_type_durations
from visualization import plot_damage_type_distribution


print("📦 Skript gestartet")

# 1. Daten laden
df_machine = load_machine_data()
df_orders = load_order_data()
df_notifications = load_notification_data()
df_failurecodes = load_failurecode_data()


# 2. Vorverarbeitung
df_machine = preprocess_machine_data(df_machine)
df_orders = preprocess_order_data(df_orders)
df_merged = merge_data(df_machine, df_orders)
df_orders.columns = df_orders.columns.str.strip()


# 3. Schadensklassifikation
df_orders = classify_damage_types(df_orders)

# 4. Analyse
analyze_priorities(df_orders)
correlate_downtime(df_merged)
print_damage_stats(df_orders)

# SAP-Schadensbilder
df_sap = analyze_sap_damage_types(df_orders, df_notifications, df_failurecodes)

# Maschinenstillstände pro Schadensbild
df_machine_avg = analyze_machine_damage_types(df_machine, df_orders)

# Kurztextanalyse nach Schadensbild
df_text = classify_damage_types(df_orders)

df_text_avg = (
    df_orders[['Damage_Type', 'Order_Duration']]
    .dropna()
    .groupby('Damage_Type')
    .mean()
    .reset_index()
    .rename(columns={'Order_Duration': 'Order_Duration_Text'})
)

# Vergleichstabelle erzeugen
print(type(df_text), type(df_sap), type(df_machine_avg))
df_combined = compare_damage_type_durations(df_text_avg, df_sap, df_machine_avg)



# 5. Visualisierung
plot_boxplot_priorities(df_orders)
visualize_matched_downtime_orders(df_machine, df_orders, downtime_threshold=60)
plot_damage_type_distribution(df_orders)





