"""Örnek kullanıcı modülü: sıcaklık dönüşümleri.

Bu dosya, onu kullanan .ekin dosyasının yanındaki `moduller/` klasöründedir;
Ekin onu `kullan sicaklik` (ya da `kullan sıcaklık`) ile bulur.

Her komut üç yerde tanımlanır:
  py   -> yorumlayıcı (Python)
  cpp  -> derleyici, PC
  ino  -> derleyici, Arduino (verilmezse cpp kullanılır)

C++ tarafı bu klasördeki sicaklik.hpp dosyasındadır; derleyici onu otomatik bulur
(Arduino taslağına da kopyalar).
"""

from ekin.modul import Islev, Sabit, Modul

MODUL = Modul(
    "sicaklik",
    "Sıcaklık birimi dönüşümleri (örnek kullanıcı modülü).",
    basliklar={"pc": ['"sicaklik.hpp"'], "arduino": ['"sicaklik.hpp"']},
    islevler=[
        Islev("fahrenhayta(santigrat'ı)", py=lambda c: c * 9 / 5 + 32,
              cpp="sicaklik::fahrenhayta({0})", donus="ondalık",
              aciklama="Santigratı Fahrenhayta çevirir.", ornek="100'ü fahrenhayta"),
        Islev("santigrata(fahrenhayt'ı)", py=lambda f: (f - 32) * 5 / 9,
              cpp="sicaklik::santigrata({0})", donus="ondalık",
              aciklama="Fahrenhaytı santigrata çevirir."),
        Islev("hissedilen(sıcaklık, rüzgar'la)", py=lambda t, v: t - 0.7 * v ** 0.5,
              cpp="sicaklik::hissedilen({0}, {1})", donus="ondalık",
              aciklama="Basit bir hissedilen sıcaklık tahmini."),
    ],
    sabitler=[
        Sabit("MUTLAK_SIFIR", -273.15, "sicaklik::MUTLAK_SIFIR", tip="ondalık", aciklama="Kelvin 0"),
    ],
)
