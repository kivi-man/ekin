"""Modül sistemi.

Her modül, `moduller/` klasöründeki bir Python dosyasıdır ve `MODUL` adlı bir
`Modul` nesnesi tanımlar. Bir işlev aynı anda üç yerde çalışacak şekilde tarif edilir:

    Islev("ekle(öğe'yi, liste'ye)",
          py=lambda oge, liste: liste.append(oge),   # yorumlayıcı
          cpp="ekin::ekle({1}, {0})",                # PC derleyici (C++)
          ino=None,                                  # Arduino (yoksa cpp kullanılır)
          donus="hiç")

İmzadaki ekler (öğe'yi, liste'ye) argüman rollerini tanımlar; böylece
`5'i sayılar'a ekle` ile `sayılar'a 5'i ekle` aynı çağrıya dönüşür.
"""

import importlib.util
import os
import re

from .ekler import ek_coz, ascii_yap
from .hatalar import EkinHatasi

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YERLESIK_MODUL_KLASORU = os.path.join(KOK, "moduller")


class Param:
    __slots__ = ("ad", "rol", "istege_bagli")

    def __init__(self, ad, rol, istege_bagli=False):
        self.ad = ad
        self.rol = rol
        self.istege_bagli = istege_bagli


_IMZA = re.compile(r"^\s*([\w]+)\s*\((.*)\)\s*$")


def imza_coz(imza):
    m = _IMZA.match(imza)
    if not m:
        raise ValueError(f"Geçersiz imza: {imza}")
    ad, ic = m.group(1), m.group(2).strip()
    params, degisken = [], False
    if ic:
        for p in ic.split(","):
            p = p.strip()
            istege = False
            if p.endswith("..."):
                degisken = True
                p = p[:-3]
            if p.endswith("?"):
                istege = True
                p = p[:-1]
            rol = None
            if "'" in p:
                p, ek = p.split("'", 1)
                c = ek_coz(ek)
                rol = c[0] if c else None
            params.append(Param(p.strip(), rol, istege))
    return ad, params, degisken


class Islev:
    def __init__(self, imza, py=None, cpp=None, ino=None, donus="hiç", aciklama="",
                 ornek="", lambda_param=None, daralt=None, gerekir=None, takma=()):
        self.ad, self.params, self.degisken = imza_coz(imza)
        # ad hâli takma adları: "sayılar'ın toplamı" -> topla
        self.takma = list(takma)
        self.imza = imza
        self.py = py
        self.cpp = cpp
        self.ino = ino
        self.donus = donus
        self.aciklama = aciklama
        self.ornek = ornek
        # {arg_sırası: "$0[]"} -> o argümandaki lambda'nın parametre tipleri
        self.lambda_param = lambda_param or {}
        # {arg_sırası: "liste[$0]"} -> o argümandaki değişkenin tipini daralt
        self.daralt = daralt or {}
        self.gerekir = gerekir or []     # derlemede ek gereksinimler ("seri")
        self.modul = None

    @property
    def roller(self):
        return [p.rol for p in self.params]

    def sablon(self, hedef):
        """Hedefe göre C++ şablonu. ino=False ise işlev Arduino'da yoktur."""
        if hedef == "arduino":
            if self.ino is False:
                return None
            if self.ino is not None:
                return self.ino
        return self.cpp

    def donus_tipi(self, tipler, lambda_donus=None):
        d = self.donus
        if callable(d):
            if d.__code__.co_argcount >= 2:
                return d(tipler, lambda_donus or {})
            return d(tipler)
        return d


class Sabit:
    def __init__(self, ad, py=None, cpp=None, ino=None, tip="tam", aciklama=""):
        self.ad = ad
        self.py = py
        self.cpp = cpp if cpp is not None else repr(py)
        self.ino = ino
        self.tip = tip
        self.aciklama = aciklama
        self.modul = None

    def sablon(self, hedef):
        if hedef == "arduino" and self.ino is not None:
            return self.ino
        return self.cpp


class Modul:
    def __init__(self, ad, aciklama="", islevler=(), sabitler=(), basliklar=None,
                 baglama=None, hedefler=("py", "pc", "arduino"), otomatik=False,
                 py_baslat=None, py_bitis=None, kare_dongusu=None, bagimliliklar=()):
        self.ad = ad
        self.klasor = None                        # modül dosyasının klasörü
        self.bagimliliklar = list(bagimliliklar)  # önce yüklenecek modüller
        self.aciklama = aciklama
        self.islevler = list(islevler)
        self.sabitler = list(sabitler)
        self.basliklar = basliklar or {}      # {"pc": [...], "arduino": [...]}
        self.baglama = baglama or {}          # {"pc": callable(platform)->[bayraklar]}
        self.hedefler = set(hedefler)
        self.otomatik = otomatik
        self.py_baslat = py_baslat            # yorumlayıcı başlarken
        self.py_bitis = py_bitis              # program bitince (pencere döngüsü vb.)
        self.kare_dongusu = kare_dongusu      # {"pc": "ekin::grafik::calistir({0});"}
        for i in self.islevler:
            i.modul = self
        for s in self.sabitler:
            s.modul = self


