import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Premium Araç Yönetimi", page_icon="🏎️", layout="wide")

# Veritabanı Bağlantısı
conn = baglanti_olustur()
cursor = conn.cursor()

# --- MODERN YAN MENÜ TASARIMI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3202/3202926.png", width=100)
    st.markdown("## Filonuzu Yönetin")
    secim = option_menu(
        menu_title=None,
        options=["Dashboard", "Yeni Araç Ekle", "Bakım/Masraf İşle", "Finansal Rapor", "Akıllı Uyarılar"],
        icons=["bar-chart-line-fill", "car-front-fill", "tools", "wallet-fill", "bell-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#4A90E2", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#4A90E2", "color": "white", "icon-color": "white"},
        }
    )
    st.markdown("---")
    st.caption("© 2026 Araç Bakım Sistemi")

# --- İÇERİK BÖLÜMÜ ---
if secim == "Dashboard":
    st.title("📊 Sistem Gösterge Paneli")
    st.markdown("Filonuzun anlık durumunu ve maliyet analizlerini buradan takip edebilirsiniz.")
    st.markdown("---")
    
    cursor.execute("SELECT COUNT(*) FROM araclar")
    toplam_arac = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(maliyet) FROM bakimlar")
    toplam_maliyet = cursor.fetchone()[0] or 0.0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🚗 Kayıtlı Araç Sayısı")
        st.markdown(f"## {toplam_arac} Adet")
    with col2:
        st.success("💰 Toplam Bakım Gideri")
        st.markdown(f"## {toplam_maliyet:,.2f} ₺")
    with col3:
        st.warning("⚡ Sistem Durumu")
        st.markdown("## Optimizasyon Aktif")

    st.markdown("<br>", unsafe_allow_html=True)
    
    df_grafik = pd.read_sql_query("SELECT plaka, SUM(maliyet) as toplam FROM bakimlar GROUP BY plaka", conn)
    
    if not df_grafik.empty:
        col_grafik1, col_grafik2 = st.columns(2)
        with col_grafik1:
            st.markdown("#### 🍩 Araç Bazlı Harcama Dağılımı")
            fig_pie = px.pie(df_grafik, values='toplam', names='plaka', hole=0.5, 
                             color_discrete_sequence=px.colors.sequential.Teal)
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_grafik2:
            st.markdown("#### 📊 Finansal Gider Karşılaştırması")
            fig_bar = px.bar(df_grafik, x='plaka', y='toplam', text_auto=True, color='plaka')
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("💡 Grafiklerin oluşması için sisteme en az bir bakım kaydı giriniz.")

