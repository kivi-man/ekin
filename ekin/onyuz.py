"""Önyüz: kaynak dosyayı ve `kullan "x.ekin"` ile alınan dosyaları yükler."""

import os
import re

from . import agac as A
from .ayristirici import Ayristirici
from .hatalar import EkinHatasi
from .modul import Kayit
from .sozcukler import SozcukAyirici

_DOSYA_KULLAN = re.compile(r'^\s*kullan\s+"([^"]+\.ekin)"', re.M)


class Kaynak:
    """Yüklenen tüm dosyaların metinleri (hata iletisinde satırı göstermek için)."""

    def __init__(self):
        self.metinler = {}

    def metin(self, dosya):
        return self.metinler.get(dosya)


def dosya_oku(yol):
    with open(yol, encoding="utf-8-sig") as f:
        return f.read()


def program_yukle(yol, kayit=None, kaynak=None):
    """Bir .ekin dosyasını, aldığı dosyalarla birlikte tek programa çevirir."""
    yol = os.path.abspath(yol)
    if kayit is None:
        kayit = Kayit([os.path.join(os.path.dirname(yol), "moduller")])
    kaynak = kaynak or Kaynak()
    islevler = set()
    govde = []
    _yukle(yol, kayit, kaynak, islevler, govde, set())
    return A.Program(govde, satir=1), kayit, kaynak


def _yukle(yol, kayit, kaynak, islevler, govde, yuklenen):
    if yol in yuklenen:
        return
    yuklenen.add(yol)
    try:
        metin = dosya_oku(yol)
    except OSError as e:
        raise EkinHatasi(f"Dosya okunamadı: {yol} ({e.strerror})")
    kaynak.metinler[os.path.basename(yol)] = metin
    # önce bu dosyanın aldığı dosyalar
    for alt in _DOSYA_KULLAN.findall(metin):
        alt_yol = os.path.join(os.path.dirname(yol), alt)
        _yukle(os.path.abspath(alt_yol), kayit, kaynak, islevler, govde, yuklenen)
    program = kaynak_ayristir(metin, kayit, os.path.basename(yol), islevler)
    govde.extend(program.govde)


def kaynak_ayristir(metin, kayit, dosya=None, on_islevler=None):
    jetonlar = SozcukAyirici(metin, dosya).ayir()
    ay = Ayristirici(jetonlar, kayit, dosya)
    if on_islevler:
        ay.islev_adlari |= on_islevler
        ay.tanimli |= on_islevler
    program = ay.program()
    if on_islevler is not None:
        on_islevler |= ay.islev_adlari
    return program
