import pandas as pd
from tabulate import tabulate  # Optional: für schönere Konsolenausgabe

def compare_damage_type_durations(df_text, df_sap, df_machine):
    """
    Führt eine Vergleichstabelle zusammen aus:
    - Kurztextanalyse (df_text)
    - SAP-Damage-Types (df_sap)
    - Maschinen-Damage-Typen (df_machine)
    """

    # Einheitliche Zuordnung der Schadensbilder – vorher alles lowercase
    mapping = {
        "mechanical": "Mechanical",
        "mechanisch": "Mechanical",
        "electrical": "Electrical",
        "elektrisch": "Electrical",
        "form": "Mold",
        "mold": "Mold",
        "hydraulic": "Automation",
        "automation": "Automation",
        "infrastructure": "Infrastructure",
        "maintenance": "Maintenance",
        "malfunction": "Malfunction",
        "machine": "Machine",
        "sensor": "Sensor",
        "other": "Other",
        "peripheral equipment": "Peripheral Equipment"
    }

    # Mapping anwenden – vereinheitlichen und ggf. Original erhalten
    for df in [df_text, df_sap, df_machine]:
        if 'Damage_Type' in df.columns:
            df['Damage_Type'] = (
                df['Damage_Type']
                .astype(str)
                .str.strip()
                .str.lower()
                .map(mapping)
                .fillna(df['Damage_Type'])  # falls kein Mapping gefunden wird
            )

    # Downtime von Stunden in Minuten umrechnen
    if 'Avg_Downtime_Minutes' in df_machine.columns:
        df_machine = df_machine.copy()
        df_machine['Downtime_Machine'] = df_machine['Avg_Downtime_Minutes'] * 60
        df_machine = df_machine[['Damage_Type', 'Downtime_Machine']]

    # Outer Join von Textanalyse und SAP
    df_combined = pd.merge(
        df_text,
        df_sap,
        on='Damage_Type',
        how='outer',
        suffixes=('_Text', '_SAP')
    )

    # Join mit Maschinen-Daten
    df_combined = pd.merge(
        df_combined,
        df_machine,
        on='Damage_Type',
        how='outer'
    )

    # Optional: auf 1 Nachkommastelle runden
    df_combined = df_combined.round(1)

    # Ausgabe als Tabelle in der Konsole
    print("\n📊 Vergleich der durchschnittlichen Auftrags-/Stillstandszeiten:")
    print(tabulate(
        df_combined[['Damage_Type', 'Order_Duration_Text', 'Order_Duration', 'Downtime_Machine']],
        headers='keys',
        tablefmt='fancy_grid',
        showindex=False
    ))

    return df_combined
