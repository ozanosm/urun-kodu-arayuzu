import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# === Stil ===
st.markdown("""
    <style>
    section.main > div { padding-top: 10px; padding-bottom: 10px; }
    .block-container { padding-top: 1rem; padding-bottom: 0.5rem; transition: all 0.4s ease-in-out; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; transition: all 0.4s ease-in-out; opacity: 0; animation: fadeIn 1s ease-in-out forwards; }
    .stTextInput > div > div > input { height: 3rem; font-size: 1.1rem; }
    .stButton button { padding: 0.5rem 1.5rem; font-size: 1rem; }
    img { transition: transform 0.3s ease-in-out; }
    img:hover { transform: scale(1.03); }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# === Sidebar Ayarları ===
st.sidebar.header("⚙️ Ayarlar")
language = st.sidebar.radio("🌐 Dil / Language", ["Türkçe", "English"])
st.session_state["lang"] = language

def t(key):
    dictionary = {
        "title": {"Türkçe": "🔍 Ürün Kodu Arama Arayüzü", "English": "🔍 Product Code Search Interface"},
        "username": {"Türkçe": "Kullanıcı Adı", "English": "Username"},
        "password": {"Türkçe": "Şifre", "English": "Password"},
        "login_button": {"Türkçe": "Giriş Yap", "English": "Login"},
        "login_success": {"Türkçe": "Giriş başarılı.", "English": "Login successful."},
        "login_failed": {"Türkçe": "Kullanıcı adı veya şifre yanlış.", "English": "Incorrect username or password."},
        "search_input": {"Türkçe": "Bir ürün kodu girin (Tempo, Ref1, Ref2):", "English": "Enter a product code (Tempo, Ref1, Ref2):"},
        "search_found": {"Türkçe": "eşleşme bulundu.", "English": "matches found."},
        "search_not_found": {"Türkçe": "Eşleşme bulunamadı.", "English": "No matches found."},
        "recent_searches": {"Türkçe": "🕘 Son Aramalar", "English": "🕘 Recent Searches"},
        "dark_mode": {"Türkçe": "🌗 Koyu Tema", "English": "🌗 Dark Mode"},
        "insights": {"Türkçe": "📈 İçgörü ve Raporlama", "English": "📈 Insights & Reporting"},
        "download_logs": {"Türkçe": "📥 Arama Kayıtlarını İndir", "English": "📥 Download Search Logs"},
        "page": {"Türkçe": "🗂️ Sayfa", "English": "🗂️ Page"}
    }
    return dictionary.get(key, {}).get(language, key)

page = st.sidebar.radio(t("page"), ["🔍 Arama", "📊 İçgörü"])

st.sidebar.markdown("[🌐 TEMPO FİLTRE Web Sitesi](https://www.tempofiltre.com)")
st.sidebar.video("https://www.youtube.com/watch?v=I2NFMYQy54k")
st.sidebar.markdown("---")

if "tema" not in st.session_state:
    st.session_state["tema"] = "light"
if st.sidebar.checkbox(t("dark_mode"), value=(st.session_state["tema"] == "dark")):
    st.session_state["tema"] = "dark"
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: #fafafa; font-family: 'Segoe UI', sans-serif; transition: background-color 0.4s ease-in-out, color 0.4s ease-in-out; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.session_state["tema"] = "light"
    st.markdown("""
        <style>
        body { font-family: 'Segoe UI', sans-serif; transition: background-color 0.4s ease-in-out, color 0.4s ease-in-out; }
        </style>
    """, unsafe_allow_html=True)

# === Logo ve Başlık ===
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png' width='200'>
        <h1 style='margin-top: 0.2em;'>🔍 Ürün Kodu Arama Arayüzü</h1>
    </div>
    <hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>
""", unsafe_allow_html=True)

# === Şifreli Giriş ===
auth_user = st.secrets["auth"]["username"]
auth_pass = st.secrets["auth"]["password"]

if "giris" not in st.session_state:
    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    if st.button(t("login_button")):
        if username == auth_user and password == auth_pass:
            st.session_state["giris"] = True
            st.success(t("login_success"))
            st.rerun()
        else:
            st.error(t("login_failed"))
    st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_container_width=True)
    st.stop()

# === Veri Yükleme ===
file_path = "veri.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines='skip', header=None, delimiter=';')
    data.columns = ["Tempo Kod", "Referans Kod 1", "Referans Kod 2"]
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
    st.stop()

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

if "recent" not in st.session_state:
    st.session_state["recent"] = []

# === İçgörü Sayfası ===
if page == "📊 İçgörü":
    st.subheader("📊 Arama Verileri")
    if os.path.exists("arama_log.csv"):
        df = pd.read_csv("arama_log.csv", names=["Tarih", "Kod", "Sonuç"])
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        df["Gün"] = df["Tarih"].dt.date
        top_codes = df["Kod"].value_counts().head(10)
        daily = df.groupby("Gün").size()

        st.write("🔝 En Çok Aranan Kodlar")
        st.bar_chart(top_codes)

        st.write("📅 Günlük Arama Hacmi")
        st.line_chart(daily)

        st.download_button(t("download_logs"), df.to_csv(index=False).encode("utf-8"), file_name="arama_log.csv")
    else:
        st.info("Henüz arama kaydı bulunamadı.")
    st.stop()

# === Arama Kutusu ===
query = st.text_input(t("search_input"), placeholder="Örn: NTH20495")

# === Öneri Sistemi ===
if query:
    norm_query = normalize(query)
    suggestions = []
    for col in data.columns:
        suggestions.extend(data[col].dropna().astype(str).tolist())
    suggestions = [s for s in set(suggestions) if norm_query in normalize(s)][:10]
    if suggestions:
        st.caption("🔁 Öneriler: " + ", ".join(suggestions))

# === Arama Motoru ===
if query:
    norm_query = normalize(query)
    exact_matches, partial_matches = [], []

    for _, row in data.iterrows():
        for col in data.columns:
            cell_value = row[col]
            if pd.isna(cell_value): continue
            norm_col = normalize(cell_value)
            if norm_col == norm_query:
                exact_matches.append(row)
                break
            elif is_sequential_match(norm_query, norm_col):
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

    st.session_state["recent"] = [query] + [q for q in st.session_state["recent"] if q != query][:4]
else:
    st.info("Arama için kod girin.")

# === Son Aramalar ===
if st.session_state["recent"]:
    st.markdown("---")
    st.subheader(t("recent_searches"))
    st.write(", ".join(st.session_state["recent"]))

# === Alt Görsel ve Footer ===
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_container_width=True)
st.markdown("""
    <div style='text-align: center; font-size: 0.85em; color: gray;'>
        © 2025 TEMPO FİLTRE | Design by osm
    </div>
""", unsafe_allow_html=True)
