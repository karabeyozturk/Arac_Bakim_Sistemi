from datetime import datetime

class Arac:
    """Araç nesnelerini temsil eden sınıf."""
    def __init__(self, plaka, marka, model, kilometre):
        self.plaka = plaka
        self.marka = marka
        self.model = model
        self.kilometre = int(kilometre)

    def bilgileri_goster(self):
        return f"{self.plaka} - {self.marka} {self.model} (Güncel KM: {self.kilometre})"

class BakimKaydi:
    """Yapılan bakım ve masraf işlemlerini temsil eden sınıf."""
    def __init__(self, plaka, islem_turu, kilometre, maliyet, tarih=None):
        self.plaka = plaka
        self.islem_turu = islem_turu
        self.kilometre = int(kilometre)
        self.maliyet = float(maliyet)
        # Eğer tarih girilmezse günün tarihini otomatik alır
        self.tarih = tarih if tarih else datetime.now().strftime("%Y-%m-%d")

    def ozet_goster(self):
        return f"[{self.tarih}] {self.islem_turu} | KM: {self.kilometre} | Tutar: {self.maliyet} TL"