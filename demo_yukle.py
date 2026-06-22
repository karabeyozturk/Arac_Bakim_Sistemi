import sqlite3
import random
from datetime import date, timedelta
from modeller import Arac
from veritabani import baglanti_olustur

print("Veritabani baglantisi kuruluyor ve eski veriler temizleniyor...")
conn = baglanti_olustur()
cursor = conn.cursor()

# Eski verileri tamamen temizle (Çakışmayı önlemek için)
cursor.execute("DELETE FROM bakimlar")
cursor.execute("DELETE FROM araclar")

# 58 ARACLIK DEV FILO HAVUZU
arac_havuzu = [
    ("16BTE525", "BMW", "F10 525d xDrive"),
    ("58KRY58", "Volkswagen", "Polo 1.4 TSI"),
    ("16ULD16", "BMW", "G20 320i M Sport"),
    ("58SVS01", "Volkswagen", "Passat 1.6 TDI B8"),
    ("34ABC01", "Renault", "Megane 1.5 dCi"),
    ("34ABC02", "Renault", "Megane 1.5 dCi"),
    ("34ABC03", "Renault", "Clio 1.0 TCe"),
    ("34ABC04", "Renault", "Clio 1.0 TCe"),
    ("06ANK11", "Ford", "Focus 1.5 TDCi"),
    ("06ANK12", "Ford", "Focus 1.5 TDCi"),
    ("06ANK13", "Ford", "Courier 1.5 TDCi"),
    ("35EGE01", "Fiat", "Egea 1.3 Multijet"),
    ("35EGE02", "Fiat", "Egea 1.4 Fire"),
    ("35EGE03", "Fiat", "Egea 1.6 Multijet"),
    ("35EGE04", "Fiat", "Fiorino 1.3 MJet"),
    ("07ANT01", "Toyota", "Corolla 1.8 Hybrid"),
    ("07ANT02", "Toyota", "Corolla 1.5 Vision"),
    ("16BUR01", "Toyota", "Yaris 1.5 Hybrid"),
    ("16BUR02", "Honda", "Civic 1.6 i-VTEC Eco"),
    ("16BUR03", "Honda", "Civic 1.5 VTEC Turbo"),
    ("34FLT01", "Peugeot", "3008 1.5 BlueHDi"),
    ("34FLT02", "Peugeot", "2008 1.2 PureTech"),
    ("34FLT03", "Peugeot", "508 1.5 BlueHDi"),
    ("06FLT01", "Citroen", "C5 Aircross 1.5 BlueHDi"),
    ("06FLT02", "Citroen", "C3 1.2 PureTech"),
    ("35FLT01", "Opel", "Astra 1.2 Turbo"),
    ("35FLT02", "Opel", "Corsa 1.2 Turbo"),
    ("35FLT03", "Opel", "Insignia 1.5 D"),
    ("58FLT01", "Skoda", "Superb 1.5 TSI"),
    ("58FLT02", "Skoda", "Octavia 1.0 TSI"),
    ("58FLT03", "Skoda", "Kamiq 1.0 TSI"),
    ("16FLT01", "Seat", "Leon 1.5 eTSI"),
    ("16FLT02", "Seat", "Ateca 1.5 EcoTSI"),
    ("16FLT03", "Seat", "Ibiza 1.0 EcoTSI"),
    ("34PRM01", "Mercedes-Benz", "C200d AMG"),
    ("34PRM02", "Mercedes-Benz", "E250 AMG"),
    ("34PRM03", "Mercedes-Benz", "A180d AMG"),
    ("06PRM01", "Audi", "A3 Sedan 35 TFSI"),
    ("06PRM02", "Audi", "A4 Sedan 40 TDI"),
    ("06PRM03", "Audi", "A6 Sedan 40 TDI"),
    ("35PRM01", "BMW", "520i Luxury Line"),
    ("35PRM02", "BMW", "X3 xDrive20d"),
    ("35PRM03", "Volvo", "XC90 B5 AWD"),
    ("58PRM01", "Volvo", "S60 B4 Inscription"),
    ("16SUV01", "Hyundai", "Tucson 1.6 T-GDI"),
    ("16SUV02", "Hyundai", "Tucson 1.6 CRDi"),
    ("34SUV01", "Kia", "Sportage 1.6 T-GDI"),
    ("34SUV02", "Kia", "Sportage 1.6 CRDi"),
    ("06SUV01", "Nissan", "Qashqai 1.3 DIG-T"),
    ("06SUV02", "Nissan", "X-Trail 1.5 e-Power"),
    ("35ECO01", "Dacia", "Duster 1.5 Blue dCi"),
    ("35ECO02", "Dacia", "Duster 1.3 TCe"),
    ("35ECO03", "Dacia", "Sandero Stepway 1.0"),
    ("58ECO01", "Renault", "Symbol 1.5 dCi"),
    ("58ECO02", "Fiat", "Linea 1.3 Multijet"),
    ("16ECO01", "Hyundai", "i20 1.4 MPI"),
    ("16ECO02", "Kia", "Picanto 1.0 MPI"),
    ("34ECO01", "Toyota", "C-HR 1.8 Hybrid")
]

