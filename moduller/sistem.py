"""sistem: işletim sistemi ile ilgili işlevler (yalnız PC). Kullanım: kullan sistem"""

import os
import platform as _platform
import subprocess
import sys

from ekin.modul import Islev, Modul


def _platform_adi():
    s = _platform.system().lower()
    return {"darwin": "macos"}.get(s, s)


MODUL = Modul(
    "sistem",
    "Komut çalıştırma, ortam değişkenleri, program argümanları (yalnız PC).",
    hedefler=("py", "pc"),
    basliklar={"pc": ['"ekin_dosya.hpp"']},
    islevler=[
        Islev("komut(komut'u)", py=lambda k: subprocess.call(k, shell=True), cpp="ekin::sistem::komut({0})",
              donus="tam", aciklama="İşletim sistemi komutunu çalıştırır, çıkış kodunu verir."),
        Islev("ortam_değişkeni(ad)", py=lambda a: os.environ.get(a, ""), cpp="ekin::sistem::ortam({0})",
              donus="metin", aciklama="Ortam değişkeninin değeri."),
        Islev("argümanlar()", py=lambda: sys.argv[2:] if len(sys.argv) > 2 else [],
              cpp="ekin::sistem::argumanlar()", donus="liste[metin]",
              aciklama="Programa verilen komut satırı argümanları."),
        Islev("platform()", py=_platform_adi, cpp="ekin::sistem::platform()", donus="metin",
              aciklama='"windows", "linux" ya da "macos".'),
    ],
)
