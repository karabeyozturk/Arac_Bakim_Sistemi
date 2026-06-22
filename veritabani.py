import sqlite3

DB_PATH = "autotrack.db"

def baglanti_olustur() -> sqlite3.Connection:
    """Veritabanı bağlantısını oluşturur; tablolar yoksa kurar."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS araclar (
            plaka     TEXT PRIMARY KEY,
            marka     TEXT NOT NULL,
            model     TEXT NOT NULL,
            kilometre INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bakimlar (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            plaka      TEXT NOT NULL,
            islem_turu TEXT NOT NULL,
            kilometre  INTEGER DEFAULT 0,
            maliyet    REAL DEFAULT 0.0,
            tarih      TEXT,
            FOREIGN KEY (plaka) REFERENCES araclar(plaka)
        )
    """)

    conn.commit()
    return conn