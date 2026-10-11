"""Derleyicinin kullandığı tip yardımcıları.

Tipler metin olarak tutulur:
    "tam", "ondalık", "mantık", "metin", "renk", "hiç", "boş",
    "liste[tam]", "liste[?]"  (öğe tipi henüz bilinmiyor),
    "?"        (henüz bilinmiyor),
    "harici"   (C++ tarafından gelen, Ekin'in bilmediği değer),
    "işlev", yapı adları ("Nokta"), harici sınıf adları ("Servo").
"""

TEMEL_TIPLER = {"tam", "ondalık", "mantık", "metin", "renk", "hiç", "boş", "işlev"}
TIP_ASCII = {"ondalik": "ondalık", "mantik": "mantık", "hic": "hiç", "bos": "boş", "islev": "işlev"}
SAYISAL = {"tam", "ondalık"}


def tip_normal(t):
    if t is None:
        return None
    if t.startswith("liste[") and t.endswith("]"):
        return "liste[" + tip_normal(t[6:-1]) + "]"
    return TIP_ASCII.get(t, t)


def liste_mi(t):
    return isinstance(t, str) and t.startswith("liste[")


def oge_tipi(t):
    if liste_mi(t):
        return t[6:-1]
    if t == "metin":
        return "metin"
    return "?"


def bilinmiyor_mu(t):
    return t is None or t == "?" or (liste_mi(t) and bilinmiyor_mu(oge_tipi(t)))


def birlestir(a, b):
    """İki tipi birleştirir. Uyuşmazlıkta None döner."""
    if a is None or a == "?":
        return b
    if b is None or b == "?":
        return a
    if a == b:
        return a
    if a in SAYISAL and b in SAYISAL:
        return "ondalık"
    if liste_mi(a) and liste_mi(b):
        ic = birlestir(oge_tipi(a), oge_tipi(b))
        if ic is None:
            return None
        return f"liste[{ic}]"
    if a == "harici":
        return b
    if b == "harici":
        return a
    if a == "boş" or b == "boş":
        return b if a == "boş" else a
    return None


def sayisal_mi(t):
    return t in SAYISAL
