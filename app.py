import pandas as pd

data = pd.read_csv("veri.csv")  # Repo ile aynı klasörde olmalı
import streamlit as st

def login():
    st.title("Giriş Yap")
    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")
    
    if username == "tempo" and password == "ozanosmanagaoglu":
        return True
    else:
        st.warning("Kullanıcı adı veya şifre yanlış.")
        return False

if not login():
    st.stop()

import streamlit as st
import pandas as pd
import re

# Sahte veri oluşturma
data = pd.DataFrame({
    "Tempo Kod": ["T-UHCAHE", "T-NQNY5A", "T-BB7M2M", "T-0G5BVS", "T-B07CSU"],
    "Referans Kod 1": ["R1-1UUX5T", "R1-0MDSQN", "R1-U3DWRY", "R1-CQ8QLM", "R1-8NP6P3"],
    "Referans Kod 2": ["R2-PQ1BUZ", "R2-YJBL3M", "R2-KBARME", "R2-7G2RSR", "R2-B1WKHR"]
})

# Kodları normalize eden fonksiyon
def normalize(text):
    if pd.isna(text):
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# Girilen input'un karakterleri sırayla bir metinde olup olmadığını kontrol eden fonksiyon
def is_sequential_match(query, text):
    it = iter(text)
    return all(char in it for char in query)

st.title("Ürün Kodu Arama Arayüzü")

query = st.text_input("Herhangi bir kod girin (Tempo, Referans1, Referans2):")

if query:
    norm_query = normalize(query)
    results = []
    for _, row in data.iterrows():
        for col in data.columns:
            norm_col = normalize(row[col])
            if is_sequential_match(norm_query, norm_col):
                results.append(row)
                break  # Satırda eşleşme varsa diğer sütunlara bakmaya gerek yok

    if results:
        st.success(f"{len(results)} eşleşme bulundu.")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("Eşleşme bulunamadı.")
else:
    st.info("Lütfen bir arama terimi girin.")  
