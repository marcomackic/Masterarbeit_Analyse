import re
import unicodedata
import pandas as pd

def clean_text(text):
    if pd.isnull(text):
        return ''
    text = unicodedata.normalize("NFD", str(text))
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    text = text.replace('#', '').replace('\xa0', ' ')
    text = re.sub(r'[^a-zA-Z0-9äöüßáéíóú\s\-]', '', text)
    return text.lower()

def classify_damage_types(df):
    df['Kurztext_clean'] = df['Kurztext'].apply(clean_text)
    df['Damage_Type'] = df['Kurztext_clean'].apply(classify_damage_extended_v2)
    return df

damage_keywords = {
    'mechanical': [r'\b(kardan|lozisk|valec|kloub|hrabe|hrabi|sroub|rameno|vibr|unwucht|mechan|welle|cep|zavit|drzak|pravitko|uvoln|ulomen|zamek|ozuben)\b'],
    'electrical': [r'\b(elektr|elektro|motor|jistic|kontakt|civka|frekven|invert|servomotor|servo|encoder|napajeni|spinac|koncak|rele|elektroskrin|elporucha|ridici|elektron|prevodnik|kabel)\b'],
    'form': [r'\b(form|forma|forme|strizn|vlozka|brous|prebrous|deska|kalandr|matrice|tvarovac|dira|lem|otisk|klise|segment|kontura|hlava|rozděl|rozdell)\b'],
    'hydraulic': [r'\b(pistnic|hydraul|tlak|tesn|netes|pruzin|pritlak|vzduch|unik vzduch|membran|vakuum|vakuova|tlumic|hadic|olej|filtr|voda|pneu|pneumat)\b'],
    'sensor': [r'\b(snimac|cidlo|sensor|senzor|indikator|enkoder|detektor|meric|mereni)\b'],
    'infrastructure': [r'\b(infrastruktura|budova|osvetlen|klimatizace|zasuvka|branka|brana|okno|dver|mazan|mazani|mazaci|ventilace|kanal|vytapeni|strop|podlaha)\b'],
    'software/control': [r'\b(software|softwar|program|reset|komunikace|chyba plc|siemens|ovlad|rizeni|system|parametr|aktualizace|modul|firmware)\b'],
    'safety': [r'\b(bezpecnost|zamek dveri|zabezpeceni|kryt|ochrana|svetelna zavora|havari|alarm|notaus|emergency)\b'],
    'maintenance': [r'\b(udrzba|cisteni|mazani|serizeni|kalibrace|kontrola|vymena|prohlidka|oprava)\b'],
    'unknown': []
}

def classify_damage_extended_v2(text):
    for category, patterns in damage_keywords.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return category
    return 'other'