elif secim == "Yeni Araç Ekle":
    st.title("🏎️ Yeni Araç Kayıt Modülü")
    st.markdown("Lütfen araca ait bilgileri eksiksiz doldurun.")
    
    with st.container():
        with st.form("arac_ekle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                plaka = st.text_input("Araç Plakası", placeholder="Örn: 34ABC123").upper()
                marka = st.text_input("Marka", placeholder="Örn: BMW")
            with col2:
                model = st.text_input("Model", placeholder="Örn: F10 525d xDrive")
                km = st.number_input("Güncel Kilometre", min_value=0, step=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Sisteme Kaydet", use_container_width=True)

            if submit:
                if plaka and marka and model:
                    try:
                        yeni_arac = Arac(plaka, marka, model, km)
                        cursor.execute("INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)", 
                                       (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre))
                        conn.commit()
                        st.success(f"✅ {plaka} plakalı araç başarıyla filoya eklendi.")
                    except sqlite3.IntegrityError:
                        st.error("❌ HATA: Bu plaka numarası sistemde zaten kayıtlı.")
                else:
                    st.warning("⚠️ Lütfen tüm alanları doldurunuz.")

elif secim == "Bakım/Masraf İşle":
    st.title("🔧 Servis ve Masraf Girişi")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.warning("Lütfen önce sisteme bir araç kaydediniz.")
    else:
        with st.form("bakim_ekle_form", clear_on_submit=True):
            secilen_plaka = st.selectbox("İşlem Yapılacak Araç:", plaka_listesi)
            islem_turu = st.text_input("İşlem Detayı", placeholder="Örn: Periyodik Bakım, LL-04 Motor Yağı Değişimi...")
            
            col1, col2 = st.columns(2)
            with col1:
                islem_km = st.number_input("İşlem Yapıldığı Kilometre", min_value=0, step=1)
            with col2:
                maliyet = st.number_input("Toplam Maliyet (TL)", min_value=0.0, step=100.0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Bakım Verisini Onayla ve İşle", use_container_width=True)

            if submit:
                if islem_turu:
                    yeni_bakim = BakimKaydi(secilen_plaka, islem_turu, islem_km, maliyet)
                    cursor.execute("INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
                                   (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih))
                    cursor.execute("UPDATE araclar SET kilometre = ? WHERE plaka = ?", (islem_km, secilen_plaka))
                    conn.commit()
                    st.success("✅ Servis kaydı başarıyla oluşturuldu. Aracın güncel kilometresi senkronize edildi.")
                else:
                    st.warning("⚠️ Lütfen işlem detayını belirtiniz.")

elif secim == "Finansal Rapor":
    st.title("📋 Finansal Geçmiş ve Raporlama")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.warning("Sistemde raporlanacak araç bulunmamaktadır.")
    else:
        secilen_plaka = st.selectbox("Analiz Edilecek Araç:", plaka_listesi)
        st.markdown("---")
        
        df = pd.read_sql_query("SELECT tarih, islem_turu, kilometre, maliyet FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC", conn, params=(secilen_plaka,))
        
        if not df.empty:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col2:
                toplam_harcama = df['maliyet'].sum()
                st.metric(label="Toplam Araç Gideri", value=f"{toplam_harcama:,.2f} ₺")
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 CSV Olarak İndir",
                    data=csv,
                    file_name=f'{secilen_plaka}_rapor.csv',
                    mime='text/csv',
                    use_container_width=True
                )
        else:
            st.info("Bu araca ait servis kaydı bulunmamaktadır.")

elif secim == "Akıllı Uyarılar":
    st.title("🚨 Periyodik Bakım ve Rodaj Takibi")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.warning("Kontrol edilecek araç kaydı bulunamadı.")
    else:
        secilen_plaka = st.selectbox("Durumu Kontrol Edilecek Araç:", plaka_listesi)
        st.markdown("---")
        
        cursor.execute("SELECT kilometre FROM araclar WHERE plaka = ?", (secilen_plaka,))
        guncel_km = cursor.fetchone()[0]
        
        cursor.execute("SELECT kilometre FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1", (secilen_plaka,))
        son_bakim = cursor.fetchone()
        
        if son_bakim:
            fark = guncel_km - son_bakim[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Mevcut Kilometre", value=f"{guncel_km:,} km")
            col2.metric(label="Son Servis Kilometresi", value=f"{son_bakim[0]:,} km")
            col3.metric(label="Servisten Sonra Yapılan", value=f"{fark:,} km", 
                        delta=f"{10000 - fark:,} km Kaldı" if fark < 10000 else "AŞILDI", delta_color="inverse")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if fark >= 10000:
                st.error("🚨 **KRİTİK DURUM:** 10.000 km periyodik bakım limiti aşılmış! Aracın acilen servise alınması gerekmektedir.")
            elif fark >= 1000:
                st.warning("⚠️ **DİKKAT:** Motor revizyonu veya ağır işlem yapıldıysa 1.000 km rodaj (ilk yağ değişimi) süresi gelmiştir.")
            else:
                st.success("✅ **HER ŞEY YOLUNDA:** Araç mekanik sınırların içinde, güvenle yola devam edebilirsiniz.")
        else:
            st.info("Sistemde karşılaştırma yapılacak geçmiş servis kaydı bulunamadı.")

conn.close()