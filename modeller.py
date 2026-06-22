from datetime import date

class Arac:
    def __init__(self, plaka: str, marka: str, model: str, kilometre: int):
        self.plaka = plaka.strip().upper()
        self.marka = marka.strip()
        self.model = model.strip()
        self.kilometre = kilometre

    def __repr__(self):
        return f"Arac({self.plaka}, {self.marka} {self.model}, {self.kilometre} km)"


class BakimKaydi:
    def __init__(self, plaka: str, islem_turu: str, kilometre: int, maliyet: float):
        self.plaka = plaka.strip().upper()
        self.islem_turu = islem_turu.strip()
        self.kilometre = kilometre
        self.maliyet = round(maliyet, 2)
        self.tarih = date.today().isoformat()

    def __repr__(self):
        return f"BakimKaydi({self.plaka} | {self.islem_turu} | {self.kilometre} km | ₺{self.maliyet})"