import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_boxplot_priorities(df_orders):
    df_plot = df_orders[['Priorität', 'Order_Duration']].dropna()
    if not df_plot.empty and df_plot['Priorität'].nunique() > 1:
        plt.figure(figsize=(8, 6))
        sns.boxplot(x='Priorität', y='Order_Duration', data=df_plot)
        plt.ylim(0, 1000)
        plt.xlabel('Priorität')
        plt.ylabel('Auftragsdauer (Minuten)')
        plt.title('Verteilung der Auftragsdauer nach Priorität')
        plt.tight_layout()
        plt.show()
    else:
        print("⚠️ Nicht genügend Daten für den Boxplot.")

        
def visualize_matched_downtime_orders(df_machine, df_orders, downtime_threshold=100):
    """
    Visualisiert Aufträge, denen ein Maschinenstillstand mit hoher Downtime zugeordnet werden kann.
    Zeigt Kurztext + Auftragsnummer sowie Downtime als Label.
    """

    if 'Downtime' not in df_machine.columns:
        print("⚠️ Spalte 'Downtime' nicht vorhanden.")
        return

    # Downtime bereinigen
    df_machine['Downtime'] = df_machine['Downtime'].apply(
        lambda x: float(str(x).replace(',', '.')) if pd.notnull(x) else 0
    )

    # Datum bereinigen
    if 'Calendar day' not in df_machine.columns or 'Start_ts' not in df_orders.columns:
        print("⚠️ Benötigte Zeitspalten fehlen.")
        return

    df_machine['Calendar day'] = pd.to_datetime(df_machine['Calendar day'], errors='coerce')
    df_orders['Start_ts'] = pd.to_datetime(df_orders['Start_ts'], errors='coerce')

    df_machine['Calendar_day_only'] = df_machine['Calendar day'].dt.date
    df_orders['Start_date_only'] = df_orders['Start_ts'].dt.date


    # Filter: nur Einträge mit hoher Downtime
    machine_filtered = df_machine[df_machine['Downtime'] > downtime_threshold]

    # Merge auf Datum
    merged = pd.merge(
        machine_filtered,
        df_orders[['Start_date_only', 'Kurztext', 'Auftrag', 'Order_Duration']],
        left_on='Calendar_day_only',
        right_on='Start_date_only',
        how='inner'
    )


    if merged.empty:
        print("⚠️ Keine passenden Aufträge mit Downtime über dem Schwellwert gefunden.")
        return

    # Anzeige vorbereiten: Kurztext + Auftragsnummer
    merged['Kurztext_Anzeige'] = merged.apply(
        lambda row: f"{row['Kurztext']} (Auftrag: {int(row['Auftrag'])})" if pd.notnull(row['Auftrag']) else row['Kurztext'],
        axis=1
    )

    # Top 10 für Plot
    top_merged = merged[['Calendar day', 'Downtime', 'Kurztext_Anzeige', 'Order_Duration']].sort_values(by='Downtime', ascending=False).head(10)

    # Plot
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        x='Downtime',
        y='Kurztext_Anzeige',
        data=top_merged,
        palette='mako'
    )
    plt.xlabel('Stillstandszeit (Minuten)')
    plt.ylabel('Kurztext + Auftrag')
    plt.title('Top 10 Maschinenstillstände mit zugeordneten Aufträgen')

    # Downtime-Werte direkt an die Balken schreiben
    for i, value in enumerate(top_merged['Downtime']):
        ax.text(value + 5, i, f"{int(value)} min", va='center')

    plt.tight_layout()
    plt.show()

def plot_damage_type_distribution(df_orders):
    """
    Plottet die Verteilung der Aufträge nach Schadenskategorie
    mit Prozentanteilen und berechnet die Trefferquote.
    """
    # Nur relevante Spalte
    df_plot = df_orders[['Damage_Type']].copy()

    if df_plot.empty or df_plot['Damage_Type'].isnull().all():
        print("⚠️ Keine Schadenskategorien vorhanden.")
        return

    # Trefferquote berechnen
    total_orders = len(df_plot)
    categorized_orders = df_plot[df_plot['Damage_Type'] != 'other'].shape[0]
    hit_rate = (categorized_orders / total_orders) * 100

    print(f"✅ Trefferquote: {hit_rate:.2f}% der Aufträge konnten einer Kategorie zugeordnet werden.")

    # Verteilung plotten
    damage_counts = df_plot['Damage_Type'].value_counts().sort_values(ascending=False)
    damage_percent = (damage_counts / total_orders) * 100

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=damage_counts.values, y=damage_counts.index)

    plt.xlabel('Anzahl Aufträge')
    plt.ylabel('Schadenskategorie')
    plt.title('Verteilung der Aufträge nach Schadenskategorie')

    # Prozentanteile auf die Balken schreiben
    for i, (count, percent) in enumerate(zip(damage_counts.values, damage_percent.values)):
        ax.text(count + 1, i, f"{percent:.1f}%", va='center')

    plt.tight_layout()
    plt.show()
