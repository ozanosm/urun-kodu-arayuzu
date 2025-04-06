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
try:
    data = pd.read_csv(file_path, on_bad_lines='skip')  # Bozuk satırları atla
    st.success("Veri başarıyla yüklendi.")
    st.write("Veri önizleme:")
    st.dataframe(data.head())
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
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
    exact_match = None
    partial_matches = []

    for _, row in data.iterrows():
        for col in data.columns:
            norm_col = normalize(str(row[col]))

            # Öncelik: Tam eşleşme
            if norm_col == norm_query:
                exact_match = [row]
                break

            # Tam eşleşme yoksa: Sıralı karakter eşleşmesi
            elif is_sequential_match(norm_query, norm_col):
                partial_matches.append(row)
                break

        if exact_match:
            break  # Tam eşleşme bulunduysa döngüyü sonlandır

    if exact_match:
        st.success("Tam eşleşme bulundu.")
        st.dataframe(pd.DataFrame(exact_match))
    elif partial_matches:
        st.info(f"{len(partial_matches)} sıralı eşleşme bulundu.")
        st.dataframe(pd.DataFrame(partial_matches))
    else:
        st.warning("Eşleşme bulunamadı.")
else:
    st.info("Arama yapmak için kod girin.")
