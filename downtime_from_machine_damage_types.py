import pandas as pd

def analyze_machine_damage_types(df_machine: pd.DataFrame, df_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Analysiert die durchschnittliche Downtime pro Schadensbild aus den Maschinendaten
    im Zeitraum zwischen frühester und spätester SAP-Order.
    Gibt ein DataFrame mit 'Damage_Type' + 'Avg_Downtime_Minutes' zurück.
    """

    # Sicherstellen, dass 'Calendar day' als Datum verfügbar ist
    if 'Calendar day' not in df_machine.columns:
        print("❌ Spalte 'Calendar day' fehlt.")
        return pd.DataFrame()

    df_machine = df_machine.copy()
    df_machine['Calendar day'] = pd.to_datetime(df_machine['Calendar day'], errors='coerce', dayfirst=True)

    # Dynamischer Zeitraum basierend auf SAP-Orders
    start_date = df_orders['Start_ts'].min().date()
    end_date = df_orders['End_ts'].max().date()
    '''
    print(f"📅 SAP-Zeitraum: {start_date} bis {end_date}")
    '''

    # Maschinendaten auf den Zeitraum filtern
    df_machine_filtered = df_machine[
        (df_machine['Calendar day'].dt.date >= start_date) &
        (df_machine['Calendar day'].dt.date <= end_date)
    ]

    # Zielspalten mit Downtime pro Schadensbild
    damage_cols = [
        'Malfunction\n(1201)',
        'Machine\n(1401)',
        'Infrastructure\n(1402)',
        'Mold\n(1403)',
        'Peripheral\nEquipment\n(1404)',
        'Automation\n(1405)'
    ]

    '''
    print("📋 Spaltennamen in df_machine_filtered:")
    print(df_machine_filtered.columns.tolist())
    '''

    # Lesbare Namen definieren
    readable_names = {
        'Malfunction\n(1201)': 'Malfunction',
        'Machine\n(1401)': 'Machine',
        'Infrastructure\n(1402)': 'Infrastructure',
        'Mold\n(1403)': 'Mold',
        'Peripheral\nEquipment\n(1404)': 'Peripheral Equipment',
        'Automation\n(1405)': 'Automation'
    }

    # 🔄 Bereinigung: Dezimaltrennzeichen, Strings zu Float, nur Zahlen extrahieren
    for col in damage_cols:
        if col in df_machine_filtered.columns:
            #print(f"\n🔍 Erste Rohwerte für '{col}':")
            #print(df_machine_filtered[col].dropna().astype(str).unique()[:5])

            df_machine_filtered.loc[:, col] = (
                df_machine_filtered[col]
                .astype(str)
                .str.replace(',', '.', regex=False)
                .str.extract(r'(\d+(?:\.\d+)?)')[0]
                .astype(float)
            )
        else:
            print(f"⚠️ Spalte '{col}' nicht gefunden!")

    '''
    # Debug-Ausgabe
    print(f"📊 Gefilterte Zeilen: {len(df_machine_filtered)}")
    print(df_machine_filtered[damage_cols].head())
    print(df_machine_filtered[damage_cols].dtypes)
    '''

    # Mittelwerte berechnen und Format anpassen
    averages = (
        df_machine_filtered[damage_cols]
        .mean()
        .rename(index=readable_names)
        .reset_index()
        .rename(columns={'index': 'Damage_Type', 0: 'Avg_Downtime_Minutes'})
    )

    print("\n📊 Durchschnittliche Downtime nach Schadensbild (nur Zeitraum der SAP-Orders):")
    print(averages)

    return averages
