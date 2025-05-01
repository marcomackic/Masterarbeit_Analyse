import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_sap_damage_types(df_orders, df_notifications, df_failurecodes):
    """
    Verknüpft SAP-Aufträge mit Schadenscodes aus Notification-Daten,
    berechnet die durchschnittliche Auftragsdauer und die Auftragsanzahl pro SAP-Schadensbild.
    """

    # 🧱 Schritt 1: Join SAP Orders mit Notifications
    df_orders = df_orders.copy()
    df_notifications = df_notifications.copy()
    df_joined = pd.merge(
        df_orders,
        df_notifications,
        left_on='Meldung',
        right_on='Meldung',
        how='inner'
    )

    if df_joined.empty:
        print("⚠️ Keine Übereinstimmungen zwischen SAP Orders und Notifications gefunden.")
        return

    # 🔗 Schritt 2: Join mit Failurecodes
    df_joined = pd.merge(
        df_joined,
        df_failurecodes,
        left_on=['Codegruppe', 'Codierungscode'],
        right_on=['Codegruppe', 'Code'],
        how='left'
    )

    if 'Order_Duration' not in df_joined.columns:
        print("⚠️ Spalte 'Order_Duration' nicht gefunden.")
        return

    # 🧮 Schritt 3: Gruppierung: Mittelwert UND Auftragsanzahl
    df_stats = (
        df_joined.groupby('Kurztext zum Code')
        .agg(
            Durchschnittliche_Auftragsdauer=('Order_Duration', 'mean'),
            Auftragsanzahl=('Order_Duration', 'count')
        )
        .reset_index()
        .sort_values(by='Durchschnittliche_Auftragsdauer', ascending=False)
    )

    if df_stats.empty:
        print("⚠️ Keine Schadensbilder mit Auftragsdauer gefunden.")
        return

    print("📊 Statistiken pro SAP-Schadensbild:")
    print(df_stats)

    # 📈 Schritt 4: Visualisierung
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=df_stats,
        x='Durchschnittliche_Auftragsdauer',
        y='Kurztext zum Code',
        palette='magma',
        legend=False
    )

    # ➡️ Auftragsanzahl auf die Balken schreiben
    for i, (duration, count) in enumerate(zip(df_stats['Durchschnittliche_Auftragsdauer'], df_stats['Auftragsanzahl'])):
        ax.text(duration + 5, i, f"{count} Aufträge", va='center')

    plt.xlabel("Durchschnittliche Auftragsdauer (Minuten)")
    plt.ylabel("SAP-Schadensbild")
    plt.title("Durchschnittliche Auftragsdauer und Auftragsanzahl pro SAP-Schadensbild")
    plt.tight_layout()
    plt.show()

    # 🟢 Rückgabe für Weiterverarbeitung
    df_stats.rename(columns={'Kurztext zum Code': 'Damage_Type'}, inplace=True)
    df_stats.rename(columns={'Durchschnittliche_Auftragsdauer': 'Order_Duration'}, inplace=True)
    return df_stats

