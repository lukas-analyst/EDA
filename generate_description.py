import pandas as pd
import requests
import os
import re
from tqdm import tqdm
from xml.sax.saxutils import escape
import warnings

# Importy vašich agentů
from Agents.analyst import get_analyst_prompt
from Agents.writer import get_writer_prompt
from Agents.corrector import get_corrector_prompt

# --- KONFIGURACE ---
XLSX_PATH = './Sortiment/dbx-input.xlsx'
OUTPUT_XML_PATH = 'generated_descriptions.xml'

# Hybridní nastavení modelů pro efektivitu
MODEL_ANALYST = "gemma3:4b"   # Rychlý pro technická data
MODEL_WRITER = "gemma3:12b"    # Kvalitní pro text
OLLAMA_URL = "http://localhost:11434/api/generate"

LIMIT = 1000     # Změňte na číslo (např. 10) pro test, None pro vše

# --- POMOCNÉ FUNKCE ---

def call_ollama(model, prompt, temperature=0.2):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 600}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        
        if response.status_code != 200:
            return f"CHYBA HTTP {response.status_code}: {response.text}"
            
        json_resp = response.json()
        if "error" in json_resp:
            return f"CHYBA OLLAMA: {json_resp['error']}"
            
        return json_resp.get("response", "").strip()
    except Exception as e:
        return f"CHYBA: {e}"


# --- AGENTURNÍ PIPELINE ---

def process_product(row):
    p_id = row['ID']
    p_name = row['Nazev_produktu']
    p_category = row['Kategorie']

    # 1. ANALÝZA (Rychlý model)
    tech_info = call_ollama(MODEL_ANALYST, get_analyst_prompt(p_name, p_category), temperature=0.0)
    if "CHYBA" in tech_info:
        print(f"  ! CHYBA ANALYST (ID {p_id}): {tech_info}")
    
    # 2. PSANÍ (Silný model)
    draft = call_ollama(MODEL_WRITER, get_writer_prompt(tech_info, p_name, p_category), temperature=0.7)
    if "CHYBA" in draft:
        print(f"  ! CHYBA WRITER (ID {p_id}): {draft}")
    
    # 3. KOREKTURA (Silný model)
    final_text = call_ollama(MODEL_WRITER, get_corrector_prompt(p_name, tech_info, draft, p_category), temperature=0.1)
    
    # DEBUG: Výpis pro kontrolu, co model skutečně vrací
    print(f"\n--- DEBUG ID: {p_id} ---")
    print(f"RAW OUTPUT:\n{final_text}\n-----------------------")

    return {
        "ID": p_id,
        "Nazev_produktu": p_name,
        "Kategorie": p_category,
        "Popis": final_text
    }

# --- HLAVNÍ LOGIKA ---

def main():
    # Načtení vstupního Excelu
    try:
        # Potlačení warningu openpyxl
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
        
        # Načteme celý soubor bez usecols pro kontrolu sloupců
        df = pd.read_excel(XLSX_PATH)
        
        # Očištění názvů sloupců od mezer
        df.columns = df.columns.str.strip()
        
        # Přejmenování sloupců (cislo -> ID, nazev -> Nazev_produktu, pozn -> Kategorie)
        rename_map = {'cislo': 'ID', 'nazev': 'Nazev_produktu', 'pozn': 'Kategorie'}
        df = df.rename(columns=rename_map)
        
        # Kontrola povinných sloupců
        required_cols = ["ID", "Kategorie", "Nazev_produktu"]
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            print(f"CHYBA: V souboru '{XLSX_PATH}' nebyly nalezeny očekávané sloupce: {missing}")
            print(f"Nalezené sloupce: {list(df.columns)}")
            print("Tip: Zkontrolujte překlepy nebo velikost písmen v hlavičce Excelu.")
            return
            
        # Filtrace jen na potřebné sloupce
        df = df[required_cols]
        
    except Exception as e:
        print(f"Kritická chyba při načítání souboru '{XLSX_PATH}': {e}")
        return
    
    # Získání již zpracovaných ID z XML souboru
    existing_ids = set()
    if os.path.exists(OUTPUT_XML_PATH):
        try:
            with open(OUTPUT_XML_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                # Jednoduchý regex pro nalezení ID v XML
                existing_ids = set(re.findall(r'<id>(.*?)</id>', content))
            print(f"Nalezeno {len(existing_ids)} již hotových popisků v '{OUTPUT_XML_PATH}'.")
        except Exception as e:
            print(f"Chyba při čtení '{OUTPUT_XML_PATH}': {e}")

    # Filtrace produktů ke zpracování
    df['ID_str'] = df['ID'].astype(str)
    to_process_df = df[~df['ID_str'].isin(existing_ids)]
    if LIMIT:
        to_process_df = to_process_df.head(LIMIT)
    to_process = to_process_df.to_dict('records')

    if not to_process:
        print("Všechny produkty jsou již zpracovány.")
        return

    print(f"Zbývá ke generování: {len(to_process)} popisků.")

    # Sekvenční zpracování a okamžitý zápis pro robustnost
    with open(OUTPUT_XML_PATH, 'a', encoding='utf-8') as f:
        # Pokud je soubor prázdný, zapíšeme otevírací tag (pozn: při pádu nebude uzavřen, ale data tam budou)
        if f.tell() == 0:
            f.write("<products>\n")

        for row in tqdm(to_process, desc="Práce agentů"):
            try:
                result = process_product(row)
                
                # Zápis XML fragmentu
                xml_fragment = f"  <product>\n    <id>{result['ID']}</id>\n    <category>{escape(str(result['Kategorie']))}</category>\n    <product_name>{escape(str(result['Nazev_produktu']))}</product_name>\n    <description>{escape(result['Popis'])}</description>\n  </product>\n"
                f.write(xml_fragment)
                f.flush() # Vynucení zápisu na disk
                
            except Exception as e:
                print(f"\nCHYBA při zpracování produktu ID {row['ID']}: {e}")
                f.write(f"  <product>\n    <id>{row['ID']}</id>\n    <error>{escape(str(e))}</error>\n  </product>\n")

    print(f"\nHotovo. Zpracováno {len(to_process)} produktů.")
    print(f"Výsledky jsou uloženy v souboru: {OUTPUT_XML_PATH}")
    print("Poznámka: Pro validní XML může být nutné na konec souboru ručně přidat </products>.")

if __name__ == "__main__":
    main()