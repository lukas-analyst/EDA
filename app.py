import streamlit as st
import pandas as pd

# Nastavení stránky
st.set_page_config(layout="wide", page_title="AI Popisky - Kontrola")

# 1. NAČTENÍ DAT
@st.cache_data
def load_data():
    # Zde se načte progress_checkpoint.csv vygenerovaný vaším skriptem
    return pd.read_csv('progress_checkpoint.csv')

df = load_data()

# 2. SIDEBAR - NAVIGACE
with st.sidebar:
    st.title("📦 Správa sortimentu")
    status = st.radio("Zobrazit:", ["K revizi", "Vše k checku", "Schváleno"])
    st.divider()
    search = st.text_input("Hledat produkt (ID/Název)")
    st.progress(0.45, text="Celkový progres: 45%")

# 3. HLAVNÍ PLOCHA
st.header("Detail produktu")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Vstupní data")
    st.info("**Název:** Matice křídlová M 4 ZB lehká")
    st.json({"typ": "matice", "rozmer": "M4", "povrch": "Zinek bílý"})

with col2:
    st.subheader("Editace popisu")
    final_text = st.text_area(
        "AI vygenerovaný text:", 
        value="Zde bude text z Ollamy...", 
        height=300
    )
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🤖 Zkusit znovu (Ollama)", use_container_width=True):
            st.warning("Generuji nový návrh...")
    with c2:
        if st.button("✅ Schválit a další", type="primary", use_container_width=True):
            st.success("Uloženo!")

# 4. PATIČKA
st.divider()
st.caption("Verze 1.0 | Model: Gemma 3:27b | Agenti: Analytik, Copywriter, Korektor")