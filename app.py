import streamlit as st
import pandas as pd
import re
import os

# Sayfa yapılandırması
st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# Başlık
st.title("🔍 Ürün Kodu Arama Arayüzü")

# Şifreli Giriş
if "giris" not in st.session_state:
    with st.expander("🔐 Giriş", expanded=True):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if username == "admin" and password == "12345":
                st.session_state["giris"] = True
                st.success("Giriş başarılı. Sayfa yeniden yüklenemeyecek, lütfen sayfayı manuel yenileyin.")
                st.stop()
            else:
                st.error("Kullanıcı adı veya şifre yanlış.")
else:
    st.info("🔓 Giriş başarılı")

if "giris" not in st.session_state:
    st.stop()

# Veri Yükleme
file_path = "veri.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines='skip')
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
    st.stop()

# Güvenli normalize fonksiyonu
def normalize(text):
    try:
        return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()
    except Exception:
        return ""

# Sıralı karakter eşleşmesi kontrolü
def is_sequential_match(query, text):
    index = 0
    for char in query:
        index = text.find(char, index)
        if index == -1:
            return False
        index += 1
    return True

# Arama Kutusu
st.markdown("---")
st.subheader("🔎 Kodla Arama")
query = st.text_input("Bir ürün kodu girin (Tempo, Ref1, Ref2):")

if query:
    norm_query = normalize(query)
    results = []

    for _, row in data.iterrows():
        matched = False
        for col in data.columns:
            cell_value = row[col]
            if pd.isna(cell_value):
                continue
            norm_col = normalize(cell_value)
            if is_sequential_match(norm_query, norm_col):
                matched = True
                break

        if matched:
            results.append(row)

    if results:
        st.success(f"{len(results)} eşleşme bulundu.")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("Eşleşme bulunamadı.")
else:
    st.info("Aramak için bir kod girin.")
