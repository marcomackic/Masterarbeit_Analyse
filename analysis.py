def analyze_priorities(df_orders):
    priority_stats = df_orders.groupby('Priorität')['Order_Duration'].mean().reset_index()
    print("\nDurchschnittliche Auftragsdauer nach Priorität:")
    print(priority_stats)

def print_damage_stats(df_orders):
    """
    Gibt für jede Schadenskategorie die Anzahl der Aufträge und die durchschnittliche Auftragsdauer aus.
    """
    damage_stats = df_orders.groupby('Damage_Type').agg(
        Auftragsanzahl=('Order_Duration', 'count'),
        Durchschnittliche_Auftragsdauer=('Order_Duration', 'mean')
    ).reset_index()

    print("\nStatistiken pro Schadensbild:")
    print(damage_stats)


def correlate_downtime(df_merged):
    if 'Downtime' in df_merged.columns:
        valid_corr = df_merged[['Order_Duration', 'Downtime']].dropna()
        if not valid_corr.empty:
            corr = valid_corr['Order_Duration'].corr(valid_corr['Downtime'])
            print(f"\n📊 Korrelationskoeffizient zwischen Order_Duration und Downtime: {corr:.3f}")
        else:
            print("⚠️ Keine gemeinsamen gültigen Werte für Order_Duration und Downtime.")
    else:
        print("⚠️ Downtime-Spalte nicht vorhanden.")
