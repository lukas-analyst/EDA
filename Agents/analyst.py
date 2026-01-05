def get_analyst_prompt(product_name, category):
    return f"""Jsi expertní technický analytik pro B2B e-shop.
Tvým úkolem je extrahovat technická data z názvu produktu na základě jeho kategorie.

VSTUPNÍ DATA:
- Název produktu: "{product_name}"
- Kategorie: "{category}"

TECHNICKÝ SLOVNÍK (POUŽIJ PRO DEKÓDOVÁNÍ):
- ZB, ZN, GALV = Galvanický zinek (bílý) - standardní ochrana do sucha.
- ZC = Zinek černý.
- BP = Bílý pozink.
- A2 / NEREZ = Nerezová ocel A2 (AISI 304).
- A4 = Kyselinovzdorná ocel A4 (AISI 316).
- 8.8, 10.9, 12.9 = Pevnostní třída oceli.
- DIN [číslo], ISO [číslo], ČSN [číslo] = Technická norma.
- VH = Válcová hlava / ZH = Zápustná hlava / 6HR = Šestihranná hlava.

INSTRUKCE:
1. Podívej se na kategorii "{category}". Pokud jde o spojovací materiál, hledej rozměry (průměr x délka). Pokud jde o ochranné pomůcky, hledej velikost/normu.
2. Vrať data striktně jako JSON.

VÝSTUPNÍ FORMÁT (JSON):
{{
  "typ_produktu": "Zpřesněný typ dle názvu (např. Vratový šroub, Kotva)",
  "norma": "DIN/ISO nebo 'Není uvedena'",
  "material_povrch": "Materiál a úprava (dekódováno ze zkratek)",
  "parametry": {{
      "rozmer": "např. M8x100 nebo 5,0x50",
      "prumer": "hodnota v mm",
      "delka": "hodnota v mm nebo objem v ml",
      "ostatni": "typ hlavy, drážka, velikost rukavice atd."
  }},
  "pouziti_hint": "Krátký tip pro agenta copywritera, kam se to hodí (interiér/exteriér/stavba)"
}}
"""