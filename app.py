import streamlit as st
import pandas as pd
import re
import os

# Sayfa yapılandırması
st.set_page_config(page_title="Ürün Kodu Arama", layout="wide")

# Görseller (GitHub üzerinden raw linklerle)
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png", width=300)
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", width=700)

# Başlık
st.title("🔍 Ürün Kodu Arama Arayüzü")

# Şifreli Giriş
if "giris" not in st.session_state:
    with st.expander("🔐 Giriş", expanded=True):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if username == "tempo" and password == "ozanosmanagaoglu":
                st.session_state["giris"] = True
                st.success("Giriş başarılı. Sayfa yeniden yüklenemeyecek, lütfen sayfayı manuel yenileyin.")
                st.stop()
            else:
                st.error("Kullanıcı adı veya şifre yanlış.")
else:
    st.info("🔓 Giriş başarılı")

if "giris" not in st.session_state:
    st.stop()

# Veri Yükleme (ilk satır başlık değil, ; ile ayrılmış)
file_path = "veri.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines='skip', header=None, delimiter=';')
    data.columns = ["Tempo Kod", "Referans Kod 1", "Referans Kod 2"]
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

    if results:
        st.success(f"{len(results)} eşleşme bulundu. Tam eşleşmeler üstte listelenmiştir.")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("Eşleşme bulunamadı.")
else:
    st.info("Aramak için bir kod girin.")
