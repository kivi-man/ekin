"""metin: Türkçe uyumlu metin işlemleri. Otomatik yüklenir.

büyüt/küçült Türkçe kurallara uyar: "istanbul" -> "İSTANBUL", "IŞIK" -> "ışık".
"""

from ekin.calisma import metne, tr_buyuk, tr_kucuk, hata, kopya
from ekin.modul import Islev, Modul


def _parcala(m, ayrac=None):
    if ayrac is None or ayrac == "":
        return m.split()
    return m.split(ayrac)


def _birlestir(liste, ayrac=""):
    return metne(ayrac).join(metne(x) for x in liste)


def _bul(aranan, kaynak):
    if isinstance(kaynak, str):
        return kaynak.find(aranan)
    try:
        return kaynak.index(aranan)
    except ValueError:
        return -1


def _icerir(kaynak, aranan):
    return aranan in kaynak


def _harf(m, i):
    if not 0 <= i < len(m):
        hata(f"Harf sırası {i} dışarıda (uzunluk {len(m)}).")
    return m[i]


def _alt_metin(m, bas, uzunluk=None):
    if uzunluk is None:
        return m[bas:]
    return m[bas:bas + uzunluk]


def _sayi_mi(m):
    try:
        float(m.strip())
        return m.strip() != ""
    except ValueError:
        return False


def _ters(x):
    return kopya(x[::-1])


def _say(kume, oge):
    return kume.count(oge)


MODUL = Modul(
    "metin",
    "Metin işlemleri (Türkçe büyük/küçük harf kurallarıyla).",
    otomatik=True,
    islevler=[
        Islev("büyüt(metin'i)", py=tr_buyuk, cpp="ekin::buyut({0})", donus="metin",
              aciklama="Büyük harfe çevirir (i -> İ).", ornek='"istanbul"\'u büyüt  ->  "İSTANBUL"'),
        Islev("küçült(metin'i)", py=tr_kucuk, cpp="ekin::kucult({0})", donus="metin",
              aciklama="Küçük harfe çevirir (I -> ı)."),
        Islev("kırp(metin'i)", py=str.strip, cpp="ekin::kirp({0})", donus="metin",
              aciklama="Baştaki ve sondaki boşlukları siler."),
        Islev("parçala(metin'i, ayraç'la?)", py=_parcala, cpp="ekin::parcala({*})", donus="liste[metin]",
              aciklama="Metni ayraca göre parçalar (ayraç yoksa boşluklara göre).",
              ornek='"a,b,c"\'yi ","\'le parçala  ->  ["a", "b", "c"]'),
        Islev("birleştir(liste'yi, ayraç'la?)", py=_birlestir, cpp="ekin::birlestir({*})", donus="metin",
              aciklama="Liste öğelerini aralarına ayraç koyarak birleştirir."),
        Islev("içerir(kaynak, aranan'ı)", py=_icerir, cpp="ekin::icerir({0}, {1})", donus="mantık",
              aciklama="Kaynak (metin ya da liste) arananı içeriyorsa doğru."),
        Islev("bul(aranan'ı, kaynak'ta)", py=_bul, cpp="ekin::bul({1}, {0})", donus="tam",
              aciklama="Arananın ilk konumu (yoksa -1). Metin ve listede çalışır.",
              ornek='"dünya"\'yı mesaj\'da bul'),
        Islev("değiştir(kaynak'ta, eski'yi, yeni'yle)", py=lambda k, e, y: k.replace(e, y),
              cpp="ekin::degistir({0}, {1}, {2})", donus="metin",
              aciklama="Metindeki tüm 'eski' parçaları 'yeni' yapar."),
        Islev("başlar(metin, önek'le)", py=lambda m, o: m.startswith(o), cpp="ekin::baslar({0}, {1})",
              donus="mantık", aciklama="Metin önekle başlıyorsa doğru."),
        Islev("biter(metin, sonek'le)", py=lambda m, s: m.endswith(s), cpp="ekin::biter({0}, {1})",
              donus="mantık", aciklama="Metin sonekle bitiyorsa doğru."),
        Islev("ters(x'i)", py=_ters, cpp="ekin::ters({0})", donus="$0",
              aciklama="Metni ya da listeyi ters çevirir."),
        Islev("harf(metin'in, sıra)", py=_harf, cpp="ekin::harf({0}, {1})", donus="metin",
              aciklama="Verilen sıradaki harf (0'dan başlar)."),
        Islev("alt_metin(metin'in, baş, uzunluk?)", py=_alt_metin, cpp="ekin::alt_metin({*})", donus="metin",
              aciklama="Metnin bir parçası."),
        Islev("sayı_mı(metin)", py=_sayi_mi, cpp="ekin::sayi_mi({0})", donus="mantık",
              aciklama="Metin bir sayıysa doğru."),
        Islev("karakter_kodu(harf'in)", py=lambda m: ord(m[0]) if m else 0, cpp="ekin::karakter_kodu({0})",
              donus="tam", aciklama="İlk harfin Unicode kodu."),
        Islev("koddan_karakter(kod)", py=chr, cpp="ekin::koddan_karakter({0})", donus="metin",
              aciklama="Unicode kodundan harf."),
        Islev("çoğalt(metin'i, kez)", py=lambda m, n: m * n, cpp="ekin::cogalt({0}, {1})", donus="metin",
              aciklama="Metni n kez yan yana yazar."),
        Islev("harfler(metin'in)", py=list, cpp="ekin::harfler({0})", donus="liste[metin]",
              aciklama="Metnin harflerinden oluşan liste."),
        Islev("satırlar(metin'in)", py=lambda m: m.splitlines(), cpp="ekin::satirlar({0})", donus="liste[metin]",
              aciklama="Metni satırlara böler."),
        Islev("say(küme'de, öğe'yi)", py=_say, cpp="ekin::say({0}, {1})", donus="tam",
              aciklama="Öğenin (metin ya da liste içinde) kaç kez geçtiği.", ornek="sayılar'da 3'ü say"),
    ],
)
