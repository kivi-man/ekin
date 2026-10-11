"""matematik: sayısal işlevler. Otomatik yüklenir."""

import math
import random

from ekin.calisma import hata
from ekin.modul import Islev, Sabit, Modul
from ekin.tipler import liste_mi, oge_tipi


def _sayi_tipi(tipler):
    return "tam" if all(t == "tam" for t in tipler) else "ondalık"


def _yuvarla(x, basamak=0):
    if basamak == 0:
        # C'deki round gibi: yarımlar sıfırdan uzağa
        return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))
    k = 10 ** basamak
    return (math.floor(x * k + 0.5) if x >= 0 else -math.floor(-x * k + 0.5)) / k


def _yuvarla_tip(tipler):
    return "tam" if len(tipler) < 2 else "ondalık"


def _en(f):
    def islev(*a):
        if len(a) == 1 and isinstance(a[0], list):
            if not a[0]:
                hata("Boş listenin en büyük/küçük öğesi yok.")
            return f(a[0])
        return f(a)
    return islev


def _en_tip(tipler):
    if len(tipler) == 1 and liste_mi(tipler[0]):
        return oge_tipi(tipler[0])
    return _sayi_tipi(tipler)


def _en_cpp(ad):
    def sablon(args, tipler):
        if len(args) == 1 and liste_mi(tipler[0]):
            return f"ekin::{ad}_liste({args[0]})"
        if all(t == "tam" for t in tipler):
            return f"ekin::{ad}<ekin::tam>({', '.join(args)})"
        return f"ekin::{ad}<ekin::ondalik>({', '.join(args)})"
    return sablon


def _olcekle(x, a1, b1, a2, b2):
    if all(isinstance(v, int) for v in (x, a1, b1, a2, b2)):
        return int((x - a1) * (b2 - a2) / (b1 - a1)) + a2
    return (x - a1) * (b2 - a2) / (b1 - a1) + a2


def _olcekle_cpp(args, tipler):
    if all(t == "tam" for t in tipler):
        return f"ekin::olcekle_tam({', '.join(args)})"
    return f"ekin::olcekle({', '.join(args)})"


def _sinirla(x, a, b):
    return max(a, min(b, x))


def _asal(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def _isaret(x):
    return (x > 0) - (x < 0)


def _ebob(a, b):
    return math.gcd(int(a), int(b))


def _ekok(a, b):
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def _faktoriyel(n):
    return math.factorial(int(n))


def _rastgele(a, b):
    return random.randint(min(a, b), max(a, b))


def _sayi_cpp(f):
    """Tam sayılar için tam, ondalıklar için ondalık sürümü seçer."""
    def sablon(args, tipler):
        return f(args, _sayi_tipi(tipler))
    return sablon


MODUL = Modul(
    "matematik",
    "Sayısal işlevler ve sabitler.",
    otomatik=True,
    islevler=[
        Islev("karekök(x'in)", py=math.sqrt, cpp="sqrt((double)({0}))", donus="ondalık",
              aciklama="Karekök.", ornek="karekök(16)  |  16'nın karekökü"),
        Islev("mutlak(x'in)", py=abs, cpp="ekin::mutlak({0})", donus=lambda t: _sayi_tipi(t),
              aciklama="Mutlak değer."),
        Islev("üs(taban, üs)", py=lambda a, b: a ** b if isinstance(a, int) and isinstance(b, int) and b >= 0 else float(a) ** b,
              cpp=_sayi_cpp(lambda a, t: f"ekin::us_{'tam' if t == 'tam' else 'ond'}({a[0]}, {a[1]})"),
              donus=lambda t: _sayi_tipi(t),
              aciklama="Üs alma (a ** b ile aynı)."),
        Islev("yuvarla(x'i, basamak?)", py=_yuvarla, cpp="ekin::yuvarla({*})", donus=_yuvarla_tip,
              aciklama="En yakın tam sayıya (ya da basamağa) yuvarlar."),
        Islev("taban(x'in)", py=lambda x: math.floor(x), cpp="(ekin::tam)floor((double)({0}))", donus="tam",
              aciklama="Aşağı yuvarlar."),
        Islev("tavan(x'in)", py=lambda x: math.ceil(x), cpp="(ekin::tam)ceil((double)({0}))", donus="tam",
              aciklama="Yukarı yuvarlar."),
        Islev("sin(x)", py=math.sin, cpp="sin((double)({0}))", donus="ondalık", aciklama="Sinüs (radyan)."),
        Islev("cos(x)", py=math.cos, cpp="cos((double)({0}))", donus="ondalık", aciklama="Kosinüs (radyan)."),
        Islev("tan(x)", py=math.tan, cpp="tan((double)({0}))", donus="ondalık", aciklama="Tanjant (radyan)."),
        Islev("asin(x)", py=math.asin, cpp="asin((double)({0}))", donus="ondalık", aciklama="Ters sinüs."),
        Islev("acos(x)", py=math.acos, cpp="acos((double)({0}))", donus="ondalık", aciklama="Ters kosinüs."),
        Islev("atan(x)", py=math.atan, cpp="atan((double)({0}))", donus="ondalık", aciklama="Ters tanjant."),
        Islev("atan2(y, x)", py=math.atan2, cpp="atan2((double)({0}), (double)({1}))", donus="ondalık",
              aciklama="İki bağımsız değişkenli ters tanjant."),
        Islev("log(x)", py=math.log, cpp="log((double)({0}))", donus="ondalık", aciklama="Doğal logaritma."),
        Islev("log10(x)", py=math.log10, cpp="log10((double)({0}))", donus="ondalık", aciklama="10 tabanında logaritma."),
        Islev("üstel(x)", py=math.exp, cpp="exp((double)({0}))", donus="ondalık", aciklama="e üzeri x."),
        Islev("derece(radyan)", py=math.degrees, cpp="((double)({0}) * 57.29577951308232)", donus="ondalık",
              aciklama="Radyanı dereceye çevirir."),
        Islev("radyan(derece)", py=math.radians, cpp="((double)({0}) * 0.017453292519943295)", donus="ondalık",
              aciklama="Dereceyi radyana çevirir."),
        Islev("hipotenüs(a, b)", py=math.hypot, cpp="sqrt((double)({0})*({0}) + (double)({1})*({1}))",
              donus="ondalık", aciklama="Dik üçgenin hipotenüsü."),
        Islev("en_büyük(değerler...)", py=_en(max), cpp=_en_cpp("en_buyuk"), donus=_en_tip,
              aciklama="En büyük değer (sayılar ya da bir liste).", ornek="en_büyük(3, 9, 4)  |  sayılar'ın en_büyüğü"),
        Islev("en_küçük(değerler...)", py=_en(min), cpp=_en_cpp("en_kucuk"), donus=_en_tip,
              aciklama="En küçük değer."),
        Islev("sınırla(x'i, alt, üst)", py=_sinirla,
              cpp=_sayi_cpp(lambda a, t: f"ekin::sinirla<ekin::{'tam' if t == 'tam' else 'ondalik'}>({', '.join(a)})"),
              donus=lambda t: _sayi_tipi(t), aciklama="x'i alt ile üst arasında tutar."),
        Islev("ölçekle(x'i, eski_alt, eski_üst, yeni_alt, yeni_üst)", py=_olcekle, cpp=_olcekle_cpp,
              donus=lambda t: _sayi_tipi(t), aciklama="Bir aralıktaki değeri başka aralığa taşır (Arduino map).",
              ornek="ölçekle(analog_oku(A0), 0, 1023, 0, 255)"),
        Islev("rastgele(alt, üst)", py=_rastgele, cpp="ekin::rastgele({0}, {1})", donus="tam",
              aciklama="alt ile üst arasında (ikisi dahil) rastgele tam sayı."),
        Islev("rastgele_ondalık()", py=random.random, cpp="ekin::rastgele_ondalik()", donus="ondalık",
              aciklama="0 ile 1 arasında rastgele ondalık sayı."),
        Islev("rastgele_tohum(tohum)", py=random.seed, cpp="ekin::rastgele_tohum({0})",
              aciklama="Rastgele sayı üretecini başlatır."),
        Islev("işaret(x'in)", py=_isaret, cpp="ekin::isaret({0})", donus="tam", aciklama="-1, 0 ya da 1."),
        Islev("çift_mi(x)", py=lambda x: x % 2 == 0, cpp="(ekin::mod_tam({0}, 2) == 0)", donus="mantık",
              aciklama="Sayı çiftse doğru."),
        Islev("tek_mi(x)", py=lambda x: x % 2 == 1, cpp="(ekin::mod_tam({0}, 2) == 1)", donus="mantık",
              aciklama="Sayı tekse doğru."),
        Islev("asal_mı(x)", py=_asal, cpp="ekin::asal_mi({0})", donus="mantık", aciklama="Sayı asalsa doğru."),
        Islev("faktöriyel(n'in)", py=_faktoriyel, cpp="ekin::faktoriyel({0})", donus="tam", aciklama="n!"),
        Islev("ebob(a, b)", py=_ebob, cpp="ekin::ebob({0}, {1})", donus="tam", aciklama="En büyük ortak bölen."),
        Islev("ekok(a, b)", py=_ekok, cpp="ekin::ekok({0}, {1})", donus="tam", aciklama="En küçük ortak kat."),
    ],
    sabitler=[
        Sabit("PI", math.pi, "ekin::pi_sayisi", tip="ondalık", aciklama="π = 3.14159..."),
        Sabit("TAU", math.tau, "(2 * ekin::pi_sayisi)", tip="ondalık", aciklama="2π"),
        Sabit("E", math.e, "ekin::e_sayisi", tip="ondalık", aciklama="e = 2.71828..."),
        Sabit("SONSUZ", math.inf, "ekin::sonsuz()", tip="ondalık", aciklama="Sonsuz."),
    ],
)