def rolleri_esle(params, degisken, argumanlar, ad="işlev"):
    """Argümanları (ifade, rol) parametrelere yerleştirir.

    params: Param listesi (ya da rol listesi). Dönüş: sıralı argüman listesi.
    Ek taşıyan argüman, aynı ekli parametreye gider; eksizler kalan boşlukları
    soldan sağa doldurur.
    """
    roller = [p.rol if isinstance(p, Param) else p for p in params]
    istege = [p.istege_bagli if isinstance(p, Param) else False for p in params]
    n = len(roller)
    yer = [None] * n
    dolu = [False] * n
    kalan = []
    for ifade, rol in argumanlar:
        konuldu = False
        if rol:
            for k in range(n):
                if roller[k] == rol and not dolu[k]:
                    yer[k] = ifade
                    dolu[k] = True
                    konuldu = True
                    break
        if not konuldu:
            kalan.append(ifade)
    ek = []
    for ifade in kalan:
        for k in range(n):
            if not dolu[k]:
                yer[k] = ifade
                dolu[k] = True
                break
        else:
            if degisken:
                ek.append(ifade)
            else:
                raise EkinHatasi(f"'{ad}' en fazla {n} argüman alır, {len(argumanlar)} verildi.")
    # eksik argümanlar: yalnızca sondaki isteğe bağlı parametreler boş kalabilir
    for k in range(n):
        if not dolu[k]:
            istege_mi = istege[k] or (degisken and k == n - 1)
            if not istege_mi or any(dolu[j] for j in range(k + 1, n)):
                gerekli = sum(1 for j in range(n) if not (istege[j] or (degisken and j == n - 1)))
                raise EkinHatasi(f"'{ad}' işlevinin {k + 1}. argümanı ({_param_adi(params[k])}) eksik; "
                                 f"en az {gerekli} argüman gerekir.")
    return [yer[k] for k in range(n) if dolu[k]] + ek


def _param_adi(p):
    return p.ad if isinstance(p, Param) else str(p)


class Kayit:
    """Yüklenmiş modüllerin ve işlevlerinin kaydı."""

    def __init__(self, arama_yollari=()):
        self.moduller = {}
        self.islevler = {}
        self.sabitler = {}
        self.yollar = [p for p in arama_yollari if p]
        ortam = os.environ.get("EKIN_YOL")
        if ortam:
            self.yollar += ortam.split(os.pathsep)
        self.yollar.append(YERLESIK_MODUL_KLASORU)
        for ad in self.otomatik_moduller():
            self.yukle(ad)

    @staticmethod
    def tum_modul_adlari():
        adlar = []
        for f in sorted(os.listdir(YERLESIK_MODUL_KLASORU)):
            if f.endswith(".py") and not f.startswith("_"):
                adlar.append(f[:-3])
        return adlar

    def otomatik_moduller(self):
        return ["temel", "matematik", "metin", "liste", "zaman"]

    def _dosya_bul(self, ad):
        dosya_adi = ascii_yap(ad) + ".py"
        for yol in self.yollar:
            tam = os.path.join(yol, dosya_adi)
            if os.path.isfile(tam):
                return tam
        return None

    _onbellek = {}

    def _modul_dosyasi(self, ad, satir=None):
        dosya = self._dosya_bul(ad)
        if dosya is None:
            mevcut = ", ".join(self.tum_modul_adlari())
            raise EkinHatasi(f"'{ad}' adlı modül bulunamadı. Mevcut modüller: {mevcut}", satir)
        if dosya in Kayit._onbellek:
            return Kayit._onbellek[dosya]
        spec = importlib.util.spec_from_file_location(f"ekin_modul_{ad}", dosya)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modul = getattr(mod, "MODUL", None)
        if modul is None:
            raise EkinHatasi(f"{dosya} dosyasında MODUL tanımı yok.", satir)
        modul.klasor = os.path.dirname(os.path.abspath(dosya))
        Kayit._onbellek[dosya] = modul
        return modul

    def oner(self, ad):
        """Yüklenmemiş bir modülde bu adda işlev/sabit varsa modülün adını döner."""
        for m_ad in self.tum_modul_adlari():
            if m_ad in self.moduller:
                continue
            try:
                m = self._modul_dosyasi(m_ad)
            except Exception:  # noqa: BLE001
                continue
            adlar = set()
            for x in list(m.islevler) + list(m.sabitler):
                adlar |= {x.ad, ascii_yap(x.ad)}
                adlar |= set(getattr(x, "takma", ()))
            if ad in adlar:
                return m_ad
        return None

    def yukle(self, ad, satir=None):
        ad = ascii_yap(ad)
        if ad in self.moduller:
            return self.moduller[ad]
        modul = self._modul_dosyasi(ad, satir)
        for b in modul.bagimliliklar:
            self.yukle(b, satir)
        self.moduller[ad] = modul
        for i in modul.islevler:
            self._kaydet(self.islevler, i.ad, i)
            for t in i.takma:
                self._kaydet(self.islevler, t, i)
        for s in modul.sabitler:
            self._kaydet(self.sabitler, s.ad, s)
        return modul

    @staticmethod
    def _kaydet(tablo, ad, nesne):
        tablo[ad] = nesne
        a = ascii_yap(ad)
        if a != ad and a not in tablo:
            tablo[a] = nesne

    def islev(self, ad):
        return self.islevler.get(ad)

    def sabit(self, ad):
        return self.sabitler.get(ad)

    def tum_adlar(self):
        return set(self.islevler) | set(self.sabitler)
