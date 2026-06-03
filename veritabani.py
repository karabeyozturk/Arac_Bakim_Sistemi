import sqlite3

def baglanti_olustur():
    """Veritabanı bağlantısını kurar ve tabloları (varsa atlar, yoksa) oluşturur."""
    # Programın çalıştığı klasörde 'arac_bakim.db' adında bir veritabanı dosyası yaratır
    conn = sqlite3.connect('arac_bakim.db')
    cursor = conn.cursor()

    # Araçlar tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS araclar (
            plaka TEXT PRIMARY KEY,
            marka TEXT,
            model TEXT,
            kilometre INTEGER
        )
    ''')

    # Bakım geçmişi tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bakimlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plaka TEXT,
            islem_turu TEXT,
            kilometre INTEGER,
            maliyet REAL,
            tarih TEXT,
            FOREIGN KEY (plaka) REFERENCES araclar(plaka)
        )
    ''')

    conn.commit()
    return conn

# Dosya ilk çalıştığında tabloların hazır olduğundan emin oluyoruz
if __name__ == "__main__":
    baglanti_olustur().close()