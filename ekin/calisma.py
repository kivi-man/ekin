"""Yorumlayıcı ile modüllerin paylaştığı çalışma zamanı yardımcıları."""

from .ekler import tr_buyuk, tr_kucuk  # noqa: F401  (modüller buradan alır)
from .hatalar import CalismaHatasi

# Komut satırı seçenekleri (modüller de okur)
SECENEKLER = {
    "hizli": False,        # bekle() gerçekten beklemesin (test/simülasyon)
    "tur_siniri": None,    # döngü: bloğu en fazla kaç kez çalışsın
    "kare_siniri": None,   # her_karede: en fazla kaç kare çizilsin
    "sessiz_sim": False,   # Arduino simülasyon iletilerini gizle
}


class Renk(tuple):
    """(kırmızı, yeşil, mavi, saydamlık) 0-255."""

    def __new__(cls, r, g, b, a=255):
        def k(v):
            return max(0, min(255, int(v)))
        return super().__new__(cls, (k(r), k(g), k(b), k(a)))

    @property
    def onaltilik(self):
        return "#%02x%02x%02x" % self[:3]

    def __repr__(self):
        if self[3] == 255:
            return f"renk({self[0]}, {self[1]}, {self[2]})"
        return f"renk({self[0]}, {self[1]}, {self[2]}, {self[3]})"


def kopya(v):
    """Değer semantiği: listeler ve yapılar atamada kopyalanır (C++ ile aynı)."""
    if isinstance(v, list):
        return [kopya(x) for x in v]
    k = getattr(v, "kopyala", None)
    if k is not None:
        return k()
    return v


def ondalik_bicim(x):
    if x != x:
        return "nan"
    if x in (float("inf"), float("-inf")):
        return "sonsuz" if x > 0 else "-sonsuz"
    s = format(x, ".10g")
    return s


def metne(v, ic=False):
    """Bir değeri ekrana yazılacak metne çevirir (C++ tarafıyla aynı biçim)."""
    if isinstance(v, bool):
        return "doğru" if v else "yanlış"
    if v is None:
        return "boş"
    if isinstance(v, float):
        return ondalik_bicim(v)
    if isinstance(v, str):
        return '"' + v + '"' if ic else v
    if isinstance(v, list):
        return "[" + ", ".join(metne(x, True) for x in v) + "]"
    if isinstance(v, Renk):
        return repr(v)
    return str(v)


def tam_yap(v):
    if isinstance(v, str):
        try:
            return int(v.strip())
        except ValueError:
            try:
                return int(float(v.strip()))
            except ValueError:
                return 0
    if isinstance(v, bool):
        return 1 if v else 0
    return int(v)


def ondalik_yap(v):
    if isinstance(v, str):
        try:
            return float(v.strip().replace(",", "."))
        except ValueError:
            return 0.0
    return float(v)


def hata(ileti):
    raise CalismaHatasi(ileti)
