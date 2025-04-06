import streamlit as st
import pandas as pd
import re
import os
import time
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# Dil seçimi (sidebar üzerinden)
language = st.sidebar.radio("🌐 Dil / Language", ["Türkçe", "English"])
st.session_state["lang"] = language

# Çok dilli metin sözlüğü
def t(key):
    dictionary = {
        "title": {"Türkçe": "🔍 Ürün Kodu Arama Arayüzü", "English": "🔍 Product Code Search Interface"},
        "login_title": {"Türkçe": "🔐 Giriş", "English": "🔐 Login"},
        "username": {"Türkçe": "Kullanıcı Adı", "English": "Username"},
        "password": {"Türkçe": "Şifre", "English": "Password"},
        "login_button": {"Türkçe": "Giriş Yap", "English": "Login"},
        "login_success": {"Türkçe": "Giriş başarılı. Sayfa yeniden yüklenemeyecek, lütfen sayfayı manuel yenileyin.", "English": "Login successful. Please manually refresh the page."},
        "login_failed": {"Türkçe": "Kullanıcı adı veya şifre yanlış.", "English": "Incorrect username or password."},
        "search_title": {"Türkçe": "🔎 Kodla Arama", "English": "🔎 Search by Code"},
        "search_input": {"Türkçe": "Bir ürün kodu girin (Tempo, Ref1, Ref2):", "English": "Enter a product code (Tempo, Ref1, Ref2):"},
        "search_found": {"Türkçe": "eşleşme bulundu. Tam eşleşmeler üstte listelenmiştir.", "English": "matches found. Exact matches are listed on top."},
        "search_not_found": {"Türkçe": "Eşleşme bulunamadı.", "English": "No matches found."},
        "search_placeholder": {"Türkçe": "Aramak için bir kod girin.", "English": "Enter a code to search."},
        "recent_searches": {"Türkçe": "🕘 Son Aramalar", "English": "🕘 Recent Searches"},
        "about_link": {"Türkçe": "[TEMPO FİLTRE Resmî Web Sitesi](https://www.tempofiltre.com)", "English": "[Visit TEMPO FILTER Website](https://www.tempofiltre.com)"},
        "dark_mode": {"Türkçe": "🌗 Koyu Tema", "English": "🌗 Dark Mode"},
        "analytics": {"Türkçe": "📈 İçgörü ve Raporlama", "English": "📈 Insights and Reporting"},
        "top_queries": {"Türkçe": "En Çok Aranan Kodlar", "English": "Most Searched Codes"},
        "search_volume": {"Türkçe": "Arama Hacmi (Günlük)", "English": "Search Volume (Daily)"},
        "search_volume_weekly": {"Türkçe": "Arama Hacmi (Haftalık)", "English": "Search Volume (Weekly)"},
        "search_by_hour": {"Türkçe": "Saatlik Arama Dağılımı", "English": "Hourly Search Distribution"},
        "download_logs": {"Türkçe": "📥 Arama Kayıtlarını İndir", "English": "📥 Download Search Logs"}
    }
    return dictionary.get(key, {}).get(language, key)

# Tema seçimi
if "tema" not in st.session_state:
    st.session_state["tema"] = "light"

