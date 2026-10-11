"""Sözcük ayırıcı (lexer).

Kaynağı jetonlara (token) böler. Özellikler:
  * Türkçe karakterli tanımlayıcılar (ğ, ş, ı, İ, ç, ö, ü)
  * Kesme işaretiyle ek: 13'ü, liste'ye, "merhaba"'yı  (’ de kabul edilir)
  * Girintiyle blok (Python gibi): GIRINTI / CIKINTI jetonları
  * "...{ifade}..." biçiminde metin içi ifade
  * cpp: bloğu (ham C++ kodu)
"""

import re

from .ekler import ek_coz, ascii_yap
from .hatalar import SozcukHatasi

ANAHTAR = {
    "eğer", "değilse", "yoksa", "ise", "iken", "için", "her", "tekrarla",
    "kez", "sürekli", "kır", "devam", "dön", "işlev", "yapı", "kullan",
    "dış", "ve", "veya", "değil", "doğru", "yanlış", "boş", "adımla",
    "kadar", "sabit", "bu",
}

# Türkçe klavyesi olmayanlar için ASCII yazımlar
ANAHTAR_ASCII = {ascii_yap(k): k for k in ANAHTAR if ascii_yap(k) != k}

ISLECLER = [
    "**=", "//=", "->", "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "%=",
    "**", "//", "+", "-", "*", "/", "%", "<", ">", "=", "(", ")", "[", "]",
    "{", "}", ",", ":", ".", "?", "&", "|", "!", ";", "@", "~", "^",
]

KESME = ("'", "’")


class Jeton:
    __slots__ = ("tur", "deger", "satir", "sutun", "ek", "ek_ham", "iyelik", "bosluk")

    def __init__(self, tur, deger, satir, sutun, bosluk=False):
        self.tur = tur          # SAYI METIN AD ANAHTAR ISLEC SATIR GIRINTI CIKINTI SON CPP
        self.deger = deger
        self.satir = satir
        self.sutun = sutun
        self.ek = None          # rol: i, e, de, den, in, le
        self.ek_ham = None      # yazıldığı gibi ek
        self.iyelik = False
        self.bosluk = bosluk    # öncesinde boşluk var mı

    def __repr__(self):
        e = f"'{self.ek_ham}" if self.ek_ham else ""
        return f"<{self.tur} {self.deger!r}{e} @{self.satir}:{self.sutun}>"


def _harf_mi(c):
    return c.isalpha() or c == "_"


def _ad_karakteri(c):
    return c.isalnum() or c == "_"


_CPP_BLOK = re.compile(r"^(\s*)cpp\s*:\s*(#.*)?$")


class SozcukAyirici:
    def __init__(self, kaynak, dosya=None, satir_ici=False, ilk_satir=1):
        self.k = kaynak.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
        if self.k.startswith("﻿"):
            self.k = self.k[1:]
        self.dosya = dosya
        self.satir_ici = satir_ici
        self.i = 0
        self.satir = ilk_satir
        self.sutun = 1
        self.jetonlar = []
        self.girintiler = [0]
        self.parantez = 0

    def hata(self, ileti, satir=None, sutun=None):
        raise SozcukHatasi(ileti, satir or self.satir, sutun or self.sutun, self.dosya)

    def bak(self, n=0):
        j = self.i + n
        return self.k[j] if j < len(self.k) else ""

    def ilerle(self, n=1):
        for _ in range(n):
            if self.i < len(self.k):
                if self.k[self.i] == "\n":
                    self.satir += 1
                    self.sutun = 1
                else:
                    self.sutun += 1
                self.i += 1

    def ekle(self, tur, deger, satir, sutun, bosluk):
        j = Jeton(tur, deger, satir, sutun, bosluk)
        self.jetonlar.append(j)
        return j

    # ------------------------------------------------------------------
    def ayir(self):
        satir_basi = True
        bosluk = False
        while self.i < len(self.k):
            if satir_basi and self.parantez == 0 and not self.satir_ici:
                satir_basi = False
                if self._satir_basi():
                    satir_basi = True
                    continue
                bosluk = True
            c = self.bak()
            if c == "\n":
                if self.parantez == 0 and not self.satir_ici:
                    if self.jetonlar and self.jetonlar[-1].tur != "SATIR":
                        self.ekle("SATIR", "\n", self.satir, self.sutun, False)
                    satir_basi = True
                self.ilerle()
                bosluk = True
                continue
            if c in " \t":
                self.ilerle()
                bosluk = True
                continue
            if c == "#":
                while self.i < len(self.k) and self.bak() != "\n":
                    self.ilerle()
                continue
            if c == "\\" and self.bak(1) == "\n":
                self.ilerle(2)
                bosluk = True
                continue
            satir, sutun = self.satir, self.sutun
            if c.isdigit():
                j = self._sayi(satir, sutun, bosluk)
            elif _harf_mi(c):
                j = self._ad(satir, sutun, bosluk)
            elif c == '"':
                j = self._metin(satir, sutun, bosluk)
            elif c in KESME:
                self.hata("Kesme işareti (') yalnızca bir sözcüğe ek bağlamak için "
                          "kullanılır, örn. liste'ye. Metinler için çift tırnak (\") kullanın.")
            else:
                j = self._islec(satir, sutun, bosluk)
            bosluk = False
            if j is not None and j.tur in ("SAYI", "METIN", "AD") or \
                    (j is not None and j.tur == "ISLEC" and j.deger in (")", "]")) or \
                    (j is not None and j.tur == "ANAHTAR" and j.deger in ("bu", "doğru", "yanlış")):
                self._ek_al(j)
        if not self.satir_ici:
            if self.jetonlar and self.jetonlar[-1].tur != "SATIR":
                self.ekle("SATIR", "\n", self.satir, self.sutun, False)
            while len(self.girintiler) > 1:
                self.girintiler.pop()
                self.ekle("CIKINTI", "", self.satir, 1, False)
        self.ekle("SON", "", self.satir, self.sutun, False)
        return self.jetonlar

    def _satir_basi(self):
        """Satır başındaki girintiyi işler. Boş/yorum satırıysa True döner."""
        bas = self.i
        sonu = self.k.find("\n", bas)
        if sonu == -1:
            sonu = len(self.k)
        satir_metni = self.k[bas:sonu]
        icerik = satir_metni.strip()
        if icerik == "" or icerik.startswith("#"):
            self.ilerle(sonu - bas)
            if self.i < len(self.k):
                self.ilerle()
            return True
        girinti = len(satir_metni) - len(satir_metni.lstrip(" "))
        self._girinti_ayarla(girinti)
        m = _CPP_BLOK.match(satir_metni)
        if m:
            self._cpp_blok(girinti, sonu)
            return True
        self.ilerle(girinti)
        return False

    def _girinti_ayarla(self, girinti):
        if girinti > self.girintiler[-1]:
            self.girintiler.append(girinti)
            self.ekle("GIRINTI", girinti, self.satir, 1, False)
        else:
            while girinti < self.girintiler[-1]:
                self.girintiler.pop()
                self.ekle("CIKINTI", "", self.satir, 1, False)
            if girinti != self.girintiler[-1]:
                self.hata("Girinti, önceki bloklardan hiçbiriyle uyuşmuyor.", self.satir, 1)

    def _cpp_blok(self, girinti, sonu):
        satir = self.satir
        self.ilerle(sonu - self.i)
        if self.i < len(self.k):
            self.ilerle()
        satirlar = []
        ic_girinti = None
        while self.i < len(self.k):
            s = self.k.find("\n", self.i)
            if s == -1:
                s = len(self.k)
            metin = self.k[self.i:s]
            if metin.strip() == "":
                satirlar.append("")
            else:
                g = len(metin) - len(metin.lstrip(" "))
                if g <= girinti:
                    break
                if ic_girinti is None:
                    ic_girinti = g
                satirlar.append(metin[min(g, ic_girinti):])
            self.ilerle(s - self.i)
            if self.i < len(self.k):
                self.ilerle()
        while satirlar and satirlar[-1] == "":
            satirlar.pop()
        self.ekle("CPP", "\n".join(satirlar), satir, 1, True)
        self.ekle("SATIR", "\n", satir, 1, False)

    def _sayi(self, satir, sutun, bosluk):
        bas = self.i
        if self.bak() == "0" and self.bak(1) in "xXbB" and self.bak(1):
            taban = 16 if self.bak(1) in "xX" else 2
            self.ilerle(2)
            while _ad_karakteri(self.bak()):
                self.ilerle()
            metin = self.k[bas:self.i].replace("_", "")
            try:
                return self.ekle("SAYI", int(metin, taban), satir, sutun, bosluk)
            except ValueError:
                self.hata(f"Geçersiz sayı: {metin}", satir, sutun)
        while self.bak().isdigit() or self.bak() == "_":
            self.ilerle()
        ondalik = False
        if self.bak() == "." and self.bak(1).isdigit():
            ondalik = True
            self.ilerle()
            while self.bak().isdigit() or self.bak() == "_":
                self.ilerle()
        if self.bak() in "eE" and (self.bak(1).isdigit() or (self.bak(1) in "+-" and self.bak(2).isdigit())):
            ondalik = True
            self.ilerle(2)
            while self.bak().isdigit():
                self.ilerle()
        metin = self.k[bas:self.i].replace("_", "")
        deger = float(metin) if ondalik else int(metin)
        return self.ekle("SAYI", deger, satir, sutun, bosluk)

    def _ad(self, satir, sutun, bosluk):
        bas = self.i
        while _ad_karakteri(self.bak()):
            self.ilerle()
        ad = self.k[bas:self.i]
        if ad in ANAHTAR:
            return self.ekle("ANAHTAR", ad, satir, sutun, bosluk)
        if ad in ANAHTAR_ASCII:
            return self.ekle("ANAHTAR", ANAHTAR_ASCII[ad], satir, sutun, bosluk)
        return self.ekle("AD", ad, satir, sutun, bosluk)

    def _metin(self, satir, sutun, bosluk):
        self.ilerle()  # "
        parcalar = []   # ("yazi", str) | ("ifade", str, satir, sutun)
        tampon = []
        kacis = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "0": "\0", "r": "\r",
                 "{": "{", "}": "}"}
        while True:
            c = self.bak()
            if c == "" or c == "\n":
                self.hata("Metin kapatılmamış; sonuna \" ekleyin.", satir, sutun)
            if c == '"':
                self.ilerle()
                break
            if c == "\\":
                n = self.bak(1)
                if n in kacis:
                    tampon.append(kacis[n])
                    self.ilerle(2)
                    continue
                self.hata(f"Bilinmeyen kaçış dizisi: \\{n}")
            if c == "{":
                if self.bak(1) == "{":
                    tampon.append("{")
                    self.ilerle(2)
                    continue
                if tampon:
                    parcalar.append(("yazi", "".join(tampon)))
                    tampon = []
                isatir, isutun = self.satir, self.sutun + 1
                self.ilerle()
                derinlik = 1
                ifade = []
                while True:
                    c2 = self.bak()
                    if c2 == "" or c2 == "\n":
                        self.hata("Metin içindeki { kapatılmamış.", isatir, isutun)
                    if c2 == "{":
                        derinlik += 1
                    elif c2 == "}":
                        derinlik -= 1
                        if derinlik == 0:
                            self.ilerle()
                            break
                    ifade.append(c2)
                    self.ilerle()
                parcalar.append(("ifade", "".join(ifade), isatir, isutun))
                continue
            if c == "}" and self.bak(1) == "}":
                tampon.append("}")
                self.ilerle(2)
                continue
            tampon.append(c)
            self.ilerle()
        if tampon or not parcalar:
            parcalar.append(("yazi", "".join(tampon)))
        return self.ekle("METIN", parcalar, satir, sutun, bosluk)

    def _islec(self, satir, sutun, bosluk):
        for isl in ISLECLER:
            if self.k.startswith(isl, self.i):
                self.ilerle(len(isl))
                if isl in "([{":
                    self.parantez += 1
                elif isl in ")]}":
                    self.parantez = max(0, self.parantez - 1)
                return self.ekle("ISLEC", isl, satir, sutun, bosluk)
        self.hata(f"Tanınmayan karakter: {self.bak()!r}")

    def _ek_al(self, j):
        if self.bak() in KESME and _harf_mi(self.bak(1)):
            satir, sutun = self.satir, self.sutun
            self.ilerle()
            bas = self.i
            while self.bak().isalpha():
                self.ilerle()
            ek = self.k[bas:self.i]
            cozum = ek_coz(ek)
            if cozum is None:
                self.hata(
                    f"'{ek}' eki tanınmadı. Geçerli ekler: -ı/-i (neyi), -a/-e (neye), "
                    f"-da/-de (nerede), -dan/-den (nereden), -ın/-in (kimin), -la/-le (neyle).",
                    satir, sutun)
            j.ek, j.iyelik = cozum
            j.ek_ham = ek
            if j.ek is None and j.iyelik:
                # x'i : tek başına iyelik mi belirtme mi? Belirtme varsayılır,
                # ayrıştırıcı ilgi zincirinde iyelik olarak yorumlar.
                j.ek = "i"


def ayir(kaynak, dosya=None):
    return SozcukAyirici(kaynak, dosya).ayir()
