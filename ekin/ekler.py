"""Türkçe ek (morfoloji) yardımcıları.

Ekin'de hal ekleri, bir argümanın işlevdeki *rolünü* belirtir:

    5'i liste'ye ekle      ->  ekle(öğe=5, liste=liste)
    liste'ye 5'i ekle      ->  aynı çağrı (sıra serbest)

Roller (kısa adları):
    i    belirtme hâli   (-ı, -i, -u, -ü, -yı ...)   "neyi?"
    e    yönelme hâli    (-a, -e, -ya, -ye)          "neye?"
    de   bulunma hâli    (-da, -de, -ta, -te, -deki) "nerede?"
    den  ayrılma hâli    (-dan, -den, -tan, -ten)    "nereden?"
    in   ilgi hâli       (-ın, -in, -nın, -nin ...)  "kimin?"
    le   vasıta hâli     (-la, -le, -yla, -yle)      "neyle?"
"""

UNLULER = set("aeıioöuüâîû")
KALIN = set("aıouâû")

ROL_ADLARI = {
    "i": "belirtme (-ı/-i/-u/-ü)",
    "e": "yönelme (-a/-e)",
    "de": "bulunma (-da/-de)",
    "den": "ayrılma (-dan/-den)",
    "in": "ilgi (-ın/-in)",
    "le": "vasıta (-la/-le)",
}

# Doğrudan köke eklenebilen hal ekleri.
HAL_EKLERI = {
    "i": ["ı", "i", "u", "ü", "yı", "yi", "yu", "yü"],
    "e": ["a", "e", "ya", "ye"],
    "de": ["da", "de", "ta", "te", "daki", "deki", "taki", "teki"],
    "den": ["dan", "den", "tan", "ten"],
    "in": ["ın", "in", "un", "ün", "nın", "nin", "nun", "nün"],
    "le": ["la", "le", "yla", "yle"],
}

# İyelik ekinden (-ı, -sı ...) sonra gelen hal ekleri ("n" kaynaştırmalı).
IYELIK_SONRASI = {
    "i": ["nı", "ni", "nu", "nü"],
    "e": ["na", "ne"],
    "de": ["nda", "nde", "ndaki", "ndeki"],
    "den": ["ndan", "nden"],
    "in": ["nın", "nin", "nun", "nün"],
    "le": ["yla", "yle"],
}

IYELIK_EKLERI = ["sı", "si", "su", "sü", "ı", "i", "u", "ü"]

# Ünsüz yumuşamasını geri alma: kitabı -> kitap, rengi -> renk
YUMUSAMA_GERI = {"b": "p", "c": "ç", "d": "t", "ğ": "k", "g": "k"}

_TR_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜâîûÂÎÛ", "cgiosuCGIOSUaiuAIU")


def ascii_yap(s):
    """Türkçe karakterleri ASCII karşılıklarına çevirir (ş -> s)."""
    return s.translate(_TR_ASCII)


def tr_buyuk(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def tr_kucuk(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def _sirali(tablo):
    ciftler = [(ek, rol) for rol, ekler in tablo.items() for ek in ekler]
    ciftler.sort(key=lambda c: -len(c[0]))
    return ciftler


_HAL_SIRALI = _sirali(HAL_EKLERI)
_IYELIK_SONRASI_SIRALI = _sirali(IYELIK_SONRASI)


def ek_coz(ek):
    """Kesme işaretinden sonra yazılan eki çözer.

    Dönüş: (rol, iyelik_var_mi) ya da tanınmazsa None.
        "yi"     -> ("i", False)
        "nin"    -> ("in", False)
        "si"     -> (None, True)        # x'i -> iyelik/belirtme belirsiz
        "sinin"  -> ("in", True)
    """
    ek = tr_kucuk(ek)
    for rol, ekler in HAL_EKLERI.items():
        if ek in ekler:
            return (rol, False)
    # iyelik + hal: "sinin", "sini", "ını" ...
    for iy in IYELIK_EKLERI:
        if ek == iy:
            return (None, True)
        if ek.startswith(iy):
            kalan = ek[len(iy):]
            for rol, ekler in IYELIK_SONRASI.items():
                if kalan in ekler:
                    return (rol, True)
    return None


def son_unlu(kelime):
    for h in reversed(kelime):
        if h in UNLULER:
            return h
    return None


def _uyumlu(kok, ek):
    """Büyük ünlü uyumunu kabaca denetler (sadece belirsizliği çözmek için)."""
    a, b = son_unlu(kok), son_unlu(ek)
    if a is None or b is None:
        return True
    return (a in KALIN) == (b in KALIN)


def _kok_adaylari(govde):
    yield govde
    if govde and govde[-1] in YUMUSAMA_GERI:
        yield govde[:-1] + YUMUSAMA_GERI[govde[-1]]


def kok_bul(kelime, bilinen):
    """Kesme işaretsiz yazılmış ekli bir kelimenin kökünü bulur.

    bilinen: tanımlı isimler kümesi. Dönüş (kök, rol) ya da None.
        kok_bul("listeyi", {"liste"})  -> ("liste", "i")
        kok_bul("sayacı",  {"sayaç"})  -> ("sayaç", "i")
    """
    if kelime in bilinen:
        return (kelime, None)
    adaylar = []
    for ek, rol in _HAL_SIRALI:
        if kelime.endswith(ek) and len(kelime) > len(ek):
            govde = kelime[: -len(ek)]
            for kok in _kok_adaylari(govde):
                # Ünlü uyumu zorunlu: 'tone' -> 'ton'+'e' gibi yanlış eşleşmeleri önler.
                if kok in bilinen and _uyumlu(kok, ek):
                    adaylar.append((-len(ek), kok, rol))
    if not adaylar:
        return None
    adaylar.sort()
    _, kok, rol = adaylar[0]
    return (kok, rol)


def iyelik_coz(kelime, bilinen):
    """'uzunluğu', 'uzunluğunu', 'x'i' gibi iyelikli sözcüğün kökünü bulur.

    Dönüş (kök, rol): rol, iyelikten sonra gelen hal ekidir (yoksa None).
    Kök bulunamazsa (kelime, None) döner.
    """
    if kelime in bilinen:
        return (kelime, None)
    denemeler = [(kelime, None)]
    for ek, rol in _IYELIK_SONRASI_SIRALI:
        if kelime.endswith(ek) and len(kelime) > len(ek):
            denemeler.append((kelime[: -len(ek)], rol))
    for govde, rol in denemeler:
        for iy in IYELIK_EKLERI:
            if govde.endswith(iy) and len(govde) > len(iy):
                for kok in _kok_adaylari(govde[: -len(iy)]):
                    if kok in bilinen:
                        return (kok, rol)
    return (kelime, None)


def ek_oner(kok, rol):
    """Bir köke, verilen rol için ünlü uyumuna uygun eki üretir (hata iletileri için)."""
    u = son_unlu(kok) or "e"
    kalin = u in KALIN
    yuvarlak = u in "ouöü"
    unlu_bitis = kok[-1:] in UNLULER
    sert = kok[-1:] in set("fstkçşhp")
    if rol == "i":
        v = ("u" if yuvarlak else "ı") if kalin else ("ü" if yuvarlak else "i")
        return ("y" if unlu_bitis else "") + v
    if rol == "e":
        return ("y" if unlu_bitis else "") + ("a" if kalin else "e")
    if rol == "de":
        return ("t" if sert else "d") + ("a" if kalin else "e")
    if rol == "den":
        return ("t" if sert else "d") + ("an" if kalin else "en")
    if rol == "in":
        v = ("u" if yuvarlak else "ı") if kalin else ("ü" if yuvarlak else "i")
        return ("n" if unlu_bitis else "") + v + "n"
    if rol == "le":
        return ("y" if unlu_bitis else "") + ("la" if kalin else "le")
    return ""
