# --- DEFINICE PŘÍKLADŮ (FEW-SHOT) - DELŠÍ TEXT, BEZ POUŽITÍ ---
FEW_SHOT_EXAMPLES = """
PŘÍKLAD 1 (Spojovací materiál - Šroub):
VSTUP: {{"typ": "Šroub", "norma": "DIN 84", "material": "Ocel ZB", "parametry": {{"rozmer": "M6x14"}}}}
NÁZEV: 008400ZB 06x014 - Šroub s VH a průbež.drážkou
VÝSTUP:
Strojní šroub s válcovou hlavou a drážkou pro plochý šroubovák dle normy DIN 84. Vyroben z oceli s povrchovou úpravou galvanickým zinkem, vhodný pro méně namáhané spoje v interiéru.

PŘÍKLAD 2 (Ochranné pomůcky):
VSTUP: {{"typ": "Rukavice", "norma": "EN 388", "material": "Kombinované", "parametry": {{"velikost": "10"}}}}
NÁZEV: PELICAN PLUS rukavice kombinované-10
VÝSTUP:
Odolné kombinované pracovní rukavice PELICAN PLUS velikosti 10. Dlaň z hovězí štípenky a tuhá manžeta zajišťují vysokou mechanickou ochranu dle normy EN 388.

PŘÍKLAD 3 (Tyčový materiál):
VSTUP: {{"typ": "Závitová tyč", "norma": "DIN 975", "material": "Ocel 4.8 ZB", "parametry": {{"rozmer": "M14x2000"}}}}
NÁZEV: Závitová tyč M14x2000 ZB 4.8
VÝSTUP:
Metrická závitová tyč o délce 2 metry, vyrobená z oceli pevnostní třídy 4.8 s galvanickým zinkováním. Ideální pro kotvení, zavěšování a spojování konstrukcí v interiéru.
"""

def get_writer_prompt(tech_data, original_name, category):
    return f"""Jsi zkušený technický redaktor pro B2B katalog.
Tvým úkolem je vytvořit **krátký marketingový popis** (1-2 věty).
Cílová skupina: Profesionálové, nákupčí, řemeslníci.

KATEGORIE PRODUKTU: {category}
PŮVODNÍ NÁZEV: {original_name}
TECHNICKÁ DATA: {tech_data}

INSTRUKCE PRO PSANÍ:
1. **Obsah:** Stručně popiš produkt, jeho klíčové vlastnosti a použití.
2. **Formát:** Pouze prostý text. Žádné Markdown formátování (žádné tučné písmo, žádné nadpisy). Žádné odrážky.
3. **Chybějící data:** Pokud ve vstupu chybí detaily, doplň logický popis standardní pro tento typ produktu.

ŘIĎ SE TĚMITO PŘÍKLADY (FEW-SHOT):
{FEW_SHOT_EXAMPLES}

NYNÍ GENERUJ POPIS PRO: {original_name}
"""