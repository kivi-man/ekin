"""Sözdizim ağacı (AST) düğümleri."""


class Dugum:
    alanlar = ()

    def __init__(self, *args, satir=0, **kw):
        for ad, d in zip(self.alanlar, args):
            setattr(self, ad, d)
        for ad in self.alanlar[len(args):]:
            setattr(self, ad, kw.pop(ad, None))
        for ad, d in kw.items():
            setattr(self, ad, d)
        self.satir = satir

    def __repr__(self):
        ic = ", ".join(f"{a}={getattr(self, a)!r}" for a in self.alanlar)
        return f"{type(self).__name__}({ic})"


class Ifade(Dugum):
    """İfade düğümü. `ek`: hal eki rolü (i, e, de, den, in, le) ya da None."""

    def __init__(self, *args, **kw):
        ek = kw.pop("ek", None)
        super().__init__(*args, **kw)
        self.ek = ek
        self.tip = None


# ---------------------------------------------------------------- ifadeler
class Sayi(Ifade):
    alanlar = ("deger",)


class Metin(Ifade):
    alanlar = ("parcalar",)   # [("yazi", str) | ("ifade", Ifade)]


class Mantik(Ifade):
    alanlar = ("deger",)


class Bos(Ifade):
    alanlar = ()


class Bu(Ifade):
    alanlar = ()


class Ad(Ifade):
    alanlar = ("ad",)


class Liste(Ifade):
    alanlar = ("ogeler",)


class Sira(Ifade):          # a[i]
    alanlar = ("nesne", "sira")


class Uye(Ifade):           # a.b
    alanlar = ("nesne", "ad")


class Iyelik(Ifade):        # liste'nin uzunluğu
    alanlar = ("nesne", "ad")


class Cagri(Ifade):         # f(a, b) ; argumanlar: [(Ifade, rol)]
    alanlar = ("islev", "argumanlar")


class IkiliIslem(Ifade):
    alanlar = ("sol", "islec", "sag")


class TekliIslem(Ifade):
    alanlar = ("islec", "deger")


class Lambda(Ifade):        # x -> x * 2
    alanlar = ("parametreler", "govde")


# ---------------------------------------------------------------- deyimler
class Program(Dugum):
    alanlar = ("govde",)


class Atama(Dugum):         # x = 5 / x += 1 / x: tam = 5
    alanlar = ("hedef", "islec", "deger", "tip_adi")


class SabitTanim(Dugum):
    alanlar = ("ad", "deger", "tip_adi")


class Eger(Dugum):
    alanlar = ("dallar", "degilse")   # dallar: [(kosul, govde)]


class Iken(Dugum):
    alanlar = ("kosul", "govde")


class Surekli(Dugum):
    alanlar = ("govde",)


class AralikDongu(Dugum):   # için i 1'den 10'a: (uçlar dahil)
    alanlar = ("degisken", "bas", "son", "adim", "govde")


class HerDongu(Dugum):      # her x liste'de:
    alanlar = ("degisken", "kume", "govde")


class Tekrarla(Dugum):      # 5 kez tekrarla:
    alanlar = ("sayi", "govde")


class Don(Dugum):
    alanlar = ("deger",)


class Kir(Dugum):
    alanlar = ()


class Devam(Dugum):
    alanlar = ()


class IfadeDeyimi(Dugum):
    alanlar = ("ifade",)


class HamCpp(Dugum):
    alanlar = ("kod",)


class Parametre(Dugum):
    alanlar = ("ad", "rol", "tip_adi", "varsayilan")


class IslevTanim(Dugum):
    # tur: "normal", "kurulum", "döngü", "her_karede", "yöntem"
    alanlar = ("ad", "parametreler", "donus_tipi", "govde", "tur")


class YapiTanim(Dugum):
    alanlar = ("ad", "alanlar_", "yontemler")   # alanlar_: [(ad, tip_adi, varsayilan)]


class Kullan(Dugum):
    # tur: "modul" | "dosya" | "baslik"
    alanlar = ("tur", "ad")


class DisIslev(Dugum):      # dış işlev f(a, b) -> tip = "şablon"
    alanlar = ("ad", "parametreler", "donus_tipi", "sablon")


class DisSabit(Dugum):      # dış sabit AD -> tip = "İFADE"
    alanlar = ("ad", "tip_adi", "sablon")
