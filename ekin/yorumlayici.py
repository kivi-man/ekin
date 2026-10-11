"""Ağaçta yürüyen yorumlayıcı (Ekin'in yorumlanan sürümü).

Derlenen sürümle aynı anlamı taşır: aralık döngüsü uçları dahil, `/` her zaman
ondalık böler, işlev içinde küresel değişkene atama o küresel değişkeni değiştirir.
"""

import time

from . import agac as A
from .calisma import metne, Renk, SECENEKLER, kopya
from .hatalar import CalismaHatasi, EkinHatasi
from .modul import rolleri_esle, Param


class _Don(Exception):
    def __init__(self, deger):
        self.deger = deger


class _Kir(Exception):
    pass


class _Devam(Exception):
    pass


class Cerceve:
    __slots__ = ("yerel", "bu")

    def __init__(self, bu=None):
        self.yerel = {}
        self.bu = bu


class EkinIslevi:
    def __init__(self, tanim, yorum, yapi=None):
        self.tanim = tanim
        self.yorum = yorum
        self.yapi = yapi
        self.params = [Param(p.ad, p.rol, p.varsayilan is not None) for p in tanim.parametreler]
        self.ad = tanim.ad

    def cagir(self, args, bu=None):
        y = self.yorum
        c = Cerceve(bu)
        tps = self.tanim.parametreler
        if len(args) > len(tps):
            raise CalismaHatasi(f"'{self.ad}' en fazla {len(tps)} argüman alır.", self.tanim.satir)
        for k, p in enumerate(tps):
            if k < len(args):
                c.yerel[p.ad] = kopya(args[k])
            elif p.varsayilan is not None:
                c.yerel[p.ad] = y.degerlendir(p.varsayilan, c)
            else:
                raise CalismaHatasi(f"'{self.ad}' işlevinin '{p.ad}' argümanı eksik.", self.tanim.satir)
        y.derinlik += 1
        if y.derinlik > 2000:
            raise CalismaHatasi("Çok derin özyineleme (yığın taştı).", self.tanim.satir)
        try:
            y.blok_calistir(self.tanim.govde, c)
        except _Don as d:
            return d.deger
        finally:
            y.derinlik -= 1
        return None

    def __call__(self, *args):
        return self.cagir(list(args))

    def __repr__(self):
        return f"<işlev {self.ad}>"


class BagliYontem:
    def __init__(self, nesne, islev):
        self.nesne = nesne
        self.islev = islev
        self.params = islev.params

    def __call__(self, *args):
        return self.islev.cagir(list(args), bu=self.nesne)


class EkinYapi:
    def __init__(self, tanim, yorum):
        self.tanim = tanim
        self.ad = tanim.ad
        self.yorum = yorum
        self.alanlar = [a[0] for a in tanim.alanlar_]
        self.params = [Param(a, None, True) for a in self.alanlar]
        self.yontemler = {m.ad: EkinIslevi(m, yorum, self) for m in tanim.yontemler}

    def __call__(self, *args):
        if len(args) > len(self.alanlar):
            raise CalismaHatasi(f"'{self.ad}' en fazla {len(self.alanlar)} değer alır.")
        n = EkinNesne(self)
        for k, (ad, _tip, vars_) in enumerate(self.tanim.alanlar_):
            if k < len(args):
                n.alanlar[ad] = kopya(args[k])
            elif vars_ is not None:
                n.alanlar[ad] = self.yorum.degerlendir(vars_, Cerceve())
            else:
                n.alanlar[ad] = 0
        return n

    def __repr__(self):
        return f"<yapı {self.ad}>"


class EkinNesne:
    def __init__(self, yapi):
        self.yapi = yapi
        self.alanlar = {}

    def __eq__(self, o):
        return isinstance(o, EkinNesne) and o.yapi is self.yapi and o.alanlar == self.alanlar

    def kopyala(self):
        n = EkinNesne(self.yapi)
        n.alanlar = {k: kopya(v) for k, v in self.alanlar.items()}
        return n

    def __repr__(self):
        ic = ", ".join(f"{k}={metne(v, True)}" for k, v in self.alanlar.items())
        return f"{self.yapi.ad}({ic})"


