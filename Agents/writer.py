FEW_SHOT_EXAMPLES = """
PŘÍKLAD 1:
VSTUP (Data od Analytika):
{
  "kategorie": "Šroub metrický",
  "norma": "DIN 84 / ČSN 021131",
  "material": "Ocel, Pevnost 4.8",
  "povrch": "Galvanický zinek bílý (ZB)",
  "rozmery": { "typ": "M6x14", "prumer": "6 mm", "delka": "14 mm" },
  "specifikace": "Válcová hlava, průběžná drážka plochá"
}
PŮVODNÍ NÁZEV: 008400ZB 06x014 - Šroub s VH a průbež.drážkou

VÝSTUP:
# Šroub s válcovou hlavou M6x14 DIN 84 ZB
## Technická specifikace
Metrický šroub s válcovou hlavou a průběžnou drážkou pro plochý šroubovák. Určen pro spoje s nižším mechanickým namáháním v interiéru.

## Hlavní technické parametry
- **Závit:** Metrický M6
- **Délka:** 14 mm
- **Materiál:** Ocel (třída pevnosti 4.8)
- **Povrchová úprava:** Galvanický zinek bílý (ochrana proti korozi v suchém prostředí)
- **Typ hlavy:** Válcová s plochou drážkou

## Použití
Vhodný pro elektrotechnický průmysl, kompletaci rozvaděčů a lehké strojírenské konstrukce, kde je vyžadována dostupnost spoje plochým šroubovákem.

---

PŘÍKLAD 2:
VSTUP (Data od Analytika):
{
  "kategorie": "Univerzální vrut",
  "norma": "Není",
  "material": "Tvrzená ocel",
  "povrch": "Bílý pozink (BP)",
  "rozmery": { "typ": "5x80", "prumer": "5.0 mm", "delka": "80 mm" },
  "specifikace": "Zápustná hlava (ZH), křížová drážka PZ, částečný závit"
}
PŮVODNÍ NÁZEV: 009700BP 50x080 - Univ.vrut ZH- 5.0x80  BP

VÝSTUP:
# Univerzální vrut do dřeva 5,0x80 mm se zápustnou hlavou
## Technická specifikace
Konstrukční vrut z tvrzené oceli určený pro spojování dřevěných prvků a deskových materiálů. Opatřen povrchovou úpravou bílým zinkem pro základní antikorozní ochranu. Zápustná hlava zajišťuje čisté zapuštění do roviny s materiálem.

## Hlavní technické parametry
- **Rozměr:** 5,0 x 80 mm
- **Typ hlavy:** Zápustná (kónická)
- **Materiál:** Ocel kalená
- **Povrch:** Galvanický zinek bílý

## Použití a montáž
Ideální pro dřevostavby, montáž nábytku a kutilské projekty. Vhodné pro měkké i tvrdé dřevo, dřevotřísku a OSB desky. U tvrdých dřevin doporučujeme předvrtání pro zamezení rozštípnutí materiálu.

---

PŘÍKLAD 3:
VSTUP (Data od Analytika):
{
  "kategorie": "Pracovní rukavice",
  "norma": "EN 388, EN 420",
  "material": "Kombinované (Hovězí štípenka + Textil)",
  "povrch": "Není",
  "rozmery": { "velikost": "10 (XL)" },
  "specifikace": "Model PELICAN PLUS, vyztužená dlaň"
}
PŮVODNÍ NÁZEV: 0101002299100 - PELICAN PLUS rukavice kombinované-10

VÝSTUP:
# Pracovní rukavice PELICAN PLUS kombinované (Velikost 10)
## Technická specifikace
Robustní kombinované rukavice určené pro těžkou manuální práci. Dlaň a prsty jsou zhotoveny z kvalitní hovězí štípenky, hřbet z odolné bavlněné tkaniny. Poskytují dobrou mechanickou ochranu proti oděru a proříznutí.

## Hlavní technické parametry
- **Velikost:** 10 (XL)
- **Materiál dlaně:** Hovězí štípenka
- **Materiál hřbetu:** Bavlněný textil
- **Typ:** Kombinované, s pevnou manžetou
- **Normy:** Splňuje požadavky pro OOP

## Použití
Určeny pro stavebnictví, logistiku, práci s paletami a manipulaci s hrubým materiálem (dřevo, železo). Poskytují komfortní úchop a ochranu kloubů.
"""

def get_writer_prompt(tech_data, original_name, category):
    return f"""Jsi B2B technický copywriter.
Tvé zadání: Vytvořit produktový popis pro e-shop na základě technických dat a kategorie.

KATEGORIE PRODUKTU: {category}
PŮVODNÍ NÁZEV: {original_name}
TECHNICKÁ DATA (od analytika): {tech_data}

STYLOVÁ PRAVIDLA (FEW-SHOT EXAMPLES):
Řiď se přesně strukturou následujících příkladů. Buď stručný, faktický, žádný marketingový balast.
{FEW_SHOT_EXAMPLES}

POKYNY PRO TENTO PRODUKT:
1. Nadpis musí obsahovat klíčové parametry.
2. Sekce "Hlavní technické parametry" musí být formou odrážek.
3. Pokud kategorie je "{category}", přizpůsob tomu sekci "Použití".
4. Vrať POUZE finální Markdown text.
"""