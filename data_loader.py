# data_loader.py
import pandas as pd
from config import (
    SAP_ORDER_PATH,
    MACHINE_DATA_PATH,
    SAP_NOTIFICATION_PATH,
    SAP_FAILURECODES_PATH
)

def load_order_data():
    return pd.read_excel(SAP_ORDER_PATH)

def load_machine_data():
    return pd.read_csv(MACHINE_DATA_PATH, delimiter=';', encoding='latin-1', header=0)

def load_notification_data():
    return pd.read_excel(SAP_NOTIFICATION_PATH)

def load_failurecode_data():
    return pd.read_excel(SAP_FAILURECODES_PATH)

def load_data():
    return load_order_data(), load_machine_data()

