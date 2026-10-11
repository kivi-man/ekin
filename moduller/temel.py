"""temel: yazma, okuma, dönüşümler. Her programa otomatik yüklenir."""

import sys

from ekin.calisma import metne, tam_yap, ondalik_yap, hata
from ekin.modul import Islev, Modul


def _yaz(*a):
    print(" ".join(metne(x) for x in a), flush=True)


def _yaz_satirsiz(*a):
    print(" ".join(metne(x) for x in a), end="", flush=True)


def _sor(soru=""):
    try:
        return input(metne(soru))
    except EOFError:
        return ""


def _uzunluk(x):
    if isinstance(x, (str, list)):
        return len(x)
    hata(f"uzunluk yalnızca metin ve liste için geçerlidir.")


def _tur(x):
    from ekin.yorumlayici import Yorumlayici
    return Yorumlayici.tur_adi(x)


def _aralik(a, b, adim=1):
    if adim == 0:
        hata("Aralık adımı sıfır olamaz.")
    if adim > 0:
        return list(range(a, b + 1, adim))
    return list(range(a, b - 1, adim))


def _iddia(kosul, ileti="iddia başarısız"):
    if not kosul:
        hata(f"İddia başarısız: {metne(ileti)}")


def _cik(kod=0):
    sys.exit(kod)


def _bos_mu(x):
    return x is None or (isinstance(x, (str, list)) and len(x) == 0)


def _mantik(x):
    if isinstance(x, str):
        return x.strip().lower() in ("doğru", "dogru", "evet", "1", "true")
    return bool(x)


def _tur_cpp(args, tipler):
    t = tipler[0] if tipler else "?"
    if t.startswith("liste["):
        t = "liste"
    return f'ekin::metin("{t}")'


MODUL = Modul(
    "temel",
    "Yazma, okuma ve tip dönüşümleri.",
    otomatik=True,
    islevler=[
        Islev("yaz(değer'i...)", py=_yaz, cpp="ekin::yaz({*})", gerekir=["seri"],
              aciklama="Değerleri aralarına boşluk koyarak yazar, satır atlar.",
              ornek='yaz "Merhaba", ad   |   "Merhaba"\'yı yaz'),
        Islev("yaz_satırsız(değer'i...)", py=_yaz_satirsiz, cpp="ekin::yaz_satirsiz({*})",
              gerekir=["seri"], aciklama="Satır atlamadan yazar."),
        Islev("sor(soru?)", py=_sor, cpp="ekin::sor({*})", donus="metin", gerekir=["seri"],
              aciklama="Kullanıcıdan bir satır okur.", ornek='ad = sor "Adın ne? "'),
        Islev("sayı_sor(soru?)", py=lambda s="": ondalik_yap(_sor(s)), cpp="ekin::ondalik_yap(ekin::sor({*}))",
              donus="ondalık", gerekir=["seri"], aciklama="Kullanıcıdan bir sayı okur."),
        Islev("tam_sor(soru?)", py=lambda s="": tam_yap(_sor(s)), cpp="ekin::tam_yap(ekin::sor({*}))",
              donus="tam", gerekir=["seri"], aciklama="Kullanıcıdan bir tam sayı okur."),
        Islev("uzunluk(x'in)", py=_uzunluk, cpp="ekin::uzunluk({0})", donus="tam",
              aciklama="Metnin harf sayısı ya da listenin öğe sayısı.",
              ornek="liste'nin uzunluğu   |   uzunluk(ad)"),
        Islev("tam(x)", py=tam_yap, cpp="ekin::tam_yap({0})", donus="tam",
              aciklama="Tam sayıya çevirir.", ornek='tam("42")'),
        Islev("ondalık(x)", py=ondalik_yap, cpp="ekin::ondalik_yap({0})", donus="ondalık",
              aciklama="Ondalık sayıya çevirir."),
        Islev("metin(x)", py=metne, cpp="ekin::metne({0})", donus="metin",
              aciklama="Metne çevirir."),
        Islev("mantık(x)", py=_mantik, cpp="ekin::mantik_yap({0})", donus="mantık",
              aciklama="Doğru/yanlış değerine çevirir."),
        Islev("tür(x'in)", py=_tur, cpp=_tur_cpp, donus="metin",
              aciklama="Değerin tipini metin olarak verir."),
        Islev("aralık(baş'tan, son'a, adım?)", py=_aralik, cpp="ekin::aralik({*})", donus="liste[tam]",
              aciklama="Baştan sona (ikisi dahil) sayılar listesi; geri saymak için negatif adım.",
              ornek="aralık(1, 5) -> [1, 2, 3, 4, 5]   aralık(5, 1, -2) -> [5, 3, 1]"),
        Islev("iddia(koşul, ileti?)", py=_iddia, cpp="ekin::iddia({*})",
              aciklama="Koşul yanlışsa programı hata ile durdurur."),
        Islev("çık(kod?)", py=_cik, cpp="ekin::cik({*})", aciklama="Programı bitirir."),
        Islev("boş_mu(x)", py=_bos_mu, cpp="ekin::bos_mu({0})", donus="mantık",
              aciklama="Metin ya da liste boşsa doğru."),
    ],
)