with st.sidebar:
    st.markdown("---")
    dark_toggle = st.checkbox(t("dark_mode"), value=(st.session_state["tema"] == "dark"))
    if dark_toggle:
        st.session_state["tema"] = "dark"
        st.markdown("""
            <style>
            body { background-color: #0e1117; color: #fafafa; font-family: 'Segoe UI', sans-serif; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.session_state["tema"] = "light"
        st.markdown("""
            <style>
            body { font-family: 'Segoe UI', sans-serif; }
            </style>
        """, unsafe_allow_html=True)

# Sidebar içerikleri
st.sidebar.markdown("---")
st.sidebar.markdown(t("about_link"))
st.sidebar.video("https://www.youtube.com/watch?v=I2NFMYQy54k")

# 📊 İçgörü ve Raporlama Paneli
if st.sidebar.button(t("analytics")):
    st.subheader(t("top_queries"))
    if os.path.exists("arama_log.csv"):
        logs = pd.read_csv("arama_log.csv", names=["timestamp", "query", "matches"])
        logs["timestamp"] = pd.to_datetime(logs["timestamp"])

        top_queries = logs["query"].value_counts().head(10)
        st.bar_chart(top_queries)

        st.subheader(t("search_volume"))
        logs["date"] = logs["timestamp"].dt.date
        volume_daily = logs.groupby("date").size()
        st.line_chart(volume_daily)

        st.subheader(t("search_volume_weekly"))
        logs["week"] = logs["timestamp"].dt.to_period("W").astype(str)
        volume_weekly = logs.groupby("week").size()
        st.line_chart(volume_weekly)

        st.subheader(t("search_by_hour"))
        logs["hour"] = logs["timestamp"].dt.hour
        volume_hour = logs.groupby("hour").size()
        st.bar_chart(volume_hour)

        st.download_button(t("download_logs"), data=logs.to_csv(index=False).encode("utf-8"), file_name="arama_log.csv")
    else:
        st.info("Henüz arama kaydı yok.")
    st.stop()

# Başlık
st.title(t("title"))

# Şifreli Giriş
auth_user = st.secrets["auth"]["username"]
auth_pass = st.secrets["auth"]["password"]

if "giris" not in st.session_state:
    with st.expander(t("login_title"), expanded=True):
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        if st.button(t("login_button")):
            if username == auth_user and password == auth_pass:
                st.session_state["giris"] = True
                st.experimental_rerun()
            else:
                st.error(t("login_failed"))
    st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png", width=300)
    st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_container_width=True)
    st.stop()

st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png", width=300)
show_hidrolik = st.empty()

# Veri Yükleme
file_path = "veri.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines='skip', header=None, delimiter=';')
    data.columns = ["Tempo Kod", "Referans Kod 1", "Referans Kod 2"]
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
    st.stop()

# Yardımcı fonksiyonlar
def normalize(text):
    try:
        return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()
    except Exception:
        return ""

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

st.markdown("---")
st.subheader(t("search_title"))

query = st.text_input(t("search_input"), placeholder="Örn: NTH20495")

suggestions = []
if query:
    query_norm = normalize(query)
    for col in data.columns:
        suggestions.extend(data[col].dropna().astype(str).tolist())
    suggestions = [s for s in set(suggestions) if query_norm in normalize(s)][:10]
    if suggestions:
        st.caption("🔁 Öneriler: " + ", ".join(suggestions))

if query:
    with st.spinner("🔄 Yükleniyor..."):
        time.sleep(0.5)
        norm_query = normalize(query)
        exact_matches = []
        partial_matches = []

        for _, row in data.iterrows():
            for col in data.columns:
                cell_value = row[col]
                if pd.isna(cell_value):
                    continue
                norm_col = normalize(cell_value)
                if norm_col == norm_query:
                    exact_matches.append(row)
                    break
                elif is_sequential_match(norm_query, norm_col):
                    partial_matches.append(row)
                    break

        results = exact_matches + partial_matches

        # Arama log kaydı (sessizce)
        with open("arama_log.csv", "a") as log:
            log.write(f"{datetime.now()},{query},{len(results)}\n")

        if results:
            st.success(f"{len(results)} {t('search_found')}")
            st.dataframe(pd.DataFrame(results))
        else:
            st.warning(t("search_not_found"))

        st.session_state["recent"] = [query] + [q for q in st.session_state["recent"] if q != query][:4]
else:
    st.info(t("search_placeholder"))

if st.session_state["recent"]:
    st.markdown("---")
    st.subheader(t("recent_searches"))
    st.write(", ".join(st.session_state["recent"]))

st.markdown("---")
show_hidrolik.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/hidrolik-filtre.jpg", width=600)
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_container_width=True)
st.markdown("""
    <div style='text-align: center; font-size: 0.85em; color: gray;'>
        © 2025 TEMPO FİLTRE | Design by Ozan
    </div>
""", unsafe_allow_html=True)
