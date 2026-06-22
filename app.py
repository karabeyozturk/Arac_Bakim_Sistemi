import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

# Sayfa genel ayarlari
st.set_page_config(page_title="Premium Arac Yonetimi", page_icon="腔", layout="wide")

# Veritabani baglantisinin kurulmasi
conn = baglanti_olustur()
cursor = conn.cursor()

# Sayfa ustu bosluk optimizasyonu için temel stil tanımı
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    div[data-testid="metric-container"] {
        background-color: #1a1c24;
        border: 1px solid #2b2e40;
        border-radius: 12px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Yatay Ust Menu Navigasyonu
secim = option_menu(
    menu_title=None,
    options=["Dashboard", "Yeni Arac Ekle", "Bakim/Masraf Isle", "Finansal Rapor", "Akilli Uyari Sistemi"],
    icons=["activity", "car-front-fill", "tools", "wallet2", "bell-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#0e1117"},
        "icon": {"color": "#4A90E2", "font-size": "16px"},
        "nav-link": {"font-size": "15px", "text-align": "center", "margin": "0px", "--hover-color": "#1a1c24"},
        "nav-link-selected": {"background-color": "#4A90E2", "color": "white"}
    }
)

st.markdown("---")

# Mizanpaj ve Modul Kontrolleri
if secim == "Dashboard":
    st.markdown("### 📊 Sistem Ozet Paneli")
    
    cursor.execute("SELECT COUNT(*) FROM araclar")
    toplam_arac = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(maliyet) FROM bakimlar")
    toplam_maliyet = cursor.fetchone()[0] or 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Kayitli Toplam Arac", value=f"{toplam_arac} Adet")
    col2.metric(label="Toplam Bakim Gideri", value=f"{toplam_maliyet:,.2f} 兆")
    col3.metric(label="Sistem Durumu", value="Aktif")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    df_grafik = pd.read_sql_query("SELECT plaka, SUM(maliyet) as toplam FROM bakimlar GROUP BY plaka", conn)
    
    if not df_grafik.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("##### Harcama Dagilimi")
            fig_pie = px.pie(df_grafik, values='toplam', names='plaka', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_g2:
            st.markdown("##### Gider Karsilastirmasi")
            fig_bar = px.bar(df_grafik, x='plaka', y='toplam', text_auto=True, color='plaka')
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Grafiklerin yuklenmesi icin sisteme arac ve bakim kaydi girilmesi gerekmektedir.")

elif secim == "Yeni Arac Ekle":
    st.markdown("### 🏎️ Yeni Arac Kayit Modulu")
    
    with st.form("arac_ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            plaka = st.text_input("Arac Plakasi").upper()
            marka = st.text_input("Marka")
        with col2:
            model = st.text_input("Model")
            km = st.number_input("Guncel Kilometre", min_value=0, step=1)
            
        submit = st.form_submit_button("Sisteme Kaydet", use_container_width=True)
        
        if submit:
            if plaka and marka and model:
                try:
                    yeni_arac = Arac(plaka, marka, model, km)
                    cursor.execute("INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)",
                                   (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre))
                    conn.commit()
                    st.success(f"{plaka} plakali arac basariyla kaydedildi.")
                except sqlite3.IntegrityError:
                    st.error("Bu plaka sistemde zaten kayitli.")
            else:
                st.warning("Lutfen tum alanlari doldurunuz.")

elif secim == "Bakim/Masraf Isle":
    st.markdown("### 🔧 Bakim ve Masraf Girisi")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]
    
    if not plaka_listesi:
        st.info("Sistemde kayitli arac bulunmamaktadir.")
    else:
        with st.form("bakim_ekle_form", clear_on_submit=True):
            secilen_plaka = st.selectbox("Arac Seciniz:", plaka_listesi)
            islem_turu = st.text_input("Yapilan Islem")
            
            col1, col2 = st.columns(2)
            with col1:
                islem_km = st.number_input("Islem Kilometresi", min_value=0, step=1)
            with col2:
                maliyet = st.number_input("Maliyet (TL)", min_value=0.0, step=50.0)
                
            submit = st.form_submit_button("Veriyi Kaydet", use_container_width=True)
            
            if submit:
                if islem_turu:
                    yeni_bakim = BakimKaydi(secilen_plaka, islem_turu, islem_km, maliyet)
                    cursor.execute("INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
                                   (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih))
                    cursor.execute("UPDATE araclar SET kilometre = ? WHERE plaka = ?", (islem_km, secilen_plaka))
                    conn.commit()
                    st.success("Bakim kaydi basariyla eklendi.")
                else:
                    st.warning("Islem turu bos birakilamaz.")

elif secim == "Finansal Rapor":
    st.markdown("### 📋 Finansal Raporlama")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]
    
    if not plaka_listesi:
        st.info("Sistemde arac bulunmuyor.")
    else:
        secilen_plaka = st.selectbox("Arac Seciniz:", plaka_listesi)
        
        df = pd.read_sql_query("SELECT tarih, islem_turu, kilometre, maliyet FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC", conn, params=(secilen_plaka,))
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            toplam_harcama = df['maliyet'].sum()
            st.metric(label="Toplam Gider", value=f"{toplam_harcama:,.2f} 兆")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 CSV Indir", data=csv, file_name=f'{secilen_plaka}_rapor.csv', mime='text/csv')
        else:
            st.info("Bu araca ait kayit bulunmamaktadir.")

elif secim == "Akilli Uyari Sistemi":
    st.markdown("### 🚨 Akilli Kontrol Paneli")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]
    
    if not plaka_listesi:
        st.info("Arac bulunamadi.")
    else:
        secilen_plaka = st.selectbox("Arac Seciniz:", plaka_listesi)
        
        cursor.execute("SELECT kilometre FROM araclar WHERE plaka = ?", (secilen_plaka,))
        guncel_km = cursor.fetchone()[0]
        
        cursor.execute("SELECT kilometre FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1", (secilen_plaka,))
        son_bakim = cursor.fetchone()
        
        if son_bakim:
            fark = guncel_km - son_bakim[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Guncel KM", value=f"{guncel_km} km")
            col2.metric(label="Son Bakim KM", value=f"{son_bakim[0]} km")
            col3.metric(label="Yapilan Yol", value=f"{fark} km")
            
            if fark >= 10000:
                st.error("🚨 Periyodik bakim zamani gelmistir!")
            elif fark >= 1000:
                st.warning("⚠️ Agir mekanik islemler sonrasi rodaj kontrolu gerekebilir.")
            else:
                st.success("✅ Durum guvenli.")
        else:
            st.info("Karsilastirma yapilacak bakim kaydi bulunmuyor.")

conn.close()