class LambdaDegeri:
    def __init__(self, dugum, cerceve, yorum):
        self.dugum = dugum
        self.cerceve = cerceve
        self.yorum = yorum
        self.params = [Param(p, None) for p in dugum.parametreler]

    def __call__(self, *args):
        c = Cerceve(self.cerceve.bu if self.cerceve else None)
        if self.cerceve:
            c.yerel.update(self.cerceve.yerel)
        for p, v in zip(self.dugum.parametreler, args):
            c.yerel[p] = kopya(v)
        return self.yorum.degerlendir(self.dugum.govde, c)


class DisIslevDegeri:
    def __init__(self, tanim):
        self.tanim = tanim
        self.params = [Param(p.ad, p.rol) for p in tanim.parametreler]

    def __call__(self, *args):
        raise CalismaHatasi(f"'{self.tanim.ad}' bir C++ (dış) işlevi; yalnızca derlenmiş sürümde "
                            f"çalışır: ekin derle dosya.ekin", self.tanim.satir)


class YerlesikDeger:
    """Modül işlevinin değer olarak kullanılması (ör. eşle(liste, karekök))."""

    def __init__(self, islev):
        self.islev = islev
        self.params = islev.params

    def __call__(self, *args):
        return self.islev.py(*args)


class Yorumlayici:
    def __init__(self, kayit, dosya=None):
        self.kayit = kayit
        self.dosya = dosya
        self.kuresel = {}
        self.ozel = {}            # kurulum, döngü, her_karede
        self.kuresel_adlar = set()
        self.derinlik = 0
        self.baslangic = time.time()
        self._baslatilan = set()

    # ------------------------------------------------------------ çalıştırma
    def calistir(self, program, son_kancalar=True):
        self._modulleri_baslat()
        self.tanimlari_kaydet(program.govde)
        self.kuresel_adlari_bul(program.govde)
        cerceve = None
        for d in program.govde:
            if isinstance(d, (A.IslevTanim, A.YapiTanim, A.DisIslev, A.DisSabit)):
                continue
            self.deyim(d, cerceve)
        if not son_kancalar:
            return
        self._modulleri_baslat()
        if "kurulum" in self.ozel:
            self.ozel["kurulum"].cagir([])
        if "döngü" in self.ozel:
            sinir = SECENEKLER.get("tur_siniri")
            n = 0
            try:
                while sinir is None or n < sinir:
                    self.ozel["döngü"].cagir([])
                    n += 1
            except KeyboardInterrupt:
                print("\n[durduruldu]")
        for m in list(self.kayit.moduller.values()):
            if m.py_bitis:
                m.py_bitis(self)

    def _modulleri_baslat(self):
        for ad, m in self.kayit.moduller.items():
            if ad not in self._baslatilan:
                self._baslatilan.add(ad)
                if m.py_baslat:
                    m.py_baslat(self)

    def tanimlari_kaydet(self, govde):
        for d in govde:
            if isinstance(d, A.IslevTanim):
                f = EkinIslevi(d, self)
                if d.tur in ("kurulum", "döngü", "her_karede"):
                    self.ozel[d.tur] = f
                else:
                    self.kuresel[d.ad] = f
            elif isinstance(d, A.YapiTanim):
                self.kuresel[d.ad] = EkinYapi(d, self)
            elif isinstance(d, A.DisIslev):
                self.kuresel[d.ad] = DisIslevDegeri(d)
            elif isinstance(d, A.DisSabit):
                pass

    def hata(self, ileti, dugum):
        raise CalismaHatasi(ileti, getattr(dugum, "satir", None), None, self.dosya)

    # ------------------------------------------------------------ deyimler
    def blok_calistir(self, govde, c):
        for d in govde:
            self.deyim(d, c)

    def deyim(self, d, c):
        try:
            return self._deyim(d, c)
        except EkinHatasi as e:
            if e.satir is None:
                e.satir = d.satir
                e.dosya = e.dosya or self.dosya
            raise
        except (_Don, _Kir, _Devam, KeyboardInterrupt, SystemExit):
            raise
        except RecursionError:
            raise CalismaHatasi("Çok derin özyineleme (yığın taştı).", d.satir, None, self.dosya)
        except ZeroDivisionError:
            raise CalismaHatasi("Sıfıra bölme.", d.satir, None, self.dosya)
        except Exception as e:  # modül işlevlerinden gelen Python hataları
            raise CalismaHatasi(f"{type(e).__name__}: {e}", d.satir, None, self.dosya)

    def _deyim(self, d, c):
        t = type(d)
        if t is A.IfadeDeyimi:
            self.degerlendir(d.ifade, c)
        elif t is A.Atama:
            self.atama(d, c)
        elif t is A.Eger:
            for kosul, govde in d.dallar:
                if self.dogru_mu(self.degerlendir(kosul, c)):
                    self.blok_calistir(govde, c)
                    return
            if d.degilse:
                self.blok_calistir(d.degilse, c)
        elif t is A.Iken:
            try:
                while self.dogru_mu(self.degerlendir(d.kosul, c)):
                    try:
                        self.blok_calistir(d.govde, c)
                    except _Devam:
                        pass
            except _Kir:
                pass
        elif t is A.Surekli:
            try:
                while True:
                    try:
                        self.blok_calistir(d.govde, c)
                    except _Devam:
                        pass
            except _Kir:
                pass
        elif t is A.AralikDongu:
            bas = self.degerlendir(d.bas, c)
            son = self.degerlendir(d.son, c)
            adim = self.degerlendir(d.adim, c) if d.adim else 1
            if adim == 0:
                self.hata("Döngü adımı sıfır olamaz.", d)
            i = bas
            try:
                while (i <= son) if adim > 0 else (i >= son):
                    self.ata_ad(d.degisken, i, c, dongu=True)
                    try:
                        self.blok_calistir(d.govde, c)
                    except _Devam:
                        pass
                    i += adim
            except _Kir:
                pass
        elif t is A.HerDongu:
            kume = self.degerlendir(d.kume, c)
            if not isinstance(kume, (list, str, tuple)):
                self.hata(f"'her' döngüsü liste ya da metin üzerinde çalışır, {self.tur_adi(kume)} verildi.", d)
            try:
                for x in list(kume):
                    self.ata_ad(d.degisken, kopya(x), c, dongu=True)
                    try:
                        self.blok_calistir(d.govde, c)
                    except _Devam:
                        pass
            except _Kir:
                pass
        elif t is A.Tekrarla:
            n = self.degerlendir(d.sayi, c)
            try:
                for _ in range(int(n)):
                    try:
                        self.blok_calistir(d.govde, c)
                    except _Devam:
                        pass
            except _Kir:
                pass
        elif t is A.Don:
            raise _Don(self.degerlendir(d.deger, c) if d.deger is not None else None)
        elif t is A.Kir:
            raise _Kir()
        elif t is A.Devam:
            raise _Devam()
        elif t is A.SabitTanim:
            self.kuresel[d.ad] = self.degerlendir(d.deger, c)
        elif t is A.Kullan:
            pass  # modüller ayrıştırmada yüklendi; dosyalar önyüzde birleştirildi
        elif t is A.HamCpp:
            pass  # yorumlayıcıda C++ bloğu yok sayılır
        elif t in (A.IslevTanim, A.YapiTanim, A.DisIslev, A.DisSabit):
            self.tanimlari_kaydet([d])
        elif t is A.Program:
            self.blok_calistir(d.govde, c)
        else:
            self.hata(f"Bilinmeyen deyim: {t.__name__}", d)

    def dogru_mu(self, v):
        return bool(v)

    # ------------------------------------------------------------ atama
    def kuresel_adlari_bul(self, govde):
        """En dış düzeyde atanan adlar (derleyiciyle aynı kural: statik olarak belirlenir)."""
        for d in govde:
            if isinstance(d, A.Atama) and isinstance(d.hedef, A.Ad):
                self.kuresel_adlar.add(d.hedef.ad)
            elif isinstance(d, (A.AralikDongu, A.HerDongu)):
                self.kuresel_adlar.add(d.degisken)
            elif isinstance(d, A.SabitTanim):
                self.kuresel_adlar.add(d.ad)
            if isinstance(d, A.Eger):
                for _k, g in d.dallar:
                    self.kuresel_adlari_bul(g)
                if d.degilse:
                    self.kuresel_adlari_bul(d.degilse)
            elif isinstance(d, (A.Iken, A.Surekli, A.AralikDongu, A.HerDongu, A.Tekrarla)):
                self.kuresel_adlari_bul(d.govde)

    def ata_ad(self, ad, deger, c, dongu=False):
        if c is None:
            tablo = self.kuresel
        elif ad in c.yerel or dongu:
            tablo = c.yerel              # işlev içindeki döngü değişkeni hep yereldir
        elif c.bu is not None and ad in c.bu.alanlar:
            tablo = c.bu.alanlar
        elif ad in self.kuresel_adlar:
            tablo = self.kuresel
        else:
            tablo = c.yerel
        if ad in tablo:
            self._tip_denetle(ad, tablo[ad], deger)
        tablo[ad] = deger

    def _tip_denetle(self, ad, eski, yeni):
        """Derlenmiş sürümle uyum: bir değişken tek bir tipte değer tutar (tam -> ondalık hariç)."""
        if eski is None or yeni is None:
            return
        a, b = self.tur_adi(eski), self.tur_adi(yeni)
        if a == b or {a, b} == {"tam", "ondalık"} or "işlev" in (a, b):
            return
        raise CalismaHatasi(f"'{ad}' değişkeni önce '{a}' tipindeydi, şimdi '{b}' veriliyor. "
                            f"Bir değişken tek bir tipte değer tutar.")

    def atama(self, d, c):
        deger = kopya(self.degerlendir(d.deger, c))
        h = d.hedef
        if d.islec != "=":
            eski = self.degerlendir(h, c)
            deger = self.ikili(d.islec[:-1], eski, deger, d)
        if isinstance(h, A.Ad):
            self.ata_ad(h.ad, deger, c)
        elif isinstance(h, A.Sira):
            nesne = self.degerlendir(h.nesne, c)
            sira = self.degerlendir(h.sira, c)
            if not isinstance(nesne, list):
                self.hata("Yalnızca liste öğelerine atama yapılabilir.", d)
            self._sira_denetle(nesne, sira, d)
            nesne[sira] = deger
        elif isinstance(h, A.Uye):
            nesne = self.degerlendir(h.nesne, c)
            if isinstance(nesne, EkinNesne):
                nesne.alanlar[h.ad] = deger
            else:
                self.hata(f"'{h.ad}' alanına atama yapılamaz.", d)

    # ------------------------------------------------------------ ifadeler
    def degerlendir(self, e, c):
        t = type(e)
        if t is A.Sayi or t is A.Mantik:
            return e.deger
        if t is A.Metin:
            if len(e.parcalar) == 1 and e.parcalar[0][0] == "yazi":
                return e.parcalar[0][1]
            return "".join(p[1] if p[0] == "yazi" else metne(self.degerlendir(p[1], c))
                           for p in e.parcalar)
        if t is A.Ad:
            return self.ad_bul(e.ad, c, e)
        if t is A.Bos:
            return None
        if t is A.Bu:
            if c is None or c.bu is None:
                self.hata("'bu' yalnızca yapı işlevlerinin içinde kullanılabilir.", e)
            return c.bu
        if t is A.Liste:
            return [kopya(self.degerlendir(x, c)) for x in e.ogeler]
        if t is A.IkiliIslem:
            if e.islec == "ve":
                return bool(self.degerlendir(e.sol, c)) and bool(self.degerlendir(e.sag, c))
            if e.islec == "veya":
                return bool(self.degerlendir(e.sol, c)) or bool(self.degerlendir(e.sag, c))
            return self.ikili(e.islec, self.degerlendir(e.sol, c), self.degerlendir(e.sag, c), e)
        if t is A.TekliIslem:
            v = self.degerlendir(e.deger, c)
            if e.islec == "değil":
                return not v
            if isinstance(v, (bool, str, list)) or v is None:
                self.hata(f"'-' işleci {self.tur_adi(v)} ile kullanılamaz.", e)
            return -v
        if t is A.Cagri:
            return self.cagri(e, c)
        if t is A.Sira:
            nesne = self.degerlendir(e.nesne, c)
            sira = self.degerlendir(e.sira, c)
            if isinstance(nesne, (list, str)):
                self._sira_denetle(nesne, sira, e)
                return nesne[sira]
            self.hata(f"{self.tur_adi(nesne)} sıra numarasıyla okunamaz.", e)
        if t is A.Uye:
            nesne = self.degerlendir(e.nesne, c)
            return self.uye(nesne, e.ad, e)
        if t is A.Iyelik:
            nesne = self.degerlendir(e.nesne, c)
            if isinstance(nesne, EkinNesne):
                if e.ad in nesne.alanlar:
                    return nesne.alanlar[e.ad]
                if e.ad in nesne.yapi.yontemler:
                    return BagliYontem(nesne, nesne.yapi.yontemler[e.ad])()
            f = self._islev_bul(e.ad, c)
            if f is not None:
                return f(nesne)
            self.hata(f"'{e.ad}' bulunamadı (ne alan ne de işlev).", e)
        if t is A.Lambda:
            return LambdaDegeri(e, c, self)
        self.hata(f"Bilinmeyen ifade: {t.__name__}", e)

    def _sira_denetle(self, nesne, sira, d):
        if isinstance(sira, bool) or not isinstance(sira, int):
            self.hata("Sıra numarası tam sayı olmalı.", d)
        if not 0 <= sira < len(nesne):
            self.hata(f"Sıra numarası {sira} dışarıda (uzunluk {len(nesne)}). İlk öğe 0'dır.", d)

    def ad_bul(self, ad, c, d):
        if c is not None:
            if ad in c.yerel:
                return c.yerel[ad]
            if c.bu is not None:
                if ad in c.bu.alanlar:
                    return c.bu.alanlar[ad]
                if ad in c.bu.yapi.yontemler:
                    return BagliYontem(c.bu, c.bu.yapi.yontemler[ad])
        if ad in self.kuresel:
            return self.kuresel[ad]
        s = self.kayit.sabit(ad)
        if s is not None:
            if s.py is None:
                self.hata(f"'{ad}' sabiti yorumlayıcıda yok (yalnızca derlenmiş sürümde).", d)
            return s.py
        f = self.kayit.islev(ad)
        if f is not None:
            return YerlesikDeger(f)
        m = self.kayit.oner(ad)
        if m:
            self.hata(f"'{ad}' '{m}' modülünde. Dosyanın başına 'kullan {m}' yazın.", d)
        self.hata(f"'{ad}' tanımlı değil. Önce bir değer atayın (ör. {ad} = 0).", d)

    def _islev_bul(self, ad, c):
        if c is not None and ad in c.yerel and callable(c.yerel[ad]):
            return c.yerel[ad]
        if ad in self.kuresel and callable(self.kuresel[ad]):
            return self.kuresel[ad]
        f = self.kayit.islev(ad)
        if f is not None:
            if f.py is None:
                raise CalismaHatasi(f"'{ad}' işlevi yorumlayıcıda yok; derlenmiş sürümde kullanılabilir.")
            return f.py
        return None

    def uye(self, nesne, ad, d):
        if isinstance(nesne, EkinNesne):
            if ad in nesne.alanlar:
                return nesne.alanlar[ad]
            if ad in nesne.yapi.yontemler:
                return BagliYontem(nesne, nesne.yapi.yontemler[ad])
            self.hata(f"'{nesne.yapi.ad}' yapısında '{ad}' adlı alan yok.", d)
        f = self._islev_bul(ad, None)
        if f is not None:
            return lambda *args: f(nesne, *args)
        if isinstance(nesne, Renk) and ad in ("kırmızı", "yeşil", "mavi", "saydamlık"):
            return nesne[["kırmızı", "yeşil", "mavi", "saydamlık"].index(ad)]
        self.hata(f"{self.tur_adi(nesne)} değerinin '{ad}' adlı bir özelliği yok.", d)

    def cagri(self, e, c):
        hedef = e.islev
        degerler = [(self.degerlendir(x, c), rol) for x, rol in e.argumanlar]
        # nesne.yöntem(...) ya da UFCS: liste.sırala()
        if isinstance(hedef, A.Uye):
            nesne = self.degerlendir(hedef.nesne, c)
            if isinstance(nesne, EkinNesne):
                if hedef.ad in nesne.yapi.yontemler:
                    f = BagliYontem(nesne, nesne.yapi.yontemler[hedef.ad])
                    return self._cagir(f, degerler, e, hedef.ad)
                if callable(nesne.alanlar.get(hedef.ad)):
                    return self._cagir(nesne.alanlar[hedef.ad], degerler, e, hedef.ad)
            yer = self.kayit.islev(hedef.ad)
            if yer is not None:
                return self._yerlesik(yer, [(nesne, None)] + degerler, e)
            f = self._islev_bul(hedef.ad, c)
            if f is not None:
                return self._cagir(f, [(nesne, None)] + degerler, e, hedef.ad)
            self.hata(f"{self.tur_adi(nesne)} değerinin '{hedef.ad}' adlı bir işlevi yok.", e)
        if isinstance(hedef, A.Ad):
            ad = hedef.ad
            f = None
            if c is not None and ad in c.yerel:
                f = c.yerel[ad]
            elif c is not None and c.bu is not None and ad in c.bu.yapi.yontemler:
                f = BagliYontem(c.bu, c.bu.yapi.yontemler[ad])
            elif ad in self.kuresel:
                f = self.kuresel[ad]
            else:
                yer = self.kayit.islev(ad)
                if yer is not None:
                    return self._yerlesik(yer, degerler, e)
                m = self.kayit.oner(ad)
                if m:
                    self.hata(f"'{ad}' komutu '{m}' modülünde. Dosyanın başına 'kullan {m}' yazın.", e)
                self.hata(f"'{ad}' adında bir işlev yok.", e)
            return self._cagir(f, degerler, e, ad)
        f = self.degerlendir(hedef, c)
        return self._cagir(f, degerler, e, "işlev")

    def _yerlesik(self, yer, degerler, e):
        if yer.py is None:
            self.hata(f"'{yer.ad}' işlevi yorumlayıcıda kullanılamaz; derleyin: "
                      f"ekin derle dosya.ekin", e)
        try:
            args = rolleri_esle(yer.params, yer.degisken, degerler, yer.ad)
        except EkinHatasi as h:
            self.hata(h.ileti, e)
        return yer.py(*args)

    def _cagir(self, f, degerler, e, ad):
        if not callable(f):
            self.hata(f"'{ad}' bir işlev değil, çağrılamaz.", e)
        params = getattr(f, "params", None)
        if params is not None:
            try:
                args = rolleri_esle(params, False, degerler, ad)
            except EkinHatasi as h:
                self.hata(h.ileti, e)
        else:
            args = [v for v, _ in degerler]
        if isinstance(f, EkinIslevi):
            return f.cagir(args)
        return f(*args)

    # ------------------------------------------------------------ işleçler
    @staticmethod
    def tur_adi(v):
        if isinstance(v, bool):
            return "mantık"
        if isinstance(v, int):
            return "tam"
        if isinstance(v, float):
            return "ondalık"
        if isinstance(v, str):
            return "metin"
        if isinstance(v, list):
            return "liste"
        if v is None:
            return "boş"
        if isinstance(v, Renk):
            return "renk"
        if isinstance(v, EkinNesne):
            return v.yapi.ad
        return "işlev" if callable(v) else type(v).__name__

    def ikili(self, op, a, b, d):
        try:
            if op == "+":
                if isinstance(a, str) or isinstance(b, str):
                    return metne(a) + metne(b)
                if isinstance(a, list) and isinstance(b, list):
                    return a + b
                self._sayi_denetle(op, a, b, d)
                return a + b
            if op in ("-", "*"):
                if op == "*" and isinstance(a, str) and isinstance(b, int):
                    return a * b
                self._sayi_denetle(op, a, b, d)
                return a - b if op == "-" else a * b
            if op == "/":
                self._sayi_denetle(op, a, b, d)
                if b == 0:
                    self.hata("Sıfıra bölme.", d)
                return a / b
            if op == "//":
                self._sayi_denetle(op, a, b, d)
                if b == 0:
                    self.hata("Sıfıra bölme.", d)
                return a // b
            if op == "%":
                self._sayi_denetle(op, a, b, d)
                if b == 0:
                    self.hata("Sıfıra bölme (mod).", d)
                return a % b
            if op == "**":
                self._sayi_denetle(op, a, b, d)
                if isinstance(a, int) and isinstance(b, int) and b >= 0:
                    return a ** b
                return float(a) ** float(b)
            if op == "==":
                return a == b
            if op == "!=":
                return a != b
            if op in ("<", ">", "<=", ">="):
                if isinstance(a, str) != isinstance(b, str):
                    self.hata(f"{self.tur_adi(a)} ile {self.tur_adi(b)} karşılaştırılamaz.", d)
                return {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]
        except TypeError:
            self.hata(f"'{op}' işleci {self.tur_adi(a)} ve {self.tur_adi(b)} ile kullanılamaz.", d)
        self.hata(f"Bilinmeyen işleç: {op}", d)

    def _sayi_denetle(self, op, a, b, d):
        for v in (a, b):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                self.hata(f"'{op}' işleci {self.tur_adi(a)} ve {self.tur_adi(b)} ile kullanılamaz.", d)
