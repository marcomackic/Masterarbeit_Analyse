import pandas as pd
import re

def preprocess_machine_data(df):
    columns_to_fill = [
        'Plant', 'Work Center', 'ArticleNr - new (MD)',
        'Material', 'Production Order',
        'Start date / time', 'End date / time'
    ]
    df[columns_to_fill] = df[columns_to_fill].ffill()
    df['Start date / time'] = pd.to_datetime(df['Start date / time'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
    df['End date / time'] = pd.to_datetime(df['End date / time'], format='%d.%m.%Y %H:%M:%S', errors='coerce')

    # 👉 Formatprüfung und Parsing von 'Calendar day'
    if 'Calendar day' in df.columns:
        df['Calendar day'] = df['Calendar day'].astype(str)
        df = df[df['Calendar day'].str.match(r'\d{2}\.\d{2}\.\d{4}', na=False)]
        df.loc[:, 'Calendar day'] = pd.to_datetime(df['Calendar day'], errors='coerce', dayfirst=True)

    if '[-] Malfunction' in df.columns:
        df = df.rename(columns={'[-] Malfunction': 'Downtime'})
        df.loc[:, 'Downtime'] = df['Downtime'].apply(parse_downtime)
    return df

def parse_downtime(val):
    if pd.isnull(val):
        return None
    val = str(val).strip().upper()
    match = re.match(r"(\d+(?:[\.,]\d*)?)\s*(H|MIN|M)?", val)
    if not match:
        return None
    number = float(match.group(1).replace(',', '.'))
    unit = match.group(2)
    return number * 60 if unit and unit.startswith('H') else number

def preprocess_order_data(df):
    df['Eckstarttermin'] = pd.to_datetime(df['Eckstarttermin'], errors='coerce')
    df['Iststart Uhrzeit'] = pd.to_timedelta(df['Iststart Uhrzeit'].astype(str), errors='coerce')
    df['Eckendtermin'] = pd.to_datetime(df['Eckendtermin'], errors='coerce')
    df['Term. Ende Uhrzeit'] = pd.to_timedelta(df['Term. Ende Uhrzeit'].astype(str), errors='coerce')

    df['Start_ts'] = df['Eckstarttermin'] + df['Iststart Uhrzeit']
    df['End_ts'] = df['Eckendtermin'] + df['Term. Ende Uhrzeit']

    valid_mask = df['Start_ts'].notna() & df['End_ts'].notna()
    df.loc[valid_mask, 'Order_Duration'] = (
        (df.loc[valid_mask, 'End_ts'] - df.loc[valid_mask, 'Start_ts']).dt.total_seconds() / 60
    )

    df = df[(df['Order_Duration'] > 0) & (df['Order_Duration'] < 10000)]
    return df

def merge_data(df_machine, df_orders):
    return pd.merge(df_machine, df_orders, left_on='Work Center', right_on='Arbeitsplatz', how='inner')
