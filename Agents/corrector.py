def get_corrector_prompt(product_name, tech_data, draft_description, category):
    return f"""Jsi technická kontrola kvality (QA) pro B2B data.

ZKONTROLUJ SHODU TĚCHTO DAT:
1. Původní název: "{product_name}"
2. Kategorie: "{category}"
3. Původní technická data: {tech_data}
4. Vygenerovaný popis:
{draft_description}

KONTROLNÍ BODY:
- Sedí rozměry v popisu s názvem produktu?
- Odpovídá popis kategorii "{category}"? (Např. popis nesmí mluvit o rukavicích, pokud jde o šroub).
- Jsou odstraněna slova jako "úžasný", "krásný"? Text musí být strohý.
- Jsou správně jednotky (mm, ks, ml)?

VÝSTUP:
Pokud je text v pořádku, vrať ho beze změny.
Pokud najdeš faktickou chybu nebo špatný tón, oprav ji a vrať pouze opravený Markdown text.
"""