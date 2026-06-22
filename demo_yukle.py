import sqlite3
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

print("Veritabanı bağlantısı kuruluyor...")
conn = baglanti_olustur()
cursor = conn.cursor()

# Sisteme eklenecek demo araçlar
arac_listesi = [
    ("16BTE525", "BMW", "F10 525d xDrive", 185000),
    ("16PL202", "Volkswagen", "Polo 1.4 TSI", 95000),
    ("58SVS58", "Toyota", "Corolla 1.8 Hybrid", 32000),
    ("16ULD99", "Honda", "Civic 1.6 i-VTEC", 78000),
    ("34KRY01", "Mercedes-Benz", "C200d AMG", 110000),
    ("06ANK06", "Hyundai", "Tucson 1.6 T-GDI", 65000)
]

print("Araçlar sisteme entegre ediliyor...")
for plaka, marka, model, km in arac_listesi:
    try:
        yeni_arac = Arac(plaka, marka, model, km)
        cursor.execute(
            "INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)",
            (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre)
        )
    except sqlite3.IntegrityError:
        pass # Plaka zaten varsa atla

# Grafiklerin oluşması için demo bakım geçmişleri
bakim_listesi = [
    ("16BTE525", "LL-04 Motor Yağı ve Filtre Değişimi", 184000, 4500.0),
    ("16BTE525", "Motor Rektefiyesi Sonrası Rodaj Bakımı", 185000, 1500.0),
    ("16PL202", "Periyodik Yıllık Bakım", 90000, 3200.0),
    ("16PL202", "Ön Fren Disk ve Balata Değişimi", 94500, 5800.0),
    ("58SVS58", "Hibrit Sistem Kontrolü ve Yağ Değişimi", 31000, 4100.0),
    ("34KRY01", "Ağır Bakım (Triger ve Devirdaim)", 105000, 18500.0)
]

print("Servis ve finansal kayıtlar işleniyor...")
for plaka, islem, km, maliyet in bakim_listesi:
    yeni_bakim = BakimKaydi(plaka, islem, km, maliyet)
    cursor.execute(
        "INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
        (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih)
    )

conn.commit()
conn.close()
print("✅ Tüm demo veriler başarıyla kalıcı veritabanına işlendi!")