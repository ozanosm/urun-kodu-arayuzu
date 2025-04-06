import streamlit as st
import pandas as pd
import re
import os

# Giriş kontrolü
def login():
    st.title("Ürün Kodu Arama Arayüzü - Giriş")
    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")
    if username == "admin" and password == "12345":
        return True
    else:
        st.warning("Kullanıcı adı veya şifre yanlış.")
        return False

if not login():
    st.stop()

# Veri yükleme
file_path = "veri.csv"
if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    st.success("Veri başarıyla yüklendi.")
else:
    st.error(f"Dosya bulunamadı: {file_path}")
    st.stop()

# Normalize ve eşleşme fonksiyonları
def normalize(text):
    if pd.isna(text):
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def is_sequential_match(query, text):
    it = iter(text)
    return all(char in it for char in query)

# Arama
st.title("Ürün Kodu Arama")
query = st.text_input("Kod girin (Tempo, Ref1, Ref2):")

if query:
    norm_query = normalize(query)
    results = []
    for _, row in data.iterrows():
        for col in data.columns:
            norm_col = normalize(str(row[col]))
            if is_sequential_match(norm_query, norm_col):
                results.append(row)
                break

    if results:
        st.success(f"{len(results)} eşleşme bulundu.")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("Eşleşme bulunamadı.")
else:
    st.info("Arama yapmak için kod girin.")
