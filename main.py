import sqlite3
from modeller import Arac, BakimKaydi
from veritabani import baglanti_olustur

def ana_menu():
    # Veritabanı bağlantımızı açıyoruz
    conn = baglanti_olustur()
    cursor = conn.cursor()

    while True:
        print("\n" + "="*40)
        print("  ARAÇ BAKIM VE MASRAF TAKİP SİSTEMİ  ")
        print("="*40)
        print("1. Yeni Araç Ekle")
        print("2. Bakım/Masraf Kaydı Ekle")
        print("3. Geçmiş Bakımları Listele")
        print("4. Yaklaşan Bakımları Kontrol Et")
        print("5. Çıkış")
        
        secim = input("\nLütfen bir işlem seçiniz (1-5): ")

        if secim == '1':
            plaka = input("Araç Plakası (Örn: 16ABC123): ").upper()
            marka = input("Marka (Örn: BMW): ")
            model = input("Model (Örn: 525d xDrive): ")
            
            try:
                # Kullanıcı harf girerse hata vermemesi için try/except bloğu
                km = int(input("Güncel Kilometre: "))
                yeni_arac = Arac(plaka, marka, model, km)
                
                cursor.execute("INSERT INTO araclar (plaka, marka, model, kilometre) VALUES (?, ?, ?, ?)", 
                               (yeni_arac.plaka, yeni_arac.marka, yeni_arac.model, yeni_arac.kilometre))
                conn.commit()
                print("\n[BAŞARILI] Araç sisteme kaydedildi!")
            except ValueError:
                print("\n[HATA] Kilometre alanına sadece sayı girmelisiniz!")
            except sqlite3.IntegrityError:
                print("\n[HATA] Bu plaka zaten sistemde kayıtlı!")

        elif secim == '2':
            plaka = input("Bakım eklenecek aracın plakası: ").upper()
            islem_turu = input("İşlem Türü (Örn: LL-04 Motor Yağı, Rektefiye Rodaj vs.): ")
            
            try:
                km = int(input("İşlemin yapıldığı Kilometre: "))
                maliyet = float(input("Maliyet (TL): "))
                
                yeni_bakim = BakimKaydi(plaka, islem_turu, km, maliyet)
                
                cursor.execute("INSERT INTO bakimlar (plaka, islem_turu, kilometre, maliyet, tarih) VALUES (?, ?, ?, ?, ?)",
                               (yeni_bakim.plaka, yeni_bakim.islem_turu, yeni_bakim.kilometre, yeni_bakim.maliyet, yeni_bakim.tarih))
                
                # Bakım eklendikçe aracın güncel kilometresini de güncelliyoruz
                cursor.execute("UPDATE araclar SET kilometre = ? WHERE plaka = ?", (km, plaka))
                conn.commit()
                print("\n[BAŞARILI] Bakım kaydı eklendi!")
            except ValueError:
                print("\n[HATA] Kilometre ve Maliyet için geçerli sayısal değerler girmelisiniz!")

        elif secim == '3':
            plaka = input("Geçmişini görmek istediğiniz aracın plakası: ").upper()
            cursor.execute("SELECT tarih, islem_turu, kilometre, maliyet FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC", (plaka,))
            kayitlar = cursor.fetchall()
            
            if kayitlar:
                print(f"\n--- {plaka} Plakalı Aracın Bakım Geçmişi ---")
                toplam_masraf = 0
                for kayit in kayitlar:
                    print(f"[{kayit[0]}] KM: {kayit[2]} | İşlem: {kayit[1]} | Tutar: {kayit[3]} TL")
                    toplam_masraf += kayit[3]
                print(f"Toplam Harcama: {toplam_masraf} TL")
            else:
                print("\n[BİLGİ] Bu araca ait kayıt bulunamadı.")

        elif secim == '4':
            plaka = input("Kontrol edilecek aracın plakası: ").upper()
            cursor.execute("SELECT kilometre FROM araclar WHERE plaka = ?", (plaka,))
            arac_kaydi = cursor.fetchone()
            
            if arac_kaydi:
                guncel_km = arac_kaydi[0]
                cursor.execute("SELECT kilometre, islem_turu FROM bakimlar WHERE plaka = ? ORDER BY kilometre DESC LIMIT 1", (plaka,))
                son_bakim = cursor.fetchone()
                
                if son_bakim:
                    fark = guncel_km - son_bakim[0]
                    print(f"\nSon işlemden bu yana {fark} km geçmiş.")
                    if fark >= 10000:
                        print("[DİKKAT] Standart 10.000 km bakım zamanınız gelmiş veya geçmiş!")
                    elif fark >= 1000:
                        print("[BİLGİ] Eğer motor rektefiyesi yapıldıysa 1.000 km rodaj yağ değişim zamanı gelmiştir!")
                    else:
                        print("[DURUM] Her şey yolunda, bakıma daha var.")
                else:
                    print("\n[BİLGİ] Bu araca ait bakım kaydı bulunamadı.")
            else:
                print("\n[HATA] Araç sistemde bulunamadı.")

        elif secim == '5':
            print("\nVeritabanı bağlantısı kapatılıyor... İyi günler!")
            conn.close()
            break
        
        else:
            print("\n[HATA] Hatalı seçim! Lütfen 1 ile 5 arasında bir değer giriniz.")

if __name__ == "__main__":
    ana_menu()