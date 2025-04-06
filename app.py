import streamlit as st
import pandas as pd
import re
import os

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
        "login_ok": {"Türkçe": "🔓 Giriş başarılı", "English": "🔓 Login successful"},
        "search_title": {"Türkçe": "🔎 Kodla Arama", "English": "🔎 Search by Code"},
        "search_input": {"Türkçe": "Bir ürün kodu girin (Tempo, Ref1, Ref2):", "English": "Enter a product code (Tempo, Ref1, Ref2):"},
        "search_found": {"Türkçe": "eşleşme bulundu. Tam eşleşmeler üstte listelenmiştir.", "English": "matches found. Exact matches are listed on top."},
        "search_not_found": {"Türkçe": "Eşleşme bulunamadı.", "English": "No matches found."},
        "search_placeholder": {"Türkçe": "Aramak için bir kod girin.", "English": "Enter a code to search."},
        "about": {"Türkçe": "ℹ️ Hakkımızda", "English": "ℹ️ About Us"},
        "about_link": {"Türkçe": "[TEMPO FİLTRE Resmî Web Sitesi](https://www.tempofiltre.com)", "English": "[Visit TEMPO FILTER Website](https://www.tempofiltre.com)"},
        "promo_video": {"Türkçe": "🎬 Tanıtım Filmimiz", "English": "🎬 Our Promo Video"},
        "search_stats": {"Türkçe": "📊 Arama İstatistikleri", "English": "📊 Search Statistics"},
        "total_searches": {"Türkçe": "Toplam arama sayısı:", "English": "Total number of searches:"},
        "exact_match_count": {"Türkçe": "Tam eşleşme:", "English": "Exact matches:"},
        "partial_match_count": {"Türkçe": "Kısmi eşleşme:", "English": "Partial matches:"},
    }
    return dictionary.get(key, {}).get(language, key)

# Hakkımızda kısmı (yan menüde)
st.sidebar.markdown(t("about"))
st.sidebar.markdown(t("about_link"))
st.sidebar.markdown(t("promo_video"))
st.sidebar.video("https://www.youtube.com/watch?v=I2NFMYQy54k")

# Görseller üstte
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/image.png", width=300)

# Başlık
st.title(t("title"))

# Şifreli Giriş
if "giris" not in st.session_state:
    with st.expander(t("login_title"), expanded=True):
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        if st.button(t("login_button")):
            if username == "tempo" and password == "ozanosmanagaoglu":
                st.session_state["giris"] = True
                st.success(t("login_success"))
                st.stop()
            else:
                st.error(t("login_failed"))
else:
    st.info(t("login_ok"))

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

# Arama istatistikleri için sayaclar
if "search_count" not in st.session_state:
    st.session_state["search_count"] = 0
if "last_exact" not in st.session_state:
    st.session_state["last_exact"] = 0
if "last_partial" not in st.session_state:
    st.session_state["last_partial"] = 0

# Arama Kutusu
st.markdown("---")
st.subheader(t("search_title"))
query = st.text_input(t("search_input"))

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

    st.session_state["search_count"] += 1
    st.session_state["last_exact"] = len(exact_matches)
    st.session_state["last_partial"] = len(partial_matches)

    if results:
        st.success(f"{len(results)} {t('search_found')}")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning(t("search_not_found"))
else:
    st.info(t("search_placeholder"))

# Arama istatistikleri gösterimi
st.markdown("---")
st.subheader(t("search_stats"))
st.write(f"🔁 {t('total_searches')} {st.session_state['search_count']}")
st.write(f"✅ {t('exact_match_count')} {st.session_state['last_exact']}")
st.write(f"🔎 {t('partial_match_count')} {st.session_state['last_partial']}")

# Sayfa altına bauma görseli
st.image("https://raw.githubusercontent.com/ozanosm/urun-kodu-arayuzu/main/bauma.png", use_column_width=True)
