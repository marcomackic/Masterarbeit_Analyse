import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_matched_downtime_orders(df_machine: pd.DataFrame, df_orders: pd.DataFrame, downtime_threshold=60):
    """
    Verknüpft SAP-Aufträge mit Maschinenstillständen (Datum + Arbeitsplatz)
    und visualisiert Top 10 Downtime + SAP-Dauer.
    """

    # Vorverarbeitung
    df_machine['Downtime'] = df_machine['Downtime'].apply(
        lambda x: float(str(x).replace(',', '.')) if pd.notnull(x) else 0
    )
    df_machine['Calendar day'] = pd.to_datetime(df_machine['Calendar day'], format='%d.%m.%Y', errors='coerce')
    df_orders['Start_ts'] = pd.to_datetime(df_orders['Start_ts'], errors='coerce')

    df_machine['Match_Day'] = df_machine['Calendar day'].dt.date
    df_orders['Match_Day'] = df_orders['Start_ts'].dt.date

    # Downtime aggregieren
    grouped = df_machine.groupby(['Match_Day', 'Work Center'], as_index=False)['Downtime'].sum()

    # Merge SAP + Downtime
    merged = pd.merge(
        df_orders[['Auftrag', 'Kurztext', 'Arbeitsplatz', 'Order_Duration', 'Match_Day']],
        grouped,
        left_on=['Match_Day', 'Arbeitsplatz'],
        right_on=['Match_Day', 'Work Center'],
        how='inner'
    )

    '''
    auftrag_id = 70004528
    debug_row = merged[merged['Auftrag'] == auftrag_id][['Auftrag', 'Order_Duration', 'Downtime']]
    print(f"\n🔎 Auftrag {auftrag_id} – Matching-Ergebnis:\n{debug_row}")

    print("🔍 Beispiele für Order_Duration:\n", merged[['Auftrag', 'Order_Duration']].dropna().head())
    '''

    # Filter und vorbereiten
    filtered = merged[merged['Downtime'] > downtime_threshold].copy()
    if filtered.empty:
        print("⚠️ Keine Einträge mit Downtime über dem Schwellwert gefunden.")
        return   

    filtered['Kurztext_mit_Auftrag'] = filtered.apply(
        lambda row: f"{row['Kurztext']} (Auftrag: {int(row['Auftrag'])})", axis=1
    )

    top = filtered[['Kurztext_mit_Auftrag', 'Downtime', 'Order_Duration']].sort_values(by='Downtime', ascending=False).head(10)


    # Plot
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
    data=top,
    x='Downtime',
    y='Kurztext_mit_Auftrag',
    hue='Kurztext_mit_Auftrag',
    palette='flare',
    legend=False
)

    for bar, (_, row) in zip(ax.patches, top.iterrows()):
        downtime = int(row['Downtime']) if pd.notnull(row['Downtime']) else 0
        duration = int(row['Order_Duration']) if pd.notnull(row['Order_Duration']) else 0
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f"{downtime} min (SAP: {duration} min)", va='center')





    plt.xlabel("Stillstandszeit (Minuten)")
    plt.ylabel("Kurztext + Auftrag")
    plt.title("Top 10 Maschinenstillstände mit Order-Dauer-Vergleich")
    plt.tight_layout()
    plt.show()



def get_top_matched_downtimes(df_orders: pd.DataFrame, df_machine: pd.DataFrame, downtime_threshold=60, top_n=10):
    """
    Gibt ein DataFrame mit den Top-N Maschinenstillständen + zugeordneten SAP-Aufträgen zurück.
    Berücksichtigt Datum + Arbeitsplatz (genaues Matching).
    """

    df_orders = df_orders.copy()
    df_machine = df_machine.copy()

    if 'Start_ts' not in df_orders.columns or 'Arbeitsplatz' not in df_orders.columns:
        print("⚠️ Fehlende Spalten in df_orders.")
        return pd.DataFrame()

    if 'Calendar day' not in df_machine.columns or 'Work Center' not in df_machine.columns or 'Downtime' not in df_machine.columns:
        print("⚠️ Fehlende Spalten in df_machine.")
        return pd.DataFrame()

    df_orders['Match_Day'] = pd.to_datetime(df_orders['Start_ts'], errors='coerce').dt.date
    df_machine['Match_Day'] = pd.to_datetime(df_machine['Calendar day'], dayfirst=True, errors='coerce').dt.date

    df_machine['Work Center'] = df_machine['Work Center'].ffill()
    df_orders['Arbeitsplatz'] = df_orders['Arbeitsplatz'].astype(str)
    df_machine['Work Center'] = df_machine['Work Center'].astype(str)

    downtime_agg = df_machine.groupby(['Match_Day', 'Work Center'], as_index=False)['Downtime'].sum()
    downtime_agg = downtime_agg[downtime_agg['Downtime'] > downtime_threshold]

    merged = pd.merge(
        df_orders,
        downtime_agg,
        left_on=['Match_Day', 'Arbeitsplatz'],
        right_on=['Match_Day', 'Work Center'],
        how='inner'
    )

    print("📋 Spalten im merged:", merged.columns.tolist())
    print(merged[['Auftrag', 'Order_Duration']].dropna().head(5))


    if merged.empty:
        print("⚠️ Keine Zuordnungen mit Downtime über Threshold gefunden.")
        return pd.DataFrame()

    merged['Kurztext_mit_Auftrag'] = merged.apply(
        lambda row: f"{row['Kurztext']} (Auftrag: {int(row['Auftrag'])})", axis=1
    )

    top_matches = (
        merged[['Kurztext_mit_Auftrag', 'Downtime']]
        .sort_values(by='Downtime', ascending=False)
        .head(top_n)
    )

    return top_matches
