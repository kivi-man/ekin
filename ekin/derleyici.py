"""Derleyici: Ekin programını C++ koduna çevirir.

Aşamalar:
  1. toplama   - işlevler, yapılar, küresel değişkenler, modüller
  2. tip çıkarımı (sabit nokta yinelemesi) - tip yazmadan statik tipler
  3. C++ üretimi - hedefe göre (pc, arduino, kütüphane)

Üretilen kod okunabilir C++'tır: Türkçe adlar ASCII'ye çevrilir (sayı -> sayi),
böylece çıktı herhangi bir C++ projesine kütüphane olarak eklenebilir.
"""

import re

from . import agac as A
from .ekler import ascii_yap
from .hatalar import DerlemeHatasi, TipHatasi, EkinHatasi
from .modul import rolleri_esle, Param
from .tipler import (birlestir, liste_mi, oge_tipi, tip_normal, bilinmiyor_mu, SAYISAL)

CPP_AYRILMIS = set("""
alignas alignof and and_eq asm auto bitand bitor bool break case catch char char16_t char32_t
char8_t class compl concept const consteval constexpr constinit const_cast continue co_await
co_return co_yield decltype default delete do double dynamic_cast else enum explicit export
extern false float for friend goto if inline int long mutable namespace new noexcept not not_eq
nullptr operator or or_eq private protected public register reinterpret_cast requires return
short signed sizeof static static_assert static_cast struct switch template this thread_local
throw true try typedef typeid typename union unsigned using virtual void volatile wchar_t while
xor xor_eq main setup loop ekin std metne abs min max round constrain map sq radians degrees PI
HALF_PI TWO_PI DEG_TO_RAD RAD_TO_DEG EULER HIGH LOW INPUT OUTPUT INPUT_PULLUP LED_BUILTIN String
Serial byte word boolean bit F delay millis micros random time exit printf puts
""".split())

ISLEC_CPP = {"==": "==", "!=": "!=", "<": "<", ">": ">", "<=": "<=", ">=": ">="}
RENK_ALANLARI = {"kırmızı": "r", "yeşil": "g", "mavi": "b", "saydamlık": "a",
                 "kirmizi": "r", "yesil": "g", "saydamlik": "a"}


class FonkBilgi:
    def __init__(self, tanim, yapi=None):
        self.tanim = tanim
        self.ad = tanim.ad
        self.yapi = yapi
        self.param_tipleri = [tip_normal(p.tip_adi) or "?" for p in tanim.parametreler]
        self.param_belirtildi = [p.tip_adi is not None for p in tanim.parametreler]
        self.donus = tip_normal(tanim.donus_tipi) or "?"
        self.donus_belirtildi = tanim.donus_tipi is not None
        self.params = [Param(p.ad, p.rol, p.varsayilan is not None) for p in tanim.parametreler]
        self.yerel = {}
        self.dondu = False   # değer döndüren 'dön' var mı


class YapiBilgi:
    def __init__(self, tanim):
        self.tanim = tanim
        self.ad = tanim.ad
        self.alanlar = {}
        self.belirtildi = {}
        for ad, tip, _ in tanim.alanlar_:
            self.alanlar[ad] = tip_normal(tip) or "?"
            self.belirtildi[ad] = tip is not None
        self.yontemler = {m.ad: FonkBilgi(m, self) for m in tanim.yontemler}


