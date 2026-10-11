"""zaman: bekleme ve saat işlevleri. Otomatik yüklenir."""

import time

from ekin.calisma import SECENEKLER
from ekin.modul import Islev, Modul

_BASLANGIC = time.perf_counter()


def _bekle(ms):
    if not SECENEKLER.get("hizli"):
        time.sleep(max(0, ms) / 1000.0)


def _yerel():
    return time.localtime()


MODUL = Modul(
    "zaman",
    "Bekleme, süre ölçme, saat ve tarih.",
    otomatik=True,
    islevler=[
        Islev("bekle(süre'yi)", py=_bekle, cpp="ekin::bekle({0})", ino="delay({0})",
              aciklama="Milisaniye cinsinden bekler.", ornek="500 bekle  |  bekle 1000"),
        Islev("saniye_bekle(süre'yi)", py=lambda s: _bekle(s * 1000), cpp="ekin::bekle((ekin::tam)(({0}) * 1000))",
              ino="delay((unsigned long)(({0}) * 1000))", aciklama="Saniye cinsinden bekler."),
        Islev("mikro_bekle(süre'yi)", py=lambda us: _bekle(us / 1000.0), cpp="ekin::mikro_bekle({0})",
              ino="delayMicroseconds({0})", aciklama="Mikrosaniye cinsinden bekler."),
        Islev("milisaniye()", py=lambda: int((time.perf_counter() - _BASLANGIC) * 1000),
              cpp="ekin::milisaniye()", ino="(ekin::tam)millis()", donus="tam",
              aciklama="Program başladığından beri geçen milisaniye."),
        Islev("mikrosaniye()", py=lambda: int((time.perf_counter() - _BASLANGIC) * 1_000_000),
              cpp="ekin::mikrosaniye()", ino="(ekin::tam)micros()", donus="tam",
              aciklama="Program başladığından beri geçen mikrosaniye."),
        Islev("zaman_damgası()", py=lambda: int(time.time()), cpp="ekin::zaman_damgasi()", ino=False,
              donus="tam", aciklama="1970'ten beri geçen saniye (yalnız PC)."),
        Islev("saat()", py=lambda: _yerel().tm_hour, cpp="ekin::saat_al(0)", ino=False, donus="tam",
              aciklama="Şu anki saat (0-23)."),
        Islev("dakika()", py=lambda: _yerel().tm_min, cpp="ekin::saat_al(1)", ino=False, donus="tam",
              aciklama="Şu anki dakika."),
        Islev("saniye()", py=lambda: _yerel().tm_sec, cpp="ekin::saat_al(2)", ino=False, donus="tam",
              aciklama="Şu anki saniye."),
        Islev("gün()", py=lambda: _yerel().tm_mday, cpp="ekin::saat_al(3)", ino=False, donus="tam",
              aciklama="Ayın günü."),
        Islev("ay()", py=lambda: _yerel().tm_mon, cpp="ekin::saat_al(4)", ino=False, donus="tam",
              aciklama="Ay (1-12)."),
        Islev("yıl()", py=lambda: _yerel().tm_year, cpp="ekin::saat_al(5)", ino=False, donus="tam",
              aciklama="Yıl."),
        Islev("tarih()", py=lambda: time.strftime("%d.%m.%Y"), cpp="ekin::tarih_metni()", ino=False,
              donus="metin", aciklama="Bugünün tarihi: GG.AA.YYYY"),
        Islev("saat_metni()", py=lambda: time.strftime("%H:%M:%S"), cpp="ekin::saat_metni()", ino=False,
              donus="metin", aciklama="Şu anki saat: SS:DD:ss"),
    ],
)
