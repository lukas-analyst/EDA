import streamlit as st
import pandas as pd
import os
import sys

# Přidání cesty k agentům do systému, aby šly importovat
sys.path.append(os.path.join(os.path.dirname(__file__), 'Agents'))

# Importování funkcí od vašich agentů
try:
    from Agents.analyst import get_analyst_prompt
    from Agents.writer import get_writer_prompt
    from Agents.corrector import get_corrector_prompt
except ImportError as e:
    st.error(f"Nepodařilo se načíst agenty ze složky Agents: {e}")

# --- KONFIGURACE ---
DB_FILE = 'eda_database.csv'

# --- LOGIKA PRO PŘEGENEROVÁNÍ (Pipeline v EDA) ---

def regenerate_item(product_name):
    """Zavolá kompletní agenturní workflow pro jeden produkt."""
    with st.spinner("Agenti pracují..."):
        # 1. Analýza
        tech_data = get_analyst_prompt(product_name)
        # 2. Psaní
        generated_description = get_writer_prompt(tech_data, product_name)
        # 3. Korektura
        final_description = get_corrector_prompt(product_name, tech_data, generated_description)
        return final_description, tech_data

# --- INICIALIZACE DAT (Upraveno) ---

def load_eda_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        st.error("Databáze EDA nebyla nalezena. Spusťte nejdříve 'generate_description.py'.")
        return pd.DataFrame()

# --- SESSION STATE ---
if 'df' not in st.session_state:
    st.session_state.df = load_eda_data()

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- HLAVNÍ ROZHRANÍ (Navigace) ---
st.set_page_config(page_title="EDA - Enrich Description App", layout="wide")

if not st.session_state.df.empty:
    df = st.session_state.df
    idx = st.session_state.current_idx
    
    # Navigační panel
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_l:
        if st.button("⬅️ Předchozí"):
            if idx > 0: st.session_state.current_idx -= 1; st.rerun()
    with col_m:
        st.write(f"Produkt {idx + 1} / {len(df)}")
    with col_r:
        if st.button("Další ➡️"):
            if idx < len(df) - 1: st.session_state.current_idx += 1; st.rerun()
            
# Získání dat aktuálního produktu
item = st.session_state.df.iloc[st.session_state.current_idx]

st.divider()

# Rozvržení: Kontext vs. Editor
col_context, col_editor = st.columns([1, 2], gap="large")

with col_context:
    st.subheader("🔍 Technický kontext")
    st.caption("Data extrahovaná Agentem Analytikem")
    
    # Zobrazení názvu produktu jako hlavního záchytného bodu
    st.info(f"**Původní název:**\n\n{item['product_name']}")
    
    # Pokusíme se zobrazit technická data (předpokládáme, že jsou uložena v JSON nebo stringu)
    # Pokud váš generovací skript ukládá i tech_data, zobrazíme je zde
    if 'tech_data' in item and pd.notna(item['tech_data']):
        try:
            st.json(item['tech_data'])
        except:
            st.code(item['tech_data'], language="text")
    else:
        st.warning("Technická data nejsou k dispozici. Spusťte analýzu.")

    # Tlačítko pro kompletní refresh tohoto jednoho produktu
    if st.button("🤖 Přegenerovat vše (Ollama)", use_container_width=True):
        new_text, new_tech = regenerate_item(item['product_name'])
        
        # Aktualizace session_state
        st.session_state.df.at[st.session_state.current_idx, 'description'] = new_text
        if 'tech_data' in st.session_state.df.columns:
            st.session_state.df.at[st.session_state.current_idx, 'tech_data'] = str(new_tech)
        
        st.session_state.df.at[st.session_state.current_idx, 'eda_status'] = 'Upraveno AI'
        st.session_state.df.to_csv(DB_FILE, index=False)
        st.rerun()

