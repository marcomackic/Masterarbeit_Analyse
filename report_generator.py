import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os

from downtime_matching import visualize_matched_downtime_orders, get_top_matched_downtimes
from categorization import classify_damage_types


def save_boxplot(df_orders, path):
    plt.figure(figsize=(10, 6))
    df_plot = df_orders[['Priorität', 'Order_Duration']].dropna()
    if not df_plot.empty and df_plot['Priorität'].nunique() > 1:
        sns.boxplot(x='Priorität', y='Order_Duration', data=df_plot)
        plt.xlabel('Priorität')
        plt.ylabel('Auftragsdauer (Minuten)')
        plt.title('Verteilung der Auftragsdauer nach Priorität')
        plt.ylim(0, 2000)
        plt.tight_layout()
        plt.savefig(path)
        plt.close()


def save_top_downtime_plot(df_top, path):
    if df_top.empty:
        print("⚠️ Keine Top-Downtime-Einträge gefunden.")
        return

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=df_top, x='Downtime', y='Kurztext_mit_Auftrag', palette='crest')
    plt.xlabel("Stillstandszeit (Minuten)")
    plt.ylabel("Fehlerbeschreibung (mit Auftrag)")
    plt.title("Top 10 Maschinenstillstände")

    for i, value in enumerate(df_top['Downtime']):
        ax.text(value + 5, i, f"{int(value)} min", va='center')

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def generate_report(df_orders, df_top):
    pdf = FPDF()
    pdf.add_page()

    # Deckblatt mit Logo
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Automatisch generierter Analysebericht", ln=True, align="C")
    pdf.image("correlation_analysis_modular/csm_greiner-packaging_RGB_a3ba649772.png", x=60, y=30, w=90)
    pdf.ln(80)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "Dieser Bericht enthält eine Übersicht über Auftragsprioritäten und Maschinenstillstände.")
    pdf.ln(5)

    # Boxplot hinzufügen
    boxplot_path = "correlation_analysis_modular/boxplot_prioritaet.png"
    save_boxplot(df_orders, boxplot_path)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "📊 Verteilung der Auftragsdauer nach Priorität", ln=True)
    pdf.image(boxplot_path, x=15, y=30, w=180)
    pdf.ln(90)

    # Downtime Balkendiagramm
    downtime_path = "correlation_analysis_modular/top_downtime.png"
    save_top_downtime_plot(df_top, downtime_path)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "🔧 Top 10 Maschinenstillstände", ln=True)
    pdf.image(downtime_path, x=15, y=30, w=180)
    pdf.ln(10)

    # PDF speichern
    pdf.output("correlation_analysis_modular/abschlussbericht.pdf")
    print("✅ Bericht wurde als abschlussbericht.pdf gespeichert.")


# Hauptlogik
if __name__ == "__main__":
    from data_loader import load_data
    from preprocessing import preprocess_machine_data, preprocess_order_data

    print("📦 Skript gestartet")

    df_machine, df_orders = load_data()
    df_machine = preprocess_machine_data(df_machine)
    df_orders = preprocess_order_data(df_orders)
    df_orders = classify_damage_types(df_orders)

    # Berechne Top-Downtime-Einträge
    top_matches = get_top_matched_downtimes(df_machine, df_orders, downtime_threshold=60)

    # Generiere Bericht
    generate_report(df_orders, top_matches)
