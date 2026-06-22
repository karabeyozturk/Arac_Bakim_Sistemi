import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

# st.set_page_config(page_title="Premium Araç Yönetimi", page_icon="🚗", layout="wide")

# conn = baglanti_olustur()
cursor = conn.cursor()

# st.sidebar.markdown("### ⚙️ Yönetim Paneli")
st.sidebar.markdown("---")
secim = st.sidebar.radio("İşlem Menüsü:", [
    "📊 Dashboard (Genel Bakış)", 
    "🚗 Yeni Araç Ekle", 
    "🔧 Bakım ve Masraf İşle", 
    "📋 Kayıtlar ve Finansal Rapor", 
    "⏱️ Akıllı Uyarı Sistemi"
])

if secim == "📊 Dashboard (Genel Bakış)":
    st.title("📊 Sistem Gösterge Paneli")
    st.markdown("Araç filonuzun ve bakım maliyetlerinizin genel finansal analizi.")
    
    # cursor.execute("SELECT COUNT(*) FROM araclar")
    toplam_arac = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(maliyet) FROM bakimlar")
    toplam_maliyet = cursor.fetchone()[0] or 0.0
    
    # col1, col2, col3 = st.columns(3)
    col1.metric(label="Kayıtlı Toplam Araç", value=f"{toplam_arac} Adet")
    col2.metric(label="Toplam Bakım Gideri", value=f"{toplam_maliyet:,.2f} ₺")
    col3.metric(label="Sistem Durumu", value="Aktif", delta="Sorunsuz")

    st.markdown("---")
    
    # df_grafik = pd.read_sql_query("SELECT plaka, SUM(maliyet) as toplam FROM bakimlar GROUP BY plaka", conn)
    
    if not df_grafik.empty:
        col_grafik1, col_grafik2 = st.columns(2)
        
        with col_grafik1:
            st.subheader("Araç Bazlı Toplam Harcama Dağılımı")
            fig_pie = px.pie(df_grafik, values='toplam', names='plaka', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_grafik2:
            st.subheader("Finansal Gider Karşılaştırması")
            fig_bar = px.bar(df_grafik, x='plaka', y='toplam', color='plaka', text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Grafik oluşturulabilmesi için sisteme bakım kaydı girilmesi gerekmektedir.")

elif secim == "🚗 Yeni Araç Ekle":
    st.title("🚗 Sisteme Yeni Araç Kaydı")
    
    # with st.form("arac_ekle_form"):
        col1, col2 = st.columns(2)
        with col1:
            plaka = st.text_input("Araç Plakası (Örn: 16ABC123)").upper()
            marka = st.text_input("Marka (Örn: BMW)")
        with col2:
            model = st.text_input("Model (Örn: 525d xDrive)")
            km = st.number_input("Güncel Kilometre", min_value=0, step=1)
        
        submit = st.form_submit_button("Sisteme Kaydet", use_container_width=True)

        if submit:
            if plaka and marka and model:
                try:
                    yeni_arac = Arac(plaka, marka, model, km)
                    cursor.execute("INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)", 
                                   (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre))
                    conn.commit()
                    st.success(f"✅ {plaka} plakalı araç başarıyla veritabanına işlenmiştir.")
                except sqlite3.IntegrityError:
                    st.error("❌ HATA: Girilen plaka sistemde zaten mevcuttur.")
            else:
                st.warning("⚠️ Eksik veri girişi! Lütfen tüm alanları doldurunuz.")

elif secim == "🔧 Bakım ve Masraf İşle":
    st.title("🔧 Bakım ve Masraf Girişi")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Kayıtlı araç bulunmamaktadır. Lütfen önce araç kaydı oluşturunuz.")
    else:
        with st.form("bakim_ekle_form"):
            secilen_plaka = st.selectbox("İşlem Yapılacak Araç:", plaka_listesi)
            islem_turu = st.text_input("İşlem Detayı (Örn: LL-04 Motor Yağı Değişimi, Rektefiye Rodaj vs.)")
            
            col1, col2 = st.columns(2)
            with col1:
                islem_km = st.number_input("İşlem Kilometresi", min_value=0, step=1)
            with col2:
                maliyet = st.number_input("Maliyet Tutarı (TL)", min_value=0.0, step=10.0)
            
            submit = st.form_submit_button("Bakım Verisini İşle", use_container_width=True)

            if submit:
                if islem_turu:
                    yeni_bakim = BakimKaydi(secilen_plaka, islem_turu, islem_km, maliyet)
                    cursor.execute("INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
                                   (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih))
                    cursor.execute("UPDATE araclar SET kilometre = ? WHERE plaka = ?", (islem_km, secilen_plaka))
                    conn.commit()
                    st.success("✅ Bakım verisi başarıyla işlenmiş ve aracın güncel kilometresi revize edilmiştir.")
                else:
                    st.warning("⚠️ İşlem detayı boş bırakılamaz.")

elif secim == "📋 Kayıtlar ve Finansal Rapor":
    st.title("📋 Finansal Rapor ve Kayıt Dökümü")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Sistemde sorgulanacak araç bulunmamaktadır.")
    else:
        secilen_plaka = st.selectbox("Sorgulanacak Araç Plakası:", plaka_listesi)
        
        # df = pd.read_sql_query("SELECT tarih, islem_turu, kilometre, maliyet FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC", conn, params=(secilen_plaka,))
        
        if not df.empty:
            toplam_harcama = df['maliyet'].sum()
            st.markdown(f"### Toplam Finansal Gider: **{toplam_harcama:,.2f} ₺**")
            
            st.dataframe(df, use_container_width=True)
            
            # csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tabloyu CSV Olarak İndir",
                data=csv,
                file_name=f'{secilen_plaka}_bakim_gecmisi.csv',
                mime='text/csv',
            )
        else:
            st.info("Bu araca ait herhangi bir bakım kaydı bulunamamıştır.")

elif secim == "⏱️ Akıllı Uyarı Sistemi":
    st.title("⏱️ Akıllı Bakım ve Rodaj Uyarıları")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Sistemde sorgulanacak araç bulunmamaktadır.")
    else:
        secilen_plaka = st.selectbox("Kontrol Edilecek Araç:", plaka_listesi)
        
        cursor.execute("SELECT kilometre FROM araclar WHERE plaka = ?", (secilen_plaka,))
        guncel_km = cursor.fetchone()[0]
        
        cursor.execute("SELECT kilometre FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1", (secilen_plaka,))
        son_bakim = cursor.fetchone()
        
        if son_bakim:
            fark = guncel_km - son_bakim[0]
            
            # col1, col2, col3 = st.columns(3)
            col1.metric(label="Güncel Kilometre", value=f"{guncel_km} km")
            col2.metric(label="Son İşlem Kilometresi", value=f"{son_bakim[0]} km")
            col3.metric(label="Kullanılan Kilometre", value=f"{fark} km", delta=f"{10000 - fark} km Kaldı" if fark < 10000 else "Sınır Aşıldı", delta_color="inverse")
            
            st.markdown("---")
            
            if fark >= 10000:
                st.error("🚨 KRİTİK UYARI: Standart 10.000 km periyodik bakım sınırı aşılmıştır! Lütfen en kısa sürede servise başvurun.")
            elif fark >= 1000:
                st.warning("⚠️ BİLGİ MESAJI: Ağır mekanik işlem (rektefiye vb.) yapıldıysa 1.000 km rodaj bakım (LL-04 yağ değişimi) zamanı gelmiştir.")
            else:
                st.success("✅ DURUM GÜVENLİ: Herhangi bir periyodik bakım veya rodaj sınırına ulaşılmamıştır.")
        else:
            st.info("Veritabanında karşılaştırma yapılabilecek bakım kaydı bulunmamaktadır.")

# conn.close()