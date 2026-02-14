def get_corrector_prompt(product_name, tech_data, draft_description, category):
    return f"""Jsi technická kontrola (QA).

PŮVODNÍ DATA:
- Název: "{product_name}"
- Kategorie: "{category}"

GENEROVANÝ POPIS KE KONTROLE:
{draft_description}

TVŮJ ÚKOL:
1. Zkontroluj technickou přesnost (sedí rozměry, materiál, norma v obou popisech?).
2. Ověř, že text je **pouze prostý text** bez Markdown formátování (žádné **tučné**, žádné # nadpisy).
3. Ověř, že text neobsahuje zakázanou sekci "Použití" nebo "Aplikace" jako nadpis.
4. Pokud je vše v pořádku, vrať text beze změny. Pokud ne, oprav ho na prostý text.

VÝSTUP: Pouze finální prostý text.
"""