import streamlit as st
import pandas as pd
import sqlite3
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

# Arayüz sayfa yapılandırması ve başlık ataması gerçekleştirilmiştir.
st.set_page_config(page_title="Araç Bakım Sistemi", layout="wide")

# Veritabanı bağlantısı başlatılarak imleç (cursor) nesnesi oluşturulmuştur.
conn = baglanti_olustur()
cursor = conn.cursor()

# Kullanıcı arayüzü için sol menü (sidebar) navigasyon yapısı kurulmuştur.
st.sidebar.title("Sistem Menüsü")
secim = st.sidebar.radio("İşlem Seçimi:", [
    "1. Yeni Araç Kaydı", 
    "2. Bakım/Masraf Girişi", 
    "3. Geçmiş Kayıt Dökümü", 
    "4. Periyodik Bakım Kontrolü"
])

if secim == "1. Yeni Araç Kaydı":
    st.header("Sisteme Yeni Araç Ekleme Modülü")
    
    # Yeni araç verilerinin alınması için form yapısı oluşturulmuştur.
    with st.form("arac_ekle_form"):
        plaka = st.text_input("Araç Plakası (Örn: 16ABC123)").upper()
        marka = st.text_input("Marka (Örn: BMW)")
        model = st.text_input("Model (Örn: 525d xDrive)")
        km = st.number_input("Güncel Kilometre", min_value=0, step=1)
        submit = st.form_submit_button("Sisteme Kaydet")

        # Form gönderimi sonrası veritabanı kayıt işlemleri ve hata yönetimi sağlanmıştır.
        if submit:
            if plaka and marka and model:
                try:
                    yeni_arac = Arac(plaka, marka, model, km)
                    cursor.execute("INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)", 
                                   (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre))
                    conn.commit()
                    st.success(f"{plaka} plakalı araç başarıyla veritabanına işlenmiştir.")
                except sqlite3.IntegrityError:
                    st.error("HATA: Girilen plaka sistemde zaten mevcuttur.")
            else:
                st.warning("Eksik veri girişi! Lütfen tüm alanları doldurunuz.")

elif secim == "2. Bakım/Masraf Girişi":
    st.header("Araç Bakım ve Masraf İşleme Modülü")
    
    # İşlem yapılacak aracın seçilebilmesi için veritabanından plaka listesi çekilmiştir.
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Kayıtlı araç bulunmamaktadır. Lütfen önce araç kaydı oluşturunuz.")
    else:
        with st.form("bakim_ekle_form"):
            secilen_plaka = st.selectbox("İşlem Yapılacak Araç:", plaka_listesi)
            islem_turu = st.text_input("İşlem Detayı (Örn: LL-04 Motor Yağı, Rektefiye Rodaj vs.)")
            islem_km = st.number_input("İşlem Kilometresi", min_value=0, step=1)
            maliyet = st.number_input("Maliyet Tutarı (TL)", min_value=0.0, step=10.0)
            submit = st.form_submit_button("Bakım Verisini İşle")

            # Bakım verilerinin kaydedilmesi ve araç güncel kilometresinin güncellenmesi sağlanmıştır.
            if submit:
                if islem_turu:
                    yeni_bakim = BakimKaydi(secilen_plaka, islem_turu, islem_km, maliyet)
                    cursor.execute("INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
                                   (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih))
                    cursor.execute("UPDATE araclar SET kilometre = ? WHERE plaka = ?", (islem_km, secilen_plaka))
                    conn.commit()
                    st.success("Bakım verisi başarıyla işlenmiş ve aracın güncel kilometresi revize edilmiştir.")
                else:
                    st.warning("İşlem detayı boş bırakılamaz.")

elif secim == "3. Geçmiş Kayıt Dökümü":
    st.header("Geçmiş Bakım ve Masraf Analizi")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Sistemde sorgulanacak araç bulunmamaktadır.")
    else:
        secilen_plaka = st.selectbox("Sorgulanacak Araç Plakası:", plaka_listesi)
        
        # Seçilen araca ait geçmiş veriler Pandas DataFrame aracılığıyla tabloya dönüştürülmüştür.
        df = pd.read_sql_query("SELECT tarih, islem_turu, kilometre, maliyet FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC", conn, params=(secilen_plaka,))
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            toplam_harcama = df['maliyet'].sum()
            st.write(f"### Toplam Finansal Gider: {toplam_harcama} TL")
        else:
            st.info("Bu araca ait herhangi bir bakım kaydı bulunamamıştır.")

elif secim == "4. Periyodik Bakım Kontrolü":
    st.header("Akıllı Bakım ve Rodaj Uyarı Sistemi")
    
    cursor.execute("SELECT plaka FROM araclar")
    plaka_listesi = [arac[0] for arac in cursor.fetchall()]

    if not plaka_listesi:
        st.info("Sistemde sorgulanacak araç bulunmamaktadır.")
    else:
        secilen_plaka = st.selectbox("Kontrol Edilecek Araç:", plaka_listesi)
        
        # Aracın güncel kilometresi ile son işlem kilometresi arasındaki fark hesaplanmıştır.
        cursor.execute("SELECT kilometre FROM araclar WHERE plaka = ?", (secilen_plaka,))
        guncel_km = cursor.fetchone()[0]
        
        cursor.execute("SELECT kilometre FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1", (secilen_plaka,))
        son_bakim = cursor.fetchone()
        
        if son_bakim:
            fark = guncel_km - son_bakim[0]
            st.write(f"Güncel Kilometre Verisi: **{guncel_km}**")
            st.write(f"Son İşlem Kilometre Verisi: **{son_bakim[0]}**")
            st.write(f"Son bakım üzerinden yapılan kilometre: **{fark} km**")
            
            # Karar ağaçları kullanılarak kilometre farkına göre durum analizi yapılmıştır.
            if fark >= 10000:
                st.error("KRİTİK UYARI: Standart 10.000 km periyodik bakım sınırı aşılmıştır!")
            elif fark >= 1000:
                st.warning("BİLGİ MESAJI: Ağır mekanik işlem (rektefiye vb.) yapıldıysa 1.000 km rodaj bakım zamanı gelmiştir.")
            else:
                st.success("DURUM GÜVENLİ: Herhangi bir periyodik bakım veya rodaj sınırına ulaşılmamıştır.")
        else:
            st.info("Veritabanında karşılaştırma yapılabilecek bakım kaydı bulunmamaktadır.")

# İşlemler tamamlandıktan sonra veritabanı bağlantısı sonlandırılmıştır.
conn.close()