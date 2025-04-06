import streamlit as st
import pandas as pd
import re
import os

# Sayfa yapılandırması
st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# Başlık
st.title("🔍 Ürün Kodu Arama Arayüzü")

# Şifreli Giriş
with st.expander("🔐 Giriş" if "giris" not in st.session_state else "🔓 Giriş başarılı", expanded="giris" not in st.session_state):
    username = st.text_input("Kullanıcı Adı", key="username")
    password = st.text_input("Şifre", type="password", key="password")
    if st.button("Giriş Yap"):
        if username == "admin" and password == "12345":
            st.session_state["giris"] = True
            st.experimental_rerun()
        else:
            st.error("Kullanıcı adı veya şifre yanlış.")

if "giris" not in st.session_state:
    st.stop()

# Veri Yükleme
file_path = "veri.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines='skip')
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
    st.stop()

# Normalize fonksiyonu (büyük/küçük harf, boşluk, sembol fark etmez)
def normalize(text):
    if pd.isna(text):
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

# Sıralı karakter eşleşmesi kontrolü (örn. nth2049 → nth20495)
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
        row_match = False
        for col in data.columns:
            norm_col = normalize(row[col])
            if is_sequential_match(norm_query, norm_col):
                row_match = True
                break  # Bir sütun eşleşiyorsa, satır sonuçlara girer

        if row_match:
            results.append(row)

    if results:
        st.success(f"{len(results)} eşleşme bulundu.")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("Eşleşme bulunamadı.")
else:
    st.info("Aramak için bir kod girin.")
