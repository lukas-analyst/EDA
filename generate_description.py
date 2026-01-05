import pandas as pd
import requests
import os
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Importy vašich agentů
from Agents.analyst import get_analyst_prompt
from Agents.writer import get_writer_prompt
from Agents.corrector import get_corrector_prompt

# --- KONFIGURACE ---
XLSX_PATH = 'Sortiment/sortiment.xlsx'
DESCRIPTIONS_DIR = 'Descriptions'

# Hybridní nastavení modelů pro efektivitu
MODEL_ANALYST = "gemma3:1b"   # Rychlý pro technická data
MODEL_WRITER = "gemma3:1b"    # Kvalitní pro text (zde máte nastaveno 1b pro test, pro ostrou verzi dejte 27b)
OLLAMA_URL = "http://localhost:11434/api/generate"

MAX_WORKERS = 1  # Počet paralelních agentů
LIMIT = 20     # Změňte na číslo (např. 10) pro test, None pro vše

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
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"CHYBA: {e}"

# --- AGENTURNÍ PIPELINE ---

def process_product(row):
    p_id = row['product_id']
    p_name = row['product_name']
    p_category = row['category']
    
    filename = f"{p_id}.md"
    filepath = os.path.join(DESCRIPTIONS_DIR, filename)

    # 1. ANALÝZA (Rychlý model)
    tech_info = call_ollama(MODEL_ANALYST, get_analyst_prompt(p_name, p_category), temperature=0.0)
    print(f"Produkt ID {p_id} - Technická data: \n {tech_info}")
    
    # 2. PSANÍ (Silný model)
    draft = call_ollama(MODEL_WRITER, get_writer_prompt(tech_info, p_name, p_category), temperature=0.7)
    print(f"Produkt ID {p_id} - Návrh popisu: \n {draft}")
    
    # 3. KOREKTURA (Silný model)
    final_text = call_ollama(MODEL_WRITER, get_corrector_prompt(p_name, tech_info, draft, p_category), temperature=0.1)
    print(f"Produkt ID {p_id} - Finální popis: \n {final_text}")

    # Zápis přímo na disk
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_text)
    
    return p_id

# --- HLAVNÍ LOGIKA ---

def main():
    # Vytvoření složky
    if not os.path.exists(DESCRIPTIONS_DIR):
        os.makedirs(DESCRIPTIONS_DIR)

    # Načtení Excelu - UPRAVENO PRO 3 SLOUPCE
    # Předpokládáme pořadí: A=ID, B=Název, C=Kategorie (indexy 0, 1, 2)
    try:
        df = pd.read_excel(XLSX_PATH, sheet_name='Zbozi', usecols=[0, 1, 2])
        df.columns = ['product_id', 'product_name', 'category']
    except ValueError as e:
        print(f"Chyba při načítání sloupců. Zkontrolujte, zda má Excel 3 sloupce. Detail: {e}")
        return
    
    if LIMIT:
        df = df.sample(n=LIMIT)

    # Detekce hotových souborů (podle ID)
    existing_files = os.listdir(DESCRIPTIONS_DIR)
    # Očistíme názvy souborů o koncovku .md, abychom mohli porovnávat s ID
    existing_ids = [f.replace('.md', '') for f in existing_files if f.endswith('.md')]
    
    print(f"Nalezeno {len(existing_ids)} již hotových popisků.")
    
    # Filtrace produktů ke zpracování
    # Převedeme ID na string pro bezpečné porovnání
    to_process = df[~df['product_id'].astype(str).isin(existing_ids)].to_dict('records')

    if not to_process:
        print("Všechny produkty jsou již vygenerovány ve složce Descriptions.")
        return

    print(f"Generování {len(to_process)} popisků...")
    print(f"Generování pro tyto produkty: {[item['product_id'] for item in to_process]}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(tqdm(executor.map(process_product, to_process), total=len(to_process), desc="Práce agentů"))

    print(f"Hotovo. Vygenerováno {len(to_process)} popisků.")

if __name__ == "__main__":
    main()