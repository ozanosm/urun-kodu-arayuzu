import streamlit as st
import pandas as pd
import re
import os
import time
from datetime import datetime

st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# Stil: daha az scroll için sıkıştırılmış yapı
st.markdown("""
    <style>
    section.main > div { padding-top: 10px; padding-bottom: 10px; }
    .block-container { padding-top: 1rem; padding-bottom: 0.5rem; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .stTextInput > div > div > input { height: 3rem; font-size: 1.1rem; }
    .stButton button { padding: 0.5rem 1.5rem; font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

# Üst logo ve başlık
st.markdown("""
    <div style='display: flex; align-items: center; gap: 1rem;'>
        <img src='https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png' width='160'>
        <h1 style='margin: 0;'>🔍 Ürün Kodu Arama Arayüzü</h1>
    </div>
    <hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>
""", unsafe_allow_html=True)

# Sidebar ayarlar
st.sidebar.header("⚙️ Ayarlar")
language = st.sidebar.radio("🌐 Dil / Language", ["Türkçe", "English"])
st.session_state["lang"] = language

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
        "dark_mode": {"Türkçe": "🌗 Koyu Tema", "English": "🌗 Dark Mode"}
    }
    return dictionary.get(key, {}).get(language, key)

# Tema ayarı (en alt)
st.sidebar.markdown("---")
if "tema" not in st.session_state:
    st.session_state["tema"] = "light"
if st.sidebar.checkbox(t("dark_mode"), value=(st.session_state["tema"] == "dark")):
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

# Şifreli giriş kontrolü
auth_user = st.secrets["auth"]["username"]
auth_pass = st.secrets["auth"]["password"]

if "giris" not in st.session_state:
    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    if st.button(t("login_button")):
        if username == auth_user and password == auth_pass:
            st.session_state["giris"] = True
            st.success(t("login_success"))
            st.stop()
        else:
            st.error(t("login_failed"))
    st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_container_width=True)
    st.stop()

# Giriş başarılıysa burada uygulama devam eder...
# Buradan sonrası arama kutusu, sonuç gösterimi ve loglama gibi bileşenlerle tamamlanır.