class Derleyici:
    def __init__(self, program, kayit, hedef="pc", dosya=None, kutuphane_adi=None):
        self.program = program
        self.kayit = kayit
        self.hedef = hedef            # "pc" | "arduino"
        self.dosya = dosya
        self.kutuphane_adi = kutuphane_adi
        self.fonklar = {}
        self.ozel = {}
        self.yapilar = {}
        self.dis_islevler = {}
        self.dis_sabitler = {}
        self.sabitler = {}            # ad -> (SabitTanim, tip)
        self.kuresel = {}
        self.ust_govde = []
        self.ust_cpp = []
        self.basliklar = []
        self.gerekenler = set()
        self.harici_adlar = set()
        self.uyarilar = []
        self.degisti = False
        self.son_tur = False
        # ad çevirme
        self._adlar = {}
        self._kullanilan = set()
        self._sayac = 0

    # ================================================================ hata
    def hata(self, ileti, dugum=None, tur=DerlemeHatasi):
        raise tur(ileti, getattr(dugum, "satir", None), None, self.dosya)

    # ================================================================ toplama
    def topla(self):
        for d in self.program.govde:
            if isinstance(d, A.IslevTanim):
                if d.tur in ("kurulum", "döngü", "her_karede"):
                    if d.tur in self.ozel:
                        self.hata(f"'{d.tur}' bloğu iki kez tanımlanmış.", d)
                    self.ozel[d.tur] = FonkBilgi(d)
                else:
                    if d.ad in self.fonklar:
                        self.hata(f"'{d.ad}' işlevi iki kez tanımlanmış.", d)
                    self.fonklar[d.ad] = FonkBilgi(d)
            elif isinstance(d, A.YapiTanim):
                self.yapilar[d.ad] = YapiBilgi(d)
            elif isinstance(d, A.DisIslev):
                self.dis_islevler[d.ad] = d
            elif isinstance(d, A.DisSabit):
                self.dis_sabitler[d.ad] = d
            elif isinstance(d, A.Kullan):
                if d.tur == "baslik":
                    self._baslik_ekle(d.ad)
                elif d.tur == "modul":
                    m = self.kayit.moduller.get(d.ad)
                    if m is not None and self.hedef not in m.hedefler and not self.kutuphane_adi:
                        hedefler = ", ".join(sorted(h for h in m.hedefler if h != "py"))
                        self.hata(f"'{d.ad}' modülü '{self.hedef}' hedefinde kullanılamaz "
                                  f"(desteklenen: {hedefler}).", d)
            elif isinstance(d, A.HamCpp):
                self.ust_cpp.append(d.kod)
            elif isinstance(d, A.SabitTanim):
                self.sabitler[d.ad] = [d, tip_normal(d.tip_adi) or "?"]
            else:
                self.ust_govde.append(d)
        if "her_karede" in self.ozel and "grafik" not in self.kayit.moduller:
            self.hata("'her_karede:' bloğu için 'kullan grafik' gerekir.", self.ozel["her_karede"].tanim)
        if self.hedef == "arduino":
            for m in self.kayit.moduller.values():
                if "arduino" not in m.hedefler:
                    self.hata(f"'{m.ad}' modülü Arduino'da kullanılamaz.")

    def _baslik_ekle(self, b):
        if b not in self.basliklar:
            self.basliklar.append(b)

    # ================================================================ tip çıkarımı
    def tip_cikar(self):
        for tur in range(30):
            self.degisti = False
            self._gecis()
            if not self.degisti:
                break
        self.son_tur = True
        self._gecis()
        self._son_denetim()

    def _gecis(self):
        # sabitler
        for ad, kayit in self.sabitler.items():
            d, tip = kayit
            self.kapsamlar = [{}]
            self.fonk = None
            self.yapi = None
            t = self.cikar(d.deger)
            kayit[1] = self._birlestir_bildir(tip, t, d, f"'{ad}' sabiti")
            if kayit[1] != tip:
                self.degisti = True
        # üst düzey
        self.fonk = None
        self.yapi = None
        self.kapsamlar = []
        self.blok_cikar(self.ust_govde)
        # yapı alanlarının varsayılanları
        for y in self.yapilar.values():
            for ad, _tip, vars_ in y.tanim.alanlar_:
                if vars_ is not None:
                    self.kapsamlar = [{}]
                    t = self.cikar(vars_)
                    self._alan_tip(y, ad, t, vars_)
        # işlevler
        for f in list(self.fonklar.values()) + list(self.ozel.values()):
            self._fonk_cikar(f)
        for y in self.yapilar.values():
            for m in y.yontemler.values():
                self._fonk_cikar(m, y)

    def _fonk_cikar(self, f, yapi=None):
        self.fonk = f
        self.yapi = yapi
        kapsam = {}
        for p, t in zip(f.tanim.parametreler, f.param_tipleri):
            kapsam[p.ad] = t
        self.kapsamlar = [kapsam]
        for k, p in enumerate(f.tanim.parametreler):
            if p.varsayilan is not None:
                t = self.cikar(p.varsayilan)
                if not f.param_belirtildi[k]:
                    yeni = birlestir(f.param_tipleri[k], t)
                    if yeni is not None and yeni != f.param_tipleri[k]:
                        f.param_tipleri[k] = yeni
                        self.degisti = True
        self.blok_cikar(f.tanim.govde)
        f.yerel = {a: t for a, t in kapsam.items() if a not in {p.ad for p in f.tanim.parametreler}}
        if f.dondu is False and not f.donus_belirtildi:
            if f.donus == "?":
                f.donus = "hiç"
        self.fonk = None
        self.yapi = None

    def _birlestir_bildir(self, eski, yeni, dugum, ne):
        b = birlestir(eski, yeni)
        if b is None:
            self.hata(f"{ne} önce '{eski}' tipinde kullanıldı, şimdi '{yeni}' veriliyor. "
                      f"Bir değişken tek bir tipte değer tutar.", dugum, TipHatasi)
        return b

    # ------------------------------------------------------------ kapsam
    def _ara(self, ad):
        """Değişkeni bulur: (tür, tip). tür: yerel | alan | kuresel | sabit"""
        for k in reversed(self.kapsamlar):
            if ad in k:
                return "yerel", k[ad]
        if self.yapi is not None and ad in self.yapi.alanlar:
            return "alan", self.yapi.alanlar[ad]
        if ad in self.kuresel:
            return "kuresel", self.kuresel[ad]
        if ad in self.sabitler:
            return "sabit", self.sabitler[ad][1]
        return None, None

    def _degisken_ata(self, ad, t, dugum, tip_adi=None):
        tur, eski = self._ara(ad)
        if tip_adi:
            t2 = tip_normal(tip_adi)
            t = birlestir(t2, t) and t2
            if t is None:
                self.hata(f"'{ad}' {t2} olarak tanımlandı ama başka tipte değer verildi.", dugum, TipHatasi)
        if tur == "sabit":
            self.hata(f"'{ad}' bir sabit; değeri değiştirilemez.", dugum)
        if tur is None:
            if self.fonk is None and not self.kapsamlar:
                self.kuresel[ad] = t
                self.degisti = True
            else:
                self.kapsamlar[0][ad] = t
            return
        yeni = self._birlestir_bildir(eski, t, dugum, f"'{ad}' değişkeni")
        if yeni != eski:
            if tur == "yerel":
                for k in reversed(self.kapsamlar):
                    if ad in k:
                        k[ad] = yeni
                        break
            elif tur == "alan":
                self.yapi.alanlar[ad] = yeni
                self.degisti = True
            elif tur == "kuresel":
                self.kuresel[ad] = yeni
                self.degisti = True

    def _dongu_degiskeni(self, ad, t, dugum):
        """İşlev içindeki döngü değişkeni her zaman yereldir; en dışta küreseldir."""
        if self.fonk is None:
            self._degisken_ata(ad, t, dugum)
            return
        k = self.kapsamlar[0]
        if ad in k:
            k[ad] = self._birlestir_bildir(k[ad], t, dugum, f"'{ad}' değişkeni")
        else:
            k[ad] = t

    def _alan_tip(self, yapi, ad, t, dugum):
        if ad not in yapi.alanlar:
            self.hata(f"'{yapi.ad}' yapısında '{ad}' alanı yok.", dugum)
        eski = yapi.alanlar[ad]
        if yapi.belirtildi.get(ad):
            if birlestir(eski, t) is None:
                self.hata(f"'{yapi.ad}.{ad}' alanı {eski} tipinde.", dugum, TipHatasi)
            return
        yeni = self._birlestir_bildir(eski, t, dugum, f"'{yapi.ad}.{ad}' alanı")
        if yeni != eski:
            yapi.alanlar[ad] = yeni
            self.degisti = True

    # ------------------------------------------------------------ deyimler
    def blok_cikar(self, govde):
        for d in govde:
            self.deyim_cikar(d)

    def deyim_cikar(self, d):
        t = type(d)
        if t is A.IfadeDeyimi:
            self.cikar(d.ifade)
        elif t is A.Atama:
            self._atama_cikar(d)
        elif t is A.Eger:
            for kosul, govde in d.dallar:
                self.cikar(kosul)
                self.blok_cikar(govde)
            if d.degilse:
                self.blok_cikar(d.degilse)
        elif t is A.Iken:
            self.cikar(d.kosul)
            self.blok_cikar(d.govde)
        elif t is A.Surekli:
            self.blok_cikar(d.govde)
        elif t is A.AralikDongu:
            tip = self.cikar(d.bas)
            tip = birlestir(tip, self.cikar(d.son))
            if d.adim:
                tip = birlestir(tip, self.cikar(d.adim))
            if tip not in SAYISAL:
                self.hata("Aralık döngüsünün uçları sayı olmalı.", d, TipHatasi)
            self._dongu_degiskeni(d.degisken, tip, d)
            self.blok_cikar(d.govde)
        elif t is A.HerDongu:
            kt = self.cikar(d.kume)
            if not (liste_mi(kt) or kt in ("metin", "harici", "?")):
                self.hata(f"'her' döngüsü liste ya da metin üzerinde çalışır ({kt} verildi).", d, TipHatasi)
            ot = oge_tipi(kt) if kt != "harici" else "harici"
            self._dongu_degiskeni(d.degisken, ot, d)
            self.blok_cikar(d.govde)
        elif t is A.Tekrarla:
            if self.cikar(d.sayi) not in ("tam", "harici", "?"):
                self.hata("'kez' sayısı tam sayı olmalı.", d, TipHatasi)
            self.blok_cikar(d.govde)
        elif t is A.Don:
            if self.fonk is None:
                self.hata("'dön' yalnızca bir işlevin içinde kullanılabilir.", d)
            if d.deger is not None:
                tip = self.cikar(d.deger)
                self.fonk.dondu = True
                f = self.fonk
                if f.donus_belirtildi:
                    if birlestir(f.donus, tip) is None:
                        self.hata(f"'{f.ad}' {f.donus} döndürmeli, {tip} döndürülüyor.", d, TipHatasi)
                else:
                    yeni = self._birlestir_bildir(None if f.donus == "hiç" else f.donus, tip, d,
                                                  f"'{f.ad}' işlevinin dönüş değeri")
                    if yeni != f.donus:
                        f.donus = yeni
                        self.degisti = True
        elif t in (A.Kir, A.Devam, A.HamCpp, A.Kullan):
            pass
        elif t is A.SabitTanim:
            self.hata("Sabitler yalnızca en dış düzeyde tanımlanabilir.", d)
        elif t in (A.IslevTanim, A.YapiTanim):
            self.hata("İşlev ve yapılar yalnızca en dış düzeyde tanımlanabilir.", d)
        else:
            self.hata(f"Bu deyim derlenemiyor: {t.__name__}", d)

    def _atama_cikar(self, d):
        h = d.hedef
        if d.islec == "=":
            beklenen = tip_normal(d.tip_adi)
            if beklenen is None and isinstance(h, A.Ad):
                beklenen = self._ara(h.ad)[1]   # ör. isimler = [] -> sonradan bulunan liste[metin]
            vt = self.cikar(d.deger, beklenen=beklenen)
        else:
            sol = self.cikar(h)
            sag = self.cikar(d.deger)
            vt = self._ikili_tip(d.islec[:-1], sol, sag, d)
        if isinstance(h, A.Ad):
            self._degisken_ata(h.ad, vt, d, d.tip_adi)
            h.tip = self._ara(h.ad)[1]
        elif isinstance(h, A.Sira):
            kt = self.cikar(h.nesne)
            self.cikar(h.sira)
            if liste_mi(kt):
                self._daralt(h.nesne, f"liste[{vt}]")
            elif kt not in ("harici", "?"):
                self.hata("Yalnızca liste öğelerine atama yapılabilir.", d, TipHatasi)
        elif isinstance(h, A.Uye):
            nt = self.cikar(h.nesne)
            if nt in self.yapilar:
                self._alan_tip(self.yapilar[nt], h.ad, vt, d)

    def _daralt(self, ifade, tip):
        """Bir değişkenin/alanın tipini (ör. liste[?] -> liste[tam]) daraltır."""
        if isinstance(ifade, A.Ad):
            tur, eski = self._ara(ifade.ad)
            if tur is not None and tur != "sabit":
                self._degisken_ata(ifade.ad, tip, ifade)
        elif isinstance(ifade, A.Uye):
            nt = self.cikar(ifade.nesne)
            if nt in self.yapilar:
                self._alan_tip(self.yapilar[nt], ifade.ad, tip, ifade)

    # ------------------------------------------------------------ ifadeler
    def cikar(self, e, beklenen=None):
        t = self._cikar(e, beklenen)
        e.tip = t
        return t

    def _cikar(self, e, beklenen=None):
        t = type(e)
        if t is A.Sayi:
            return "ondalık" if isinstance(e.deger, float) else "tam"
        if t is A.Metin:
            for p in e.parcalar:
                if p[0] == "ifade":
                    self.cikar(p[1])
            return "metin"
        if t is A.Mantik:
            return "mantık"
        if t is A.Bos:
            return "boş"
        if t is A.Bu:
            if self.yapi is None:
                self.hata("'bu' yalnızca yapı işlevlerinin içinde kullanılabilir.", e)
            return self.yapi.ad
        if t is A.Ad:
            return self._ad_tip(e)
        if t is A.Liste:
            ot = "?"
            if beklenen and liste_mi(beklenen):
                ot = oge_tipi(beklenen)
            for x in e.ogeler:
                xt = self.cikar(x)
                yeni = birlestir(ot, xt)
                if yeni is None:
                    self.hata(f"Listedeki öğeler aynı tipte olmalı ({ot} ve {xt} karışık).", e, TipHatasi)
                ot = yeni
            return f"liste[{ot}]"
        if t is A.IkiliIslem:
            sol = self.cikar(e.sol)
            sag = self.cikar(e.sag)
            return self._ikili_tip(e.islec, sol, sag, e)
        if t is A.TekliIslem:
            v = self.cikar(e.deger)
            if e.islec == "değil":
                return "mantık"
            if v not in SAYISAL and v not in ("harici", "?"):
                self.hata(f"'-' işleci {v} ile kullanılamaz.", e, TipHatasi)
            return v
        if t is A.Sira:
            nt = self.cikar(e.nesne)
            st = self.cikar(e.sira)
            if st not in ("tam", "harici", "?"):
                self.hata("Sıra numarası tam sayı olmalı.", e, TipHatasi)
            if liste_mi(nt):
                return oge_tipi(nt)
            if nt == "metin":
                return "metin"
            if nt in ("harici", "?"):
                return nt
            self.hata(f"{nt} sıra numarasıyla okunamaz.", e, TipHatasi)
        if t is A.Uye:
            return self._uye_tip(e)
        if t is A.Iyelik:
            return self._iyelik_tip(e)
        if t is A.Cagri:
            return self._cagri_tip(e)
        if t is A.Lambda:
            return self._lambda_tip(e, getattr(e, "param_tipleri", None))
        self.hata(f"Bu ifade derlenemiyor: {t.__name__}", e)

    def _ad_tip(self, e):
        tur, tip = self._ara(e.ad)
        if tur is not None:
            e.cozum = tur
            return tip
        if e.ad in self.dis_sabitler:
            e.cozum = "dis_sabit"
            return tip_normal(self.dis_sabitler[e.ad].tip_adi) or "harici"
        if e.ad in self.fonklar or (self.yapi is not None and e.ad in self.yapi.yontemler):
            e.cozum = "fonk"
            return "işlev"
        s = self.kayit.sabit(e.ad)
        if s is not None:
            e.cozum = "modul_sabit"
            return s.tip
        if self.kayit.islev(e.ad) is not None:
            e.cozum = "yerlesik"
            return "işlev"
        e.cozum = "harici"
        if self.son_tur:
            self._tanimsiz_denetle(e.ad, e)
            self.harici_adlar.add(e.ad)
        return "harici"

    def _cpp_kullaniliyor(self):
        """Program C++ başlığı, cpp: bloğu ya da dış tanım kullanıyor mu?"""
        if not hasattr(self, "_cpp_var"):
            kod = [d for d in self.program.govde]
            var = bool(self.basliklar or self.ust_cpp or self.dis_islevler or self.dis_sabitler)

            def gez(x):
                nonlocal var
                if isinstance(x, A.HamCpp):
                    var = True
                for v in vars(x).values():
                    for o in (v if isinstance(v, list) else [v]):
                        if isinstance(o, A.Dugum):
                            gez(o)
            for d in kod:
                gez(d)
            self._cpp_var = var
        return self._cpp_var

    def _tanimsiz_denetle(self, ad, dugum):
        """Tanımsız ad: Arduino/C++ adıysa olduğu gibi aktarılır, değilse hata verilir."""
        if ascii_yap(ad) == ad and ad.isascii() and (self.hedef == "arduino" or self._cpp_kullaniliyor()):
            return
        m = self.kayit.oner(ad)
        if m:
            self.hata(f"'{ad}' '{m}' modülünde. Dosyanın başına 'kullan {m}' yazın.", dugum)
        self.hata(f"'{ad}' tanımlı değil. Önce bir değer atayın (ör. {ad} = 0); "
                  f"bir C++ adıysa ilgili başlığı 'kullan <...>' ile ekleyin.", dugum)

    def _ikili_tip(self, op, a, b, d):
        if "harici" in (a, b) or "?" in (a, b):
            if op in ("==", "!=", "<", ">", "<=", ">=", "ve", "veya"):
                return "mantık"
            if op == "/":
                return "ondalık"
            if op == "+" and "metin" in (a, b):
                return "metin"
            return b if a in ("harici", "?") else a
        if op in ("ve", "veya"):
            return "mantık"
        if op in ("==", "!="):
            if birlestir(a, b) is None:
                self.hata(f"{a} ile {b} karşılaştırılamaz.", d, TipHatasi)
            return "mantık"
        if op in ("<", ">", "<=", ">="):
            if not ((a in SAYISAL and b in SAYISAL) or (a == b == "metin")):
                self.hata(f"{a} ile {b} büyüklük karşılaştırması yapılamaz.", d, TipHatasi)
            return "mantık"
        if op == "+":
            if a == "metin" or b == "metin":
                return "metin"
            if liste_mi(a) and liste_mi(b):
                r = birlestir(a, b)
                if r is None:
                    self.hata(f"{a} ile {b} birleştirilemez.", d, TipHatasi)
                return r
        if op == "*" and a == "metin" and b == "tam":
            return "metin"
        if a not in SAYISAL or b not in SAYISAL:
            self.hata(f"'{op}' işleci {a} ve {b} ile kullanılamaz.", d, TipHatasi)
        if op == "/":
            return "ondalık"
        if op == "**":
            return "tam" if a == b == "tam" else "ondalık"
        return birlestir(a, b)

    def _uye_tip(self, e):
        nt = self.cikar(e.nesne)
        if nt in self.yapilar:
            y = self.yapilar[nt]
            if e.ad in y.alanlar:
                e.cozum = "alan"
                return y.alanlar[e.ad]
            if e.ad in y.yontemler:
                e.cozum = "yontem"
                return "işlev"
            self.hata(f"'{nt}' yapısında '{e.ad}' adlı alan yok.", e, TipHatasi)
        if nt == "renk" and e.ad in RENK_ALANLARI:
            e.cozum = "renk"
            return "tam"
        e.cozum = "harici"
        return "harici"

    def _iyelik_tip(self, e):
        nt = self.cikar(e.nesne)
        if nt in self.yapilar:
            y = self.yapilar[nt]
            if e.ad in y.alanlar:
                e.cozum = A.Uye(e.nesne, e.ad, satir=e.satir)
                return self.cikar(e.cozum)
            if e.ad in y.yontemler:
                e.cozum = A.Cagri(A.Uye(e.nesne, e.ad, satir=e.satir), [], satir=e.satir)
                return self.cikar(e.cozum)
        if nt == "renk" and e.ad in RENK_ALANLARI:
            e.cozum = A.Uye(e.nesne, e.ad, satir=e.satir)
            return self.cikar(e.cozum)
        if e.ad in self.fonklar or self.kayit.islev(e.ad) is not None or e.ad in self.dis_islevler:
            e.cozum = A.Cagri(A.Ad(e.ad, satir=e.satir), [(e.nesne, None)], satir=e.satir)
            return self.cikar(e.cozum)
        e.cozum = A.Uye(e.nesne, e.ad, satir=e.satir)
        return self.cikar(e.cozum)

    def _lambda_tip(self, e, param_tipleri):
        param_tipleri = param_tipleri or ["?"] * len(e.parametreler)
        e.param_tipleri = param_tipleri
        self.kapsamlar.append(dict(zip(e.parametreler, param_tipleri)))
        try:
            e.donus = self.cikar(e.govde)
        finally:
            self.kapsamlar.pop()
        return "işlev"

    # ------------------------------------------------------------ çağrılar
    def _sirala(self, params, degisken, argumanlar, ad, e):
        try:
            return rolleri_esle(params, degisken, argumanlar, ad)
        except EkinHatasi as h:
            self.hata(h.ileti, e)

    def _cagri_tip(self, e):
        hedef = e.islev
        if isinstance(hedef, A.Uye):
            nt = self.cikar(hedef.nesne)
            if nt in self.yapilar and hedef.ad in self.yapilar[nt].yontemler:
                m = self.yapilar[nt].yontemler[hedef.ad]
                args = self._sirala(m.params, False, e.argumanlar, hedef.ad, e)
                e.cozum = ("yontem", m, args, hedef.nesne)
                return self._kullanici_cagri(m, args, e)
            ad = hedef.ad
            if ad in self.fonklar or self.kayit.islev(ad) is not None or ad in self.dis_islevler:
                # UFCS: liste.sırala() -> sırala(liste)
                return self._ad_cagri(ad, [(hedef.nesne, None)] + list(e.argumanlar), e)
            for x, _ in e.argumanlar:
                self.cikar(x)
            e.cozum = ("harici_uye", hedef.nesne, ad, [x for x, _ in e.argumanlar])
            return "harici"
        if isinstance(hedef, A.Ad):
            return self._ad_cagri(hedef.ad, list(e.argumanlar), e)
        self.cikar(hedef)
        for x, _ in e.argumanlar:
            self.cikar(x)
        e.cozum = ("ifade", hedef, [x for x, _ in e.argumanlar])
        return "harici"

    def _ad_cagri(self, ad, argumanlar, e):
        # yapı içinde kardeş yöntem
        if self.yapi is not None and ad in self.yapi.yontemler and self._ara(ad)[0] is None:
            m = self.yapi.yontemler[ad]
            args = self._sirala(m.params, False, argumanlar, ad, e)
            e.cozum = ("yontem", m, args, None)
            return self._kullanici_cagri(m, args, e)
        if ad in self.fonklar:
            f = self.fonklar[ad]
            args = self._sirala(f.params, False, argumanlar, ad, e)
            e.cozum = ("kullanici", f, args)
            return self._kullanici_cagri(f, args, e)
        if ad in self.yapilar:
            y = self.yapilar[ad]
            alanlar = list(y.alanlar)
            if len(argumanlar) > len(alanlar):
                self.hata(f"'{ad}' en fazla {len(alanlar)} değer alır.", e)
            args = [x for x, _ in argumanlar]
            for a, x in zip(alanlar, args):
                self._alan_tip(y, a, self.cikar(x), x)
            e.cozum = ("yapi", y, args)
            return ad
        if ad in self.dis_islevler:
            d = self.dis_islevler[ad]
            params = [Param(p.ad, p.rol, p.varsayilan is not None) for p in d.parametreler]
            args = self._sirala(params, False, argumanlar, ad, e)
            for x in args:
                self.cikar(x)
            e.cozum = ("dis", d, args)
            return tip_normal(d.donus_tipi) or "hiç"
        yer = self.kayit.islev(ad)
        if yer is not None:
            return self._yerlesik_cagri(yer, argumanlar, e)
        # yerel bir lambda/işlev değişkeni ya da C++ işlevi
        for x, _ in argumanlar:
            self.cikar(x)
        if self._ara(ad)[0] is not None:
            e.cozum = ("ifade", A.Ad(ad, satir=e.satir), [x for x, _ in argumanlar])
            self.cikar(e.cozum[1])
            return "harici"
        if self.son_tur:
            self._tanimsiz_denetle(ad, e)
            self.harici_adlar.add(ad)
        e.cozum = ("harici", ad, [x for x, _ in argumanlar])
        if ad[:1].isupper():
            return f"sınıf:{ad}"
        return "harici"

    def _kullanici_cagri(self, f, args, e):
        for k, x in enumerate(args):
            xt = self.cikar(x)
            if k >= len(f.param_tipleri):
                continue
            if f.param_belirtildi[k]:
                if birlestir(f.param_tipleri[k], xt) is None:
                    self.hata(f"'{f.ad}' işlevinin '{f.params[k].ad}' parametresi {f.param_tipleri[k]} "
                              f"bekliyor, {xt} verildi.", e, TipHatasi)
                continue
            yeni = self._birlestir_bildir(f.param_tipleri[k], xt, e, f"'{f.ad}' işlevinin '{f.params[k].ad}' parametresi")
            if yeni != f.param_tipleri[k]:
                f.param_tipleri[k] = yeni
                self.degisti = True
        return f.donus

    def _yerlesik_cagri(self, yer, argumanlar, e):
        args = self._sirala(yer.params, yer.degisken, argumanlar, yer.ad, e)
        # işlev adı verilmiş lambda yuvalarını lambda'ya çevir: eşle(l, karekök)
        for k in yer.lambda_param:
            if k < len(args) and isinstance(args[k], A.Ad) and not isinstance(args[k], A.Lambda):
                ad = args[k].ad
                if ad in self.fonklar or self.kayit.islev(ad) is not None:
                    p = A.Ad("_x", satir=e.satir)
                    args[k] = A.Lambda(["_x"], A.Cagri(A.Ad(ad, satir=e.satir), [(p, None)], satir=e.satir),
                                       satir=e.satir)
        tipler = [None] * len(args)
        for k, x in enumerate(args):
            if k not in yer.lambda_param:
                tipler[k] = self.cikar(x)
        lambda_donus = {}
        for k, ifade in yer.lambda_param.items():
            if k < len(args):
                pt = self._tip_ifadesi(ifade, tipler, {})
                if isinstance(args[k], A.Lambda):
                    args[k].param_tipleri = [pt] * len(args[k].parametreler)
                    tipler[k] = self.cikar(args[k])
                    lambda_donus[k] = args[k].donus
                else:
                    tipler[k] = self.cikar(args[k])
        for k, ifade in yer.daralt.items():
            if k < len(args):
                self._daralt(args[k], self._tip_ifadesi(ifade, tipler, lambda_donus))
                tipler[k] = self.cikar(args[k])
        donus = yer.donus_tipi(tipler, lambda_donus)
        donus = self._tip_ifadesi(donus, tipler, lambda_donus)
        e.cozum = ("yerlesik", yer, args, tipler)
        return tip_normal(donus)

    @staticmethod
    def _tip_ifadesi(s, tipler, lambda_donus):
        if not isinstance(s, str):
            return s

        def t(i):
            i = int(i)
            return tipler[i] if i < len(tipler) and tipler[i] else "?"
        s = re.sub(r"\$(\d)\[\]", lambda m: oge_tipi(t(m.group(1))), s)
        s = re.sub(r"\$(\d)", lambda m: t(m.group(1)), s)
        s = re.sub(r"@(\d)", lambda m: lambda_donus.get(int(m.group(1)), "?"), s)
        return s

    # ------------------------------------------------------------ son denetim
    def _son_denetim(self):
        for ad, t in self.kuresel.items():
            if bilinmiyor_mu(t) and t != "harici":
                self.hata(f"'{ad}' değişkeninin tipi bulunamadı. Tipini yazın, ör. {ad}: liste[tam] = []")
        for f in list(self.fonklar.values()) + list(self.ozel.values()):
            for a, t in f.yerel.items():
                if bilinmiyor_mu(t) and t != "harici":
                    self.hata(f"'{f.ad}' içindeki '{a}' değişkeninin tipi bulunamadı. "
                              f"Tipini yazın, ör. {a}: liste[tam] = []", f.tanim)

    # ================================================================ C++ adları
    def cad(self, ad):
        """Ekin adını geçerli, okunabilir bir C++ adına çevirir."""
        if ad in self._adlar:
            return self._adlar[ad]
        a = ascii_yap(ad)
        a = re.sub(r"[^A-Za-z0-9_]", "_", a)
        if not a or a[0].isdigit():
            a = "_" + a
        if a in CPP_AYRILMIS or re.fullmatch(r"B[01]+", a) or a.startswith("__"):
            a = a + "_"
        temel, n = a, 2
        while a in self._kullanilan:
            a = f"{temel}_{n}"
            n += 1
        self._kullanilan.add(a)
        self._adlar[ad] = a
        return a

    def gecici(self, on="e"):
        self._sayac += 1
        return f"_{on}{self._sayac}"

    def ctip(self, t, dugum=None):
        t = tip_normal(t)
        if t == "tam":
            return "ekin::tam"
        if t == "ondalık":
            return "ekin::ondalik"
        if t == "mantık":
            return "bool"
        if t == "metin":
            return "ekin::metin"
        if t == "renk":
            return "ekin::Renk"
        if t == "hiç":
            return "void"
        if t == "boş":
            return "std::nullptr_t"
        if liste_mi(t):
            ic = oge_tipi(t)
            if bilinmiyor_mu(ic):
                self.hata("Listenin öğe tipi bulunamadı. Tipini yazın, ör. x: liste[tam] = []", dugum)
            return f"ekin::Liste<{self.ctip(ic, dugum)}>"
        if t in self.yapilar:
            return self.cad(t)
        if t.startswith("sınıf:"):
            return t[6:]
        if t in ("harici", "işlev", "?"):
            return "auto"
        return t  # harici C++ tip adı (tip açıklamasında yazılmış)

    # ================================================================ üretim
    def derle(self):
        self.topla()
        self.tip_cikar()
        kod = self._uret()
        if self.harici_adlar:
            adlar = ", ".join(sorted(self.harici_adlar))
            self.uyarilar.append(f"Ekin'de tanımlı olmayan adlar C++'a olduğu gibi aktarıldı: {adlar}")
        return kod

    def _uret(self):
        self.cikti = []
        self.girinti = 0
        kutuphane = self.kutuphane_adi is not None
        # gövdeleri önce üret (kullanılan başlıkları/gereksinimleri toplamak için)
        govde = []
        self.cikti = govde
        self._yapilari_uret(kutuphane)
        self._kureselleri_uret(kutuphane)
        self._islevleri_uret(kutuphane)
        if not kutuphane:
            self._giris_uret()
        else:
            if self.ust_govde:
                self.uyarilar.append("Kütüphane çıktısında en dış düzeydeki komutlar (atama dışında) yok sayıldı.")
        on = []
        on.append(f"// Ekin derleyicisi tarafından üretildi. Kaynak: {self.dosya or '?'}")
        on.append(f"// Hedef: {'kütüphane' if kutuphane else self.hedef}")
        if kutuphane:
            on.append("#pragma once")
        if self.hedef == "arduino":
            on.append("#include <Arduino.h>")
            if "seri" in self.gerekenler:
                on.append("#define EKIN_SERI 1")
        on.append('#include "ekin.hpp"')
        for m in self.kayit.moduller.values():
            for b in m.basliklar.get(self.hedef, []):
                if b not in self.basliklar:
                    self.basliklar.append(b)
        for g in sorted(self.gerekenler):
            if g.startswith("<") or g.startswith('"'):
                self._baslik_ekle(g)
        for b in self.basliklar:
            on.append(f"#include {b}")
        if "<Servo.h>" in self.basliklar:
            on.append('#include "ekin_servo.hpp"')
        on.append("")
        for kod in self.ust_cpp:
            on.append(kod)
            on.append("")
        if kutuphane:
            on.append(f"namespace {self.cad(self.kutuphane_adi)} {{")
            on.append("")
        son = []
        if kutuphane:
            son = ["", f"}}  // namespace {self.cad(self.kutuphane_adi)}"]
        return "\n".join(on + govde + son) + "\n"

    def yaz(self, satir=""):
        self.cikti.append(("    " * self.girinti + satir) if satir else "")

    # ------------------------------------------------------------ yapılar
    def _yapi_sirasi(self):
        sira, ziyaret = [], set()

        def gez(y, yol=()):
            if y.ad in ziyaret:
                return
            if y.ad in yol:
                self.hata(f"'{y.ad}' yapısı kendini (dolaylı olarak) içeriyor.", y.tanim)
            for t in y.alanlar.values():
                ic = t
                while liste_mi(ic):
                    ic = oge_tipi(ic)
                if ic in self.yapilar and not liste_mi(t):
                    gez(self.yapilar[ic], yol + (y.ad,))
            ziyaret.add(y.ad)
            sira.append(y)
        for y in self.yapilar.values():
            gez(y)
        return sira

    def _yapilari_uret(self, kutuphane):
        if not self.yapilar:
            return
        inl = "inline " if kutuphane else ""
        self.yaz("// ---- yapılar")
        for y in self.yapilar.values():
            self.yaz(f"struct {self.cad(y.ad)};")
        self.yaz()
        for y in self._yapi_sirasi():
            ya = self.cad(y.ad)
            self.yaz(f"struct {ya} {{")
            self.girinti += 1
            vars_ = {ad: v for ad, _t, v in y.tanim.alanlar_}
            self.yapi, self.fonk, self.kapsamlar = y, None, [{}]
            for ad, t in y.alanlar.items():
                if bilinmiyor_mu(t):
                    self.hata(f"'{y.ad}.{ad}' alanının tipi bulunamadı; tipini yazın: {ad}: tam = 0", y.tanim)
                ilk = f" = {self.ifade(vars_[ad])}" if vars_.get(ad) is not None else "{}"
                self.yaz(f"{self.ctip(t)} {self.cad(ad)}{ilk};")
            if y.alanlar:
                self.yaz(f"{ya}() {{}}")
                params = []
                for k, (ad, t) in enumerate(y.alanlar.items()):
                    p = f"{self.ctip(t)} {self.cad(ad)}_"
                    if k > 0:
                        v = vars_.get(ad)
                        p += f" = {self.ifade(v)}" if v is not None else f" = {self.ctip(t)}{{}}"
                    params.append(p)
                bas = ", ".join(f"{self.cad(a)}({self.cad(a)}_)" for a in y.alanlar)
                self.yaz(f"{ya}({', '.join(params)}) : {bas} {{}}")
                esit = " && ".join(f"{self.cad(a)} == o.{self.cad(a)}" for a in y.alanlar)
                self.yaz(f"bool operator==(const {ya}& o) const {{ return {esit}; }}")
                self.yaz(f"bool operator!=(const {ya}& o) const {{ return !(*this == o); }}")
            for m in y.yontemler.values():
                self.yaz(self._imza(m, sinif=None, varsayilan=True) + ";")
            self.girinti -= 1
            self.yaz("};")
            # metne: yaz/metin içinde gösterim
            parcalar = []
            for k, a in enumerate(y.alanlar):
                on = (", " if k else "") + f"{a}="
                parcalar.append(f'ekin::metin("{on}") + ekin::metne_ic(n.{self.cad(a)})')
            ic = " + ".join(parcalar) if parcalar else 'ekin::metin("")'
            self.yaz(f'{inl}ekin::metin metne(const {ya}& n) {{ return ekin::metin("{y.ad}(") + {ic} + ekin::metin(")"); }}')
            self.yaz()
            self.yapi = None

    def _imza(self, f, sinif=None, varsayilan=False):
        params = []
        sablon = []
        for k, p in enumerate(f.tanim.parametreler):
            t = f.param_tipleri[k]
            if bilinmiyor_mu(t) or t in ("harici", "işlev"):
                tn = f"T{k}"
                sablon.append(f"typename {tn}")
                ct = tn
            else:
                ct = self.ctip(t, f.tanim)
                if t == "metin" or liste_mi(t) or t in self.yapilar:
                    ct = f"const {ct}&" if not self._parametre_degisir(f, p.ad) else ct
            s = f"{ct} {self.cad(p.ad)}"
            if varsayilan and p.varsayilan is not None:
                self.fonk = f
                self.kapsamlar = [dict(zip([q.ad for q in f.tanim.parametreler], f.param_tipleri))]
                s += f" = {self.ifade(p.varsayilan)}"
            params.append(s)
        donus = self._donus_ctip(f)
        ad = self.cad(f.ad)
        if sinif:
            ad = f"{sinif}::{ad}"
        on = f"template<{', '.join(sablon)}> " if sablon else ""
        return f"{on}{donus} {ad}({', '.join(params)})"

    def _parametre_degisir(self, f, ad):
        """Parametreye işlev içinde atama yapılıyor mu (const& kullanılamaz)?"""
        bulundu = []

        def gez(x):
            if isinstance(x, A.Atama):
                h = x.hedef
                while isinstance(h, (A.Sira, A.Uye)):
                    h = h.nesne
                if isinstance(h, A.Ad) and h.ad == ad:
                    bulundu.append(True)
            if isinstance(x, A.Cagri) and getattr(x, "cozum", None) and x.cozum[0] == "yerlesik":
                yer, args = x.cozum[1], x.cozum[2]
                if yer.ad in ("ekle", "çıkar", "sil", "araya_ekle", "temizle") or yer.daralt:
                    for a in args:
                        if isinstance(a, A.Ad) and a.ad == ad:
                            bulundu.append(True)
            if isinstance(x, A.Cagri) and getattr(x, "cozum", None) and x.cozum[0] in ("harici_uye",):
                h = x.cozum[1]
                if isinstance(h, A.Ad) and h.ad == ad:
                    bulundu.append(True)
            for v in vars(x).values():
                if isinstance(v, A.Dugum):
                    gez(v)
                elif isinstance(v, (list, tuple)):
                    for o in v:
                        if isinstance(o, A.Dugum):
                            gez(o)
                        elif isinstance(o, (list, tuple)):
                            for o2 in o:
                                if isinstance(o2, A.Dugum):
                                    gez(o2)
                                elif isinstance(o2, list):
                                    for o3 in o2:
                                        if isinstance(o3, A.Dugum):
                                            gez(o3)
        for d in f.tanim.govde:
            gez(d)
        return bool(bulundu)

    def _donus_ctip(self, f):
        t = f.donus
        if t in ("?", "hiç") and not f.dondu:
            return "void"
        if t in ("harici", "işlev") or bilinmiyor_mu(t):
            if self.hedef == "arduino":
                self.hata(f"'{f.ad}' işlevinin dönüş tipi bulunamadı; yazın: işlev {f.ad}(...) -> tam:", f.tanim)
            return "auto"
        return self.ctip(t, f.tanim)

    # ------------------------------------------------------------ küreseller
    def _kureselleri_uret(self, kutuphane):
        inl = "inline " if kutuphane else ""
        if self.sabitler:
            self.yaz("// ---- sabitler")
        for ad, (d, t) in self.sabitler.items():
            self.fonk, self.yapi, self.kapsamlar = None, None, [{}]
            ct = self.ctip(t, d) if t != "harici" else "auto"
            self.yaz(f"{inl}const {ct} {self.cad(ad)} = {self.ifade(d.deger)};")
        if self.sabitler:
            self.yaz()
        self._dogrudan_kurulan = set()
        harici = []
        if self.kuresel:
            self.yaz("// ---- küresel değişkenler")
        kesme_degiskenleri = self._kesme_degiskenleri()
        for ad, t in self.kuresel.items():
            if t.startswith("sınıf:") or t == "harici":
                harici.append(ad)
                continue
            # kesme işlevinde değişen sayısal küreseller 'volatile' olmalı
            vol = "volatile " if ad in kesme_degiskenleri and t in ("tam", "ondalık", "mantık") else ""
            self.yaz(f"{inl}{vol}{self.ctip(t)} {self.cad(ad)}{{}};")
        # C++ sınıfı tipindeki küreseller: ilk atamadaki kurucuyla doğrudan oluştur
        for ad in harici:
            ilk = self._ilk_atama(ad)
            if ilk is not None and isinstance(ilk.deger, A.Cagri) and getattr(ilk.deger, "cozum", None) \
                    and ilk.deger.cozum[0] == "harici" and ilk.deger.cozum[1][:1].isupper():
                sinif, args = ilk.deger.cozum[1], ilk.deger.cozum[2]
                self.fonk, self.yapi, self.kapsamlar = None, None, []
                a = ", ".join(self.ifade(x) for x in args)
                self.yaz(f"{inl}{sinif} {self.cad(ad)}{'(' + a + ')' if a else ''};")
                self._dogrudan_kurulan.add(id(ilk))
            elif ilk is not None:
                self.fonk, self.yapi, self.kapsamlar = None, None, []
                self.yaz(f"{inl}decltype({self.ifade(ilk.deger)}) {self.cad(ad)};")
            else:
                self.hata(f"'{ad}' değişkeninin tipi bulunamadı.")
        if self.kuresel:
            self.yaz()

    def _kesme_degiskenleri(self):
        """kesme_bağla ile verilen işlevlerin atama yaptığı küresel adlar."""
        islevler, adlar = set(), set()

        def gez(x, gorev):
            if isinstance(x, A.Cagri) and getattr(x, "cozum", None) and x.cozum[0] == "yerlesik" \
                    and x.cozum[1].ad == "kesme_bağla" and len(x.cozum[2]) > 1 and isinstance(x.cozum[2][1], A.Ad):
                islevler.add(x.cozum[2][1].ad)
            if gorev and isinstance(x, A.Atama) and isinstance(x.hedef, A.Ad) and x.hedef.ad in self.kuresel:
                adlar.add(x.hedef.ad)
            for v in vars(x).values():
                for o in (v if isinstance(v, (list, tuple)) else [v]):
                    for o2 in (o if isinstance(o, (list, tuple)) else [o]):
                        if isinstance(o2, A.Dugum):
                            gez(o2, gorev)
                        elif isinstance(o2, list):
                            for o3 in o2:
                                if isinstance(o3, A.Dugum):
                                    gez(o3, gorev)
        tum = self.ust_govde + [f.tanim for f in list(self.fonklar.values()) + list(self.ozel.values())]
        for d in tum:
            gez(d, False)
        for ad in islevler:
            if ad in self.fonklar:
                gez(self.fonklar[ad].tanim, True)
        return adlar

    def _ilk_atama(self, ad):
        for d in self.ust_govde:
            if isinstance(d, A.Atama) and isinstance(d.hedef, A.Ad) and d.hedef.ad == ad and d.islec == "=":
                return d
        return None

    # ------------------------------------------------------------ işlevler
    def _islevleri_uret(self, kutuphane):
        inl = "inline " if kutuphane else ""
        hepsi = list(self.fonklar.values())
        if hepsi:
            self.yaz("// ---- işlev bildirimleri")
            for f in hepsi:
                if not self._sablon_mu(f):
                    self.yaz(inl + self._imza(f, varsayilan=True) + ";")
            self.yaz()
        for y in self.yapilar.values():
            for m in y.yontemler.values():
                self._islev_govdesi(m, self._imza(m, sinif=self.cad(y.ad)), y)
        for f in hepsi:
            imza = self._imza(f, varsayilan=self._sablon_mu(f))
            self._islev_govdesi(f, inl + imza if not self._sablon_mu(f) else imza)
        for tur, ad in (("kurulum", "ekin_kurulum"), ("döngü", "ekin_dongu"), ("her_karede", "ekin_her_karede")):
            if tur in self.ozel:
                self._islev_govdesi(self.ozel[tur], f"void {ad}()")

    def _sablon_mu(self, f):
        return any(bilinmiyor_mu(t) or t in ("harici", "işlev") for t in f.param_tipleri)

    def _islev_govdesi(self, f, imza, yapi=None):
        self.fonk, self.yapi = f, yapi
        self.kapsamlar = [dict(zip([p.ad for p in f.tanim.parametreler], f.param_tipleri))]
        self.kapsamlar[0].update(f.yerel)
        self.bildirilen = set()
        self.yaz(imza + " {")
        self.girinti += 1
        for ad, t in f.yerel.items():
            if t in ("harici",) or t.startswith("sınıf:"):
                continue
            self.yaz(f"{self.ctip(t, f.tanim)} {self.cad(ad)}{{}};")
            self.bildirilen.add(ad)
        self.blok(f.tanim.govde)
        self.girinti -= 1
        self.yaz("}")
        self.yaz()
        self.fonk, self.yapi = None, None

    def _giris_uret(self):
        self.fonk, self.yapi, self.kapsamlar = None, None, []
        self.bildirilen = set(self.kuresel)
        kare = None
        if "grafik" in self.kayit.moduller:
            kd = self.kayit.moduller["grafik"].kare_dongusu.get(self.hedef)
            if kd:
                kare = kd.format("ekin_her_karede" if "her_karede" in self.ozel else "nullptr")
        if self.hedef == "arduino":
            self.yaz("void setup() {")
            self.girinti += 1
            self.yaz("ekin::baslat();")
            self._ust_komutlar()
            if "kurulum" in self.ozel:
                self.yaz("ekin_kurulum();")
            self.girinti -= 1
            self.yaz("}")
            self.yaz()
            self.yaz("void loop() {")
            self.girinti += 1
            if "döngü" in self.ozel:
                self.yaz("ekin_dongu();")
            self.girinti -= 1
            self.yaz("}")
            return
        self.yaz("int main(int argc, char** argv) {")
        self.girinti += 1
        self.yaz("ekin::baslat(argc, argv);")
        self._ust_komutlar()
        if "kurulum" in self.ozel:
            self.yaz("ekin_kurulum();")
        if "döngü" in self.ozel:
            self.yaz("while (true) ekin_dongu();")
        if kare:
            self.yaz(kare)
        self.yaz("return 0;")
        self.girinti -= 1
        self.yaz("}")

    def _ust_komutlar(self):
        for d in self.ust_govde:
            if id(d) in getattr(self, "_dogrudan_kurulan", ()):
                continue
            self.deyim(d)

    # ------------------------------------------------------------ deyim üretimi
    def blok(self, govde):
        for d in govde:
            self.deyim(d)

    def deyim(self, d):
        try:
            self._deyim(d)
        except EkinHatasi as e:
            if e.satir is None:
                e.satir = d.satir
            raise

    def _deyim(self, d):
        t = type(d)
        if t is A.IfadeDeyimi:
            self.yaz(self.ifade(d.ifade) + ";")
        elif t is A.Atama:
            self._atama(d)
        elif t is A.Eger:
            for k, (kosul, govde) in enumerate(d.dallar):
                on = "if" if k == 0 else "} else if"
                self.yaz(f"{on} ({self._kosul(kosul)}) {{")
                self.girinti += 1
                self.blok(govde)
                self.girinti -= 1
            if d.degilse:
                self.yaz("} else {")
                self.girinti += 1
                self.blok(d.degilse)
                self.girinti -= 1
            self.yaz("}")
        elif t is A.Iken:
            self.yaz(f"while ({self._kosul(d.kosul)}) {{")
            self.girinti += 1
            self.blok(d.govde)
            self.girinti -= 1
            self.yaz("}")
        elif t is A.Surekli:
            self.yaz("while (true) {")
            self.girinti += 1
            self.blok(d.govde)
            self.girinti -= 1
            self.yaz("}")
        elif t is A.AralikDongu:
            self._aralik(d)
        elif t is A.HerDongu:
            o = self.gecici("o")
            kt = d.kume.tip
            kume = self.ifade(d.kume)
            if kt == "metin":
                kume = f"ekin::harfler({kume})"
            self.yaz(f"for (const auto& {o} : {kume}) {{")
            self.girinti += 1
            self.yaz(f"{self._ad_hedef(d.degisken)} = {o};")
            self.blok(d.govde)
            self.girinti -= 1
            self.yaz("}")
        elif t is A.Tekrarla:
            i, n = self.gecici("i"), self.gecici("n")
            self.yaz(f"for (ekin::tam {i} = 0, {n} = {self.ifade(d.sayi)}; {i} < {n}; ++{i}) {{")
            self.girinti += 1
            self.blok(d.govde)
            self.girinti -= 1
            self.yaz("}")
        elif t is A.Don:
            if d.deger is None:
                self.yaz("return;")
            else:
                self.yaz(f"return {self.ifade(d.deger)};")
        elif t is A.Kir:
            self.yaz("break;")
        elif t is A.Devam:
            self.yaz("continue;")
        elif t is A.HamCpp:
            for s in d.kod.splitlines():
                self.yaz(s)
        elif t is A.Kullan:
            pass
        else:
            self.hata(f"Bu deyim derlenemiyor: {t.__name__}", d)

    def _kosul(self, e):
        s = self.ifade(e)
        if s.startswith("(") and s.endswith(")") and self._dengeli(s[1:-1]):
            return s[1:-1]
        return s

    @staticmethod
    def _dengeli(s):
        d = 0
        for c in s:
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
                if d < 0:
                    return False
        return d == 0

    def _ad_hedef(self, ad):
        tur, _ = self._ara(ad)
        if tur == "alan":
            return self.cad(ad)
        return self.cad(ad)

    def _aralik(self, d):
        tip = self.ctip(self._ara(d.degisken)[1] or "tam")
        v = self._ad_hedef(d.degisken)
        c = self.gecici("c")
        # adım sabitse (ya da yoksa) yön derleme anında bellidir: sade bir for döngüsü
        sabit = d.adim is None or isinstance(d.adim, A.Sayi)
        if sabit:
            adim = d.adim.deger if d.adim else 1
            if adim == 0:
                self.hata("Döngü adımı sıfır olamaz.", d)
            son = self.ifade(d.son)
            if not isinstance(d.son, (A.Sayi, A.Ad)):
                s = self.gecici("son")
                self.yaz(f"{{ const {tip} {s} = {son};")
                son = s
            if adim > 0:
                kosul, art = f"{c} <= {son}", (f"++{c}" if adim == 1 else f"{c} += {adim}")
            else:
                kosul, art = f"{c} >= {son}", (f"--{c}" if adim == -1 else f"{c} -= {-adim}")
            self.yaz(f"for ({tip} {c} = {self.ifade(d.bas)}; {kosul}; {art}) {{")
            ek_kapanis = not isinstance(d.son, (A.Sayi, A.Ad))
        else:
            s, a = self.gecici("son"), self.gecici("adim")
            adim = self.ifade(d.adim) if d.adim else "1"
            self.yaz(f"{{ const {tip} {s} = {self.ifade(d.son)};")
            self.yaz(f"  {tip} {c} = {self.ifade(d.bas)};")
            self.yaz(f"  const {tip} {a} = ekin::adim_denetle(({tip})({adim}));")
            self.yaz(f"for (; {a} > 0 ? {c} <= {s} : {c} >= {s}; {c} += {a}) {{")
            ek_kapanis = True
        self.girinti += 1
        self.yaz(f"{v} = {c};")
        self.blok(d.govde)
        self.girinti -= 1
        self.yaz("}}" if ek_kapanis else "}")

    def _atama(self, d):
        h = d.hedef
        deger = self.ifade(d.deger)
        if isinstance(h, A.Ad):
            tur, tip = self._ara(h.ad)
            hedef = self.cad(h.ad)
            if d.islec == "=" and tur in ("yerel", "kuresel") and (tip == "harici" or str(tip).startswith("sınıf:")) \
                    and h.ad not in self.bildirilen:
                self.bildirilen.add(h.ad)
                self.yaz(f"auto {hedef} = {deger};")
                return
        else:
            hedef = self.ifade(h)
        op = d.islec
        sol_tip = h.tip if isinstance(h, A.Ad) else getattr(h, "tip", None)
        if op == "=":
            self.yaz(f"{hedef} = {deger};")
        elif op == "+=":
            if sol_tip == "metin" and d.deger.tip != "metin":
                deger = f"ekin::metne({deger})"
            if liste_mi(sol_tip):
                self.yaz(f"{hedef} = ekin::liste_birlestir({hedef}, {deger});")
            else:
                self.yaz(f"{hedef} += {deger};")
        elif op in ("-=", "*="):
            if op == "*=" and sol_tip == "metin":
                self.yaz(f"{hedef} = ekin::cogalt({hedef}, {deger});")
            else:
                self.yaz(f"{hedef} {op} {deger};")
        else:
            f = self._islev_sec(op[:-1], sol_tip, d.deger.tip)
            self.yaz(f"{hedef} = {f}({hedef}, {deger});")

    # ------------------------------------------------------------ ifade üretimi
    def ifade(self, e):
        t = type(e)
        if t is A.Sayi:
            v = e.deger
            if isinstance(v, float):
                s = repr(v)
                if "e" not in s and "." not in s and "inf" not in s:
                    s += ".0"
                return s
            if abs(v) > 2147483647:
                return f"{v}LL"
            return str(v) if v >= 0 else f"({v})"
        if t is A.Metin:
            return self._metin(e)
        if t is A.Mantik:
            return "true" if e.deger else "false"
        if t is A.Bos:
            return "nullptr"
        if t is A.Bu:
            return "(*this)"
        if t is A.Ad:
            return self._ad(e)
        if t is A.Liste:
            ot = oge_tipi(e.tip)
            if bilinmiyor_mu(ot):
                if not e.ogeler:
                    # tipin önemsiz olduğu yer (ör. boş_mu([])): herhangi bir tip yeter
                    return "ekin::Liste<ekin::tam>()"
                self.hata("Listenin öğe tipi bulunamadı. Tipini yazın, ör. x: liste[tam] = []", e)
            ct = self.ctip(ot, e)
            if not e.ogeler:
                return f"ekin::Liste<{ct}>()"
            return f"ekin::liste_yap<{ct}>({', '.join(self.ifade(x) for x in e.ogeler)})"
        if t is A.IkiliIslem:
            return self._ikili(e)
        if t is A.TekliIslem:
            v = self.ifade(e.deger)
            return f"(!{v})" if e.islec == "değil" else f"(-{v})"
        if t is A.Sira:
            n = self.ifade(e.nesne)
            s = self.ifade(e.sira)
            if e.nesne.tip == "metin":
                return f"ekin::harf({n}, {s})"
            if liste_mi(e.nesne.tip):
                return f"ekin::sira({n}, {s})"
            return f"{n}[{s}]"
        if t is A.Uye:
            n = self.ifade(e.nesne)
            coz = getattr(e, "cozum", "harici")
            if coz == "alan":
                return f"{n}.{self.cad(e.ad)}"
            if coz == "renk":
                return f"(ekin::tam){n}.{RENK_ALANLARI[e.ad]}"
            return f"{n}.{e.ad}"
        if t is A.Iyelik:
            return self.ifade(e.cozum)
        if t is A.Cagri:
            return self._cagri(e)
        if t is A.Lambda:
            return self._lambda(e)
        self.hata(f"Bu ifade derlenemiyor: {t.__name__}", e)

    @staticmethod
    def _cpp_metin(s):
        out = []
        for c in s:
            if c == "\\":
                out.append("\\\\")
            elif c == '"':
                out.append('\\"')
            elif c == "\n":
                out.append("\\n")
            elif c == "\t":
                out.append("\\t")
            elif c == "\r":
                out.append("\\r")
            elif c == "\0":
                out.append("\\0")
            elif c == "?":
                out.append("\\?")
            else:
                out.append(c)
        return '"' + "".join(out) + '"'

    def _metin(self, e):
        parcalar = []
        for p in e.parcalar:
            if p[0] == "yazi":
                if p[1] or len(e.parcalar) == 1:
                    parcalar.append(f"ekin::metin({self._cpp_metin(p[1])})")
            else:
                x = self.ifade(p[1])
                parcalar.append(x if p[1].tip == "metin" else f"ekin::metne({x})")
        if not parcalar:
            return 'ekin::metin("")'
        if len(parcalar) == 1:
            if e.parcalar[0][0] == "ifade" and e.parcalar[0][1].tip == "metin":
                return f"ekin::metin({parcalar[0]})"
            return parcalar[0]
        return "(" + " + ".join(parcalar) + ")"

    def _ad(self, e):
        coz = getattr(e, "cozum", None)
        if coz is None:
            self._ad_tip(e)
            coz = e.cozum
        if coz in ("yerel", "kuresel", "alan", "sabit", "fonk"):
            return self.cad(e.ad)
        if coz == "dis_sabit":
            return self.dis_sabitler[e.ad].sablon
        if coz == "modul_sabit":
            s = self.kayit.sabit(e.ad)
            sb = s.sablon(self.hedef)
            if sb is None:
                self.hata(f"'{e.ad}' {self.hedef} hedefinde kullanılamaz.", e)
            return sb
        if coz == "yerlesik":
            self.hata(f"'{e.ad}' yerleşik işlevi burada değer olarak kullanılamaz; "
                      f"bir lambda yazın: x -> {e.ad}(x)", e)
        return e.ad

    def _ikili(self, e):
        a, b = self.ifade(e.sol), self.ifade(e.sag)
        at, bt = e.sol.tip, e.sag.tip
        op = e.islec
        if op == "ve":
            return f"({a} && {b})"
        if op == "veya":
            return f"({a} || {b})"
        if op in ISLEC_CPP:
            if at == "metin" and isinstance(e.sag, A.Metin):
                pass
            return f"({a} {op} {b})"
        if op == "+":
            if e.tip == "metin":
                if at != "metin":
                    a = f"ekin::metne({a})"
                if bt != "metin":
                    b = f"ekin::metne({b})"
                return f"({a} + {b})"
            if liste_mi(e.tip):
                return f"ekin::liste_birlestir({a}, {b})"
            return f"({a} + {b})"
        if op == "*" and at == "metin":
            return f"ekin::cogalt({a}, {b})"
        if op in ("-", "*"):
            return f"({a} {op} {b})"
        return f"{self._islev_sec(op, at, bt)}({a}, {b})"

    @staticmethod
    def _islev_sec(op, at, bt):
        """Tipe göre çalışma zamanı işlevi: tam sayılarla tam, değilse ondalık sürüm."""
        tamlar = at == "tam" and bt == "tam"
        if op == "/":
            return "ekin::bol"
        if op == "//":
            return "ekin::tam_bol" if tamlar else "ekin::taban_bol"
        if op == "%":
            return "ekin::mod_tam" if tamlar else "ekin::mod_ond"
        if op == "**":
            return "ekin::us_tam" if tamlar else "ekin::us_ond"
        raise ValueError(op)

    def _lambda(self, e):
        tipler = getattr(e, "param_tipleri", None) or ["?"] * len(e.parametreler)
        ps = []
        kapsam = {}
        for p, t in zip(e.parametreler, tipler):
            if bilinmiyor_mu(t) or t == "harici":
                if self.hedef == "arduino":
                    self.hata("Lambda parametresinin tipi bulunamadı.", e)
                ps.append(f"auto {self.cad(p)}")
            else:
                ct = self.ctip(t)
                ps.append(f"const {ct}& {self.cad(p)}" if t == "metin" or liste_mi(t) or t in self.yapilar
                          else f"{ct} {self.cad(p)}")
            kapsam[p] = t
        self.kapsamlar.append(kapsam)
        try:
            govde = self.ifade(e.govde)
        finally:
            self.kapsamlar.pop()
        return f"[&]({', '.join(ps)}) {{ return {govde}; }}"

    def _cagri(self, e):
        coz = getattr(e, "cozum", None)
        if coz is None:
            self.hata("Çağrı çözümlenemedi.", e)
        tur = coz[0]
        if tur == "kullanici":
            f, args = coz[1], coz[2]
            return f"{self.cad(f.ad)}({', '.join(self._arg(x, f, k) for k, x in enumerate(args))})"
        if tur == "yontem":
            m, args, nesne = coz[1], coz[2], coz[3]
            a = ", ".join(self._arg(x, m, k) for k, x in enumerate(args))
            if nesne is None:
                return f"{self.cad(m.ad)}({a})"
            return f"{self.ifade(nesne)}.{self.cad(m.ad)}({a})"
        if tur == "yapi":
            y, args = coz[1], coz[2]
            return f"{self.cad(y.ad)}({', '.join(self.ifade(x) for x in args)})"
        if tur == "dis":
            d, args = coz[1], coz[2]
            a = [self.ifade(x) for x in args]
            if d.sablon is None:
                return f"{d.ad}({', '.join(a)})"
            return self._sablon_doldur(d.sablon, a, [x.tip for x in args])
        if tur == "yerlesik":
            yer, args, tipler = coz[1], coz[2], coz[3]
            for g in yer.gerekir:
                self.gerekenler.add(g)
            sb = yer.sablon(self.hedef)
            if sb is None:
                self.hata(f"'{yer.ad}' işlevi '{self.hedef}' hedefinde kullanılamaz.", e)
            a = [self.ifade(x) for x in args]
            return self._sablon_doldur(sb, a, tipler)
        if tur == "harici":
            return f"{coz[1]}({', '.join(self.ifade(x) for x in coz[2])})"
        if tur == "harici_uye":
            return f"{self.ifade(coz[1])}.{coz[2]}({', '.join(self.ifade(x) for x in coz[3])})"
        if tur == "ifade":
            return f"{self.ifade(coz[1])}({', '.join(self.ifade(x) for x in coz[2])})"
        self.hata("Çağrı çözümlenemedi.", e)

    def _arg(self, x, f, k):
        s = self.ifade(x)
        return s

    @staticmethod
    def _sablon_doldur(sb, args, tipler):
        if isinstance(sb, dict):
            sb = sb.get(len(args), sb.get("*"))
        if callable(sb):
            return sb(args, tipler)
        s = sb.replace("{*}", ", ".join(args))
        for k in range(len(args) - 1, -1, -1):
            s = s.replace("{%d}" % k, args[k])
        return s


def derle(program, kayit, hedef="pc", dosya=None, kutuphane_adi=None):
    d = Derleyici(program, kayit, hedef, dosya, kutuphane_adi)
    kod = d.derle()
    return kod, d.uyarilar