# DETAYLI MEKANİK, ELEKTRONİK VE PERİYODİK İŞLEM HAVUZU
islem_havuzu = [
    ("Periyodik Bakim (Castrol/Motul 5W-30 + Orijinal Filtre Seti)", 3500, 5000),
    ("Periyodik Bakim (LL-04 Spesifikasyonlu Yag ve Filtreler)", 4500, 6500),
    ("Yazlik/Kislik Lastik Degisimi ve Rot Balans", 1500, 3000),
    ("On ve Arka Fren Balata Degisimi (Brembo/Bosch)", 3500, 6000),
    ("Varta 74Ah AGM Aku Degisimi ve Adaptasyon", 3800, 5500),
    ("Klima Gazi R134a Dolumu ve Ozonla Dezenfeksiyon", 1200, 2000),
    ("Silecek Supurgeleri ve Antifrizli Cam Suyu Ilavesi", 600, 1200),
    ("Agir Bakim (Triger Seti, Devirdaim, V-Kayisi Rulmanlari)", 14000, 25000),
    ("DSG Mekatronik Tup Degisimi ve Adaptasyon", 25000, 45000),
    ("ZF 8 Ileri Sanziman Yagi ve Karter Degisimi", 18000, 28000),
    ("Kavrama (Baski-Balata) ve Cift Kutleli Volant Degisimi", 16000, 32000),
    ("DPF Makinali Temizligi ve Rejenerasyon", 4000, 8000),
    ("EGR Valfi Degisimi ve Manifold Kurum Temizligi", 7000, 14000),
    ("Enjektor Memesi Degisimi ve Bosch Cihazi ile Kodlama", 12000, 24000),
    ("Turbo Kartus Revizyonu ve Intercooler Temizligi", 15000, 28000),
    ("On Takim Revizyonu (Z Rot, Salincak, Amortisor Takozlari)", 8000, 16000),
    ("Komple Motor Rektefiyesi (Piston, Sekman, Ana Kol Yatak)", 65000, 150000),
    ("Motor Rektefiyesi Sonrasi 1.000 KM Rodaj Yag Degisimi (LL-04)", 3000, 4500),
    ("Silindir Kapak Contasi Degisimi ve Kapak Taslama", 22000, 38000),
    ("Direksiyon Kutusu Revizyonu ve EPS Kalibrasyonu", 11000, 19000),
    ("Eksantrik Mili Sensoru ve Atesleme Bobinleri Takim Degisimi", 6000, 12000)
]

print("Simulasyon baslatildi: 58 Arac, binlerce kilometre ve servis kaydi olusturuluyor...")

baslangic_tarihi = date(2024, 6, 1)
bitis_tarihi = date(2026, 6, 20)
toplam_gun = (bitis_tarihi - baslangic_tarihi).days
toplam_islem_sayisi = 0

for plaka, marka, model in arac_havuzu:
    kayit_sayisi = random.randint(5, 14) 
    guncel_km = random.randint(10000, 350000)
    
    tarihler = sorted([baslangic_tarihi + timedelta(days=random.randint(0, toplam_gun)) for _ in range(kayit_sayisi)])
    
    islem_kmleri = []
    gecici_km = guncel_km - (kayit_sayisi * random.randint(4000, 15000))
    for _ in range(kayit_sayisi):
        islem_kmleri.append(max(0, gecici_km))
        gecici_km += random.randint(3000, 18000)
        
    guncel_km = islem_kmleri[-1] + random.randint(100, 6000)
    
    yeni_arac = Arac(plaka, marka, model, guncel_km)
    cursor.execute(
        "INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)",
        (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre)
    )
    
    for i in range(kayit_sayisi):
        islem_adi, min_fiyat, max_fiyat = random.choice(islem_havuzu)
        
        if "Rodaj Yag" in islem_adi and i > 0:
            islem_km = islem_kmleri[i-1] + random.randint(950, 1100)
        else:
            islem_km = islem_kmleri[i]
            
        maliyet = round(random.uniform(min_fiyat, max_fiyat), 2)
        islem_tarihi = tarihler[i].isoformat()
        
        cursor.execute(
            "INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
            (plaka, islem_adi, islem_km, maliyet, islem_tarihi)
        )
        toplam_islem_sayisi += 1

conn.commit()
conn.close()

print("-" * 50)
print("ISLEM TAMAMLANDI!")
print("Sisteme Yuklenen Arac Sayisi: 58 Adet")
print(f"Olusturulan Servis / Finans Kaydi: {toplam_islem_sayisi} Adet")
print("-" * 50)