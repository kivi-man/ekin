"""liste: liste işlemleri. Otomatik yüklenir."""

import random

from ekin.calisma import hata, kopya
from ekin.modul import Islev, Modul
from ekin.tipler import oge_tipi


def _ekle(oge, liste):
    liste.append(kopya(oge))


def _cikar(oge, liste):
    if oge in liste:
        liste.remove(oge)
        return True
    return False


def _sil(liste, sira):
    if not 0 <= sira < len(liste):
        hata(f"Silinecek sıra {sira} dışarıda (uzunluk {len(liste)}).")
    return liste.pop(sira)


def _araya(liste, sira, oge):
    liste.insert(max(0, min(sira, len(liste))), kopya(oge))


def _karistir(l):
    k = kopya(l)
    random.shuffle(k)
    return k


def _ortalama(l):
    if not l:
        hata("Boş listenin ortalaması alınamaz.")
    return sum(l) / len(l)


def _dilim(l, bas, son):
    return kopya(l[max(0, bas):son + 1])


def _ilk(l):
    if not l:
        hata("Boş listenin ilk öğesi yok.")
    return l[0]


def _son(l):
    if not l:
        hata("Boş listenin son öğesi yok.")
    return l[-1]


def _esle_tip(tipler, lambda_donus):
    return f"liste[{lambda_donus.get(1, '?')}]"


MODUL = Modul(
    "liste",
    "Liste işlemleri.",
    otomatik=True,
    islevler=[
        Islev("ekle(öğe'yi, liste'ye)", py=_ekle, cpp="ekin::ekle({1}, {0})", daralt={1: "liste[$0]"},
              aciklama="Listenin sonuna öğe ekler.", ornek="5'i sayılar'a ekle"),
        Islev("çıkar(öğe'yi, liste'den)", py=_cikar, cpp="ekin::cikar({1}, {0})", donus="mantık",
              aciklama="Öğenin ilk geçtiği yeri listeden çıkarır.", ornek="5'i sayılar'dan çıkar"),
        Islev("sil(liste'den, sıra'yı)", py=_sil, cpp="ekin::sil({0}, {1})", donus="$0[]",
              aciklama="Verilen sıradaki öğeyi siler ve döndürür.", ornek="sayılar'dan 0'ı sil"),
        Islev("araya_ekle(liste'ye, sıra, öğe'yi)", py=_araya, cpp="ekin::araya_ekle({0}, {1}, {2})",
              aciklama="Öğeyi verilen sıraya yerleştirir."),
        Islev("içinde(öğe'yi, liste'de)", py=lambda o, l: o in l, cpp="ekin::icerir({1}, {0})", donus="mantık",
              aciklama="Öğe listede varsa doğru.", ornek="eğer içinde(3, sayılar): ..."),
        Islev("sırala(liste'yi)", py=lambda l: kopya(sorted(l)), cpp="ekin::sirala({0})", donus="$0", takma=["sıralı"],
              aciklama="Küçükten büyüğe sıralanmış yeni liste."),
        Islev("ters_sırala(liste'yi)", py=lambda l: kopya(sorted(l, reverse=True)), cpp="ekin::ters_sirala({0})",
              donus="$0", aciklama="Büyükten küçüğe sıralanmış yeni liste."),
        Islev("karıştır(liste'yi)", py=_karistir, cpp="ekin::karistir({0})", donus="$0",
              aciklama="Karıştırılmış yeni liste."),
        Islev("topla(liste'yi)", py=sum, cpp="ekin::topla({0})", donus="$0[]", takma=["toplam"],
              aciklama="Liste öğelerinin toplamı.", ornek="sayılar'ı topla"),
        Islev("çarp(liste'yi)", py=lambda l: __import__("math").prod(l), cpp="ekin::carp({0})", donus="$0[]", takma=["çarpım"],
              aciklama="Liste öğelerinin çarpımı."),
        Islev("ortalama(liste'nin)", py=_ortalama, cpp="ekin::ortalama({0})", donus="ondalık",
              aciklama="Ortalama.", ornek="notlar'ın ortalaması"),
        Islev("temizle(liste'yi)", py=lambda l: l.clear(), cpp="ekin::temizle({0})",
              aciklama="Listeyi boşaltır."),
        Islev("dilim(liste'den, baş, son)", py=_dilim, cpp="ekin::dilim({0}, {1}, {2})", donus="$0",
              aciklama="baş ile son (ikisi dahil) arasındaki öğeler."),
        Islev("süz(liste'yi, koşul'la)", py=lambda l, f: [kopya(x) for x in l if f(x)], cpp="ekin::suz({0}, {1})",
              donus="$0", lambda_param={1: "$0[]"},
              aciklama="Koşulu sağlayan öğelerden yeni liste.", ornek="çiftler = süz(sayılar, x -> x % 2 == 0)"),
        Islev("eşle(liste'yi, işlev'le)", py=lambda l, f: [f(x) for x in l], cpp="ekin::esle({0}, {1})",
              donus=_esle_tip, lambda_param={1: "$0[]"},
              aciklama="Her öğeye işlevi uygular.", ornek="kareler = eşle(sayılar, x -> x * x)"),
        Islev("hepsi(liste'nin, koşul'la)", py=lambda l, f: all(f(x) for x in l), cpp="ekin::hepsi({0}, {1})",
              donus="mantık", lambda_param={1: "$0[]"}, aciklama="Tüm öğeler koşulu sağlıyorsa doğru."),
        Islev("biri(liste'nin, koşul'la)", py=lambda l, f: any(f(x) for x in l), cpp="ekin::biri({0}, {1})",
              donus="mantık", lambda_param={1: "$0[]"}, aciklama="En az bir öğe koşulu sağlıyorsa doğru."),
        Islev("ilk(liste'nin)", py=_ilk, cpp="ekin::ilk({0})", donus="$0[]", aciklama="İlk öğe."),
        Islev("son(liste'nin)", py=_son, cpp="ekin::son({0})", donus="$0[]", aciklama="Son öğe."),
        Islev("doldur(adet, değer'le)", py=lambda n, v: [kopya(v) for _ in range(n)], cpp="ekin::doldur({0}, {1})",
              donus=lambda t: f"liste[{t[1] if len(t) > 1 else '?'}]",
              aciklama="Aynı değerden n tane içeren liste.", ornek="doldur(5, 0)  ->  [0, 0, 0, 0, 0]"),
        Islev("kopya(x'in)", py=kopya, cpp="({0})", donus="$0",
              aciklama="Listenin kopyası."),
    ],
)
