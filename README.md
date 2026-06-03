# Araç Bakım ve Masraf Takip Sistemi

Bu proje, İleri Programlama dersi final projesi kapsamında geliştirilmiş nesne yönelimli (OOP) bir Python uygulamasıdır. Kullanıcıların araçlarına ait periyodik bakımları, parça onarımlarını ve bu işlemlerin maliyetlerini kilometre bazlı olarak takip etmelerini sağlar.

## Özellikler
* **Nesne Yönelimli Tasarım:** `Arac` ve `BakimKaydi` sınıfları ile gerçek dünya modellemesi.
* **Veri Kalıcılığı:** Tüm veriler `sqlite3` kullanılarak `arac_bakim.db` veritabanında güvenle saklanır.
* **Hata Yönetimi:** Hatalı veri girişleri (örneğin kilometre yerine harf yazılması) `try/except` blokları ile yakalanır.
* **Akıllı Uyarı Sistemi:** 10.000 km periyodik bakımları ve ağır mekanik işlemler (örn: rektefiye) sonrası 1.000 km rodaj kontrollerini otomatik hesaplar.

## Kurulum ve Çalıştırma

Projenin çalışması için bilgisayarınızda **Python 3.10 veya üzeri** bir sürümün yüklü olması gerekmektedir. Herhangi bir harici kütüphane kurulumuna (pip install) gerek yoktur; standart kütüphaneler (`sqlite3`, `datetime`) kullanılmıştır.

1. Depoyu bilgisayarınıza klonlayın:
   ```bash
   git clone [https://github.com/karabeyozturk/Arac_Bakim_Sistemi.git](https://github.com/karabeyozturk/Arac_Bakim_Sistemi.git)