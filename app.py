import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# === Stil Tanımları ===
st.markdown("""
    <style>
    section.main > div { padding-top: 10px; padding-bottom: 10px; }
    .block-container { padding-top: 1rem; padding-bottom: 0.5rem; transition: all 0.4s ease-in-out; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; transition: all 0.4s ease-in-out; opacity: 0; animation: fadeIn 1s ease-in-out forwards; }
    .stTextInput > div > div > input { height: 3rem; font-size: 1.1rem; }
    .stButton button { padding: 0.5rem 1.5rem; font-size: 1rem; }
    img.logo { display: block; margin-left: auto; margin-right: auto; margin-top: 10px; margin-bottom: 10px; }
    img:hover { transform: scale(1.03); transition: 0.3s ease-in-out; }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# === Sidebar: Dil ve Tema ===
st.sidebar.header("⚙️ Ayarlar / Settings")
language = st.sidebar.radio("🌐 Dil / Language", ["Türkçe", "English"])
st.session_state["lang"] = language

# === Çeviri Fonksiyonu ===
try:
    with open("lang.json", "r", encoding="utf-8") as f:
        translations = json.load(f)
except FileNotFoundError:
    st.error("Çeviri dosyası (lang.json) bulunamadı.")
    st.stop()

def t(key):
    return translations.get(key, {}).get(language, key)

# === Logo ===
st.markdown("""
    <img src='https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png' width='180' class='logo'>
""", unsafe_allow_html=True)

# === Sidebar Bağlantılar ===
st.sidebar.markdown("[🌐 TEMPO FİLTRE Web Sitesi](https://www.tempofiltre.com)")
st.sidebar.video("https://www.youtube.com/watch?v=I2NFMYQy54k")

# === Tema Seçimi ===
if "tema" not in st.session_state:
    st.session_state["tema"] = "light"
if st.sidebar.checkbox(t("dark_mode"), value=(st.session_state["tema"] == "dark")):
    st.session_state["tema"] = "dark"
    st.markdown("""
        <style>
        body, .stApp { background-color: #0e1117 !important; color: #fafafa; }
        .stTextInput input { background-color: #262730; color: white; }
        .stButton button { background-color: #444; color: white; border: none; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.session_state["tema"] = "light"
    st.markdown("""
        <style>
        body, .stApp { background-color: white; color: black; }
        </style>
    """, unsafe_allow_html=True)

# === Başlık ===
st.markdown(f"<h1 style='text-align: center;'>{t('title')}</h1><hr>", unsafe_allow_html=True)

# === Giriş ===
if "giris" not in st.session_state:
    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    if st.button(t("login_button")):
        if username == "tempo" and password == "ozanosmanagaoglu":
            st.session_state["giris"] = True
            st.rerun()
        else:
            st.error(t("login_failed"))
    st.stop()

# === Veri Yükleme ===
file_path = "veri.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines='skip', header=None, delimiter=';')
    data.columns = [t("tempo_code"), t("ref1_code"), t("ref2_code")]
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
    st.stop()

# === Fonksiyonlar ===
def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def is_sequential_match(query, text):
    index = 0
    for char in query:
        index = text.find(char, index)
        if index == -1:
            return False
        index += 1
    return True

# === Arama Alanı ===
query = st.text_input(t("search_input"), placeholder="NTH20495")
if not query:
    st.info(t("search_input"))

if query:
    norm_query = normalize(query)
    exact_matches, partial_matches = [], []

    for _, row in data.iterrows():
        for col in data.columns:
            val = row[col]
            if pd.isna(val): continue
            norm_val = normalize(val)
            if norm_val == norm_query:
                exact_matches.append(row)
                break
            elif is_sequential_match(norm_query, norm_val):
                partial_matches.append(row)
                break

    results = exact_matches + partial_matches
    with open("arama_log.csv", "a") as log:
        log.write(f"{datetime.now()},{query},{len(results)}\n")

    if results:
        st.success(f"{len(results)} {t('search_found')}")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning(t("search_not_found"))

    if "recent" not in st.session_state:
        st.session_state["recent"] = []
    st.session_state["recent"] = [query] + [q for q in st.session_state["recent"] if q != query][:4]

# === Son Aramalar ===
if st.session_state.get("recent"):
    st.markdown("---")
    st.subheader(t("recent_searches"))
    st.write(", ".join(st.session_state["recent"]))

# === Alt Görsel ===
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_container_width=True)

# === Footer ===
st.markdown("""
    <div style='text-align: center; font-size: 0.85em; color: gray;'>
        © 2025 TEMPO FİLTRE | Design by Ozan
    </div>
""", unsafe_allow_html=True)
