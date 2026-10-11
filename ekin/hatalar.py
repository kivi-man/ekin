"""Ekin hata türleri. Tüm iletiler Türkçedir ve satır bilgisi taşır."""


class EkinHatasi(Exception):
    tur = "Hata"

    def __init__(self, ileti, satir=None, sutun=None, dosya=None):
        super().__init__(ileti)
        self.ileti = ileti
        self.satir = satir
        self.sutun = sutun
        self.dosya = dosya

    def bicimle(self, kaynak=None):
        yer = ""
        if self.dosya:
            yer += f"{self.dosya}"
        if self.satir:
            yer += f":{self.satir}" if yer else f"satır {self.satir}"
        metin = f"{self.tur}"
        if yer:
            metin += f" ({yer})"
        metin += f": {self.ileti}"
        if kaynak and self.satir:
            satirlar = kaynak.splitlines()
            if 0 < self.satir <= len(satirlar):
                kod = satirlar[self.satir - 1]
                metin += f"\n    {kod}"
                if self.sutun:
                    metin += "\n    " + " " * (self.sutun - 1) + "^"
        return metin


class SozcukHatasi(EkinHatasi):
    tur = "Yazım hatası"


class SozdizimHatasi(EkinHatasi):
    tur = "Sözdizimi hatası"


class TipHatasi(EkinHatasi):
    tur = "Tip hatası"


class CalismaHatasi(EkinHatasi):
    tur = "Çalışma hatası"


class DerlemeHatasi(EkinHatasi):
    tur = "Derleme hatası"