with col_editor:
    st.subheader("✍️ Editor popisu")
    
    # Text area pro editaci
    # Používáme st.text_area, změna se projeví po stisku Ctrl+Enter nebo kliknutí mimo
    edited_description = st.text_area(
        "Finální text popisku:",
        value=item['description'] if pd.notna(item['description']) else "",
        height=450,
        key=f"desc_{st.session_state.current_idx}"
    )

    # Logika ukládání při změně textu
    if edited_description != item['description']:
        st.session_state.df.at[st.session_state.current_idx, 'description'] = edited_description
        st.session_state.df.at[st.session_state.current_idx, 'eda_status'] = 'Upraveno expertem'
        st.session_state.df.to_csv(DB_FILE, index=False)
        st.toast("Změny uloženy", icon="💾")

    # Akční tlačítka pod editorem
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ SCHVÁLIT A DALŠÍ", type="primary", use_container_width=True):
            st.session_state.df.at[st.session_state.current_idx, 'eda_status'] = 'Schváleno'
            st.session_state.df.to_csv(DB_FILE, index=False)
            if st.session_state.current_idx < len(st.session_state.df) - 1:
                st.session_state.current_idx += 1
                st.rerun()
            else:
                st.success("Dosáhli jste konce seznamu!")
                
    with c2:
        if st.button("⚠️ Označit k revizi", use_container_width=True):
            st.session_state.df.at[st.session_state.current_idx, 'eda_status'] = 'Vyžaduje kontrolu'
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.info("Označeno k revizi.")
            
with st.sidebar:
    st.header("📊 Statistiky projektu")
    
    # Výpočet statistik
    total_count = len(st.session_state.df)
    approved_count = len(st.session_state.df[st.session_state.df['eda_status'] == 'Schváleno'])
    needs_review_count = len(st.session_state.df[st.session_state.df['eda_status'] == 'Vyžaduje kontrolu'])
    progress = approved_count / total_count if total_count > 0 else 0
    
    st.metric("Schváleno", f"{approved_count} / {total_count}", f"{progress:.1%}")
    st.progress(progress)
    
    if needs_review_count > 0:
        st.warning(f"⚠️ K revizi: {needs_review_count} položek")

    st.divider()
    
    st.header("🔍 Filtry fronty")
    # Filtr, který ovlivní, jaké produkty se budou nabízet k listování
    filter_mode = st.selectbox(
        "Zobrazit produkty:",
        ["Všechny", "Pouze nové / AI upravené", "Pouze k revizi", "Pouze schválené"]
    )
    
    # Aplikace filtru na indexy
    if filter_mode == "Pouze nové / AI upravené":
        filtered_indices = st.session_state.df[st.session_state.df['eda_status'].isin(['Nové', 'Upraveno AI'])].index.tolist()
    elif filter_mode == "Pouze k revizi":
        filtered_indices = st.session_state.df[st.session_state.df['eda_status'] == 'Vyžaduje kontrolu'].index.tolist()
    elif filter_mode == "Pouze schválené":
        filtered_indices = st.session_state.df[st.session_state.df['eda_status'] == 'Schváleno'].index.tolist()
    else:
        filtered_indices = st.session_state.df.index.tolist()

    # Rychlý skok na index v rámci filtru
    if filtered_indices:
        st.caption(f"V tomto filtru je {len(filtered_indices)} položek.")
    else:
        st.error("Žádné položky neodpovídají filtru.")

    st.divider()

    st.header("📤 Export dat")
    if st.button("🚀 Generovat finální Excel", use_container_width=True):
        # Příprava dat pro export (vybereme jen schválené nebo vše, podle potřeby)
        export_df = st.session_state.df[st.session_state.df['eda_status'] == 'Schváleno']
        
        if not export_df.empty:
            output_file = 'Website/Sortiment/Products/Description/EDA_FINAL_EXPORT.xlsx'
            export_df.to_excel(output_file, index=False)
            st.success(f"Exportováno {len(export_df)} schválených položek!")
            st.balloons()
        else:
            st.error("Není co exportovat. Nejdříve schvalte nějaké popisky.")

# --- ÚPRAVA NAVIGACE (Aby respektovala filtry) ---
# Tuto část vložíme do horní navigace z Části 1

def next_filtered():
    current_idx = st.session_state.current_idx
    # Najdeme nejbližší vyšší index ve filtrovaném seznamu
    next_idx_list = [i for i in filtered_indices if i > current_idx]
    if next_idx_list:
        st.session_state.current_idx = next_idx_list[0]
    else:
        st.toast("Jste na konci filtrovaného seznamu")

def prev_filtered():
    current_idx = st.session_state.current_idx
    # Najdeme nejbližší nižší index ve filtrovaném seznamu
    prev_idx_list = [i for i in filtered_indices if i < current_idx]
    if prev_idx_list:
        st.session_state.current_idx = prev_idx_list[-1]
    else:
        st.toast("Jste na začátku filtrovaného seznamu")