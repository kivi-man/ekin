"""dosya: dosya okuma/yazma (yalnız PC). Kullanım: kullan dosya"""

import os

from ekin.calisma import metne
from ekin.modul import Islev, Modul


def _oku(yol):
    with open(yol, encoding="utf-8") as f:
        return f.read()


def _yaz(m, yol, kip="w"):
    with open(yol, kip, encoding="utf-8") as f:
        f.write(metne(m))


MODUL = Modul(
    "dosya",
    "Dosya okuma ve yazma (yalnız PC).",
    hedefler=("py", "pc"),
    basliklar={"pc": ['"ekin_dosya.hpp"']},
    islevler=[
        Islev("dosya_oku(yol'u)", py=_oku, cpp="ekin::dosya::oku({0})", donus="metin",
              aciklama="Dosyanın tamamını metin olarak okur.", ornek='içerik = dosya_oku "notlar.txt"'),
        Islev("satırları_oku(yol'u)", py=lambda y: _oku(y).splitlines(), cpp="ekin::dosya::satirlari_oku({0})",
              donus="liste[metin]", aciklama="Dosyayı satır listesi olarak okur."),
        Islev("dosyaya_yaz(metin'i, yol'a)", py=_yaz, cpp="ekin::dosya::yaz({1}, ekin::metne({0}), false)",
              aciklama="Metni dosyaya yazar (eskisinin üstüne).", ornek='"merhaba"\'yı "a.txt"\'ye dosyaya_yaz'),
        Islev("dosyaya_ekle(metin'i, yol'a)", py=lambda m, y: _yaz(m, y, "a"),
              cpp="ekin::dosya::yaz({1}, ekin::metne({0}), true)", aciklama="Metni dosyanın sonuna ekler."),
        Islev("dosya_var(yol)", py=os.path.isfile, cpp="ekin::dosya::var({0})", donus="mantık",
              aciklama="Dosya varsa doğru."),
        Islev("dosya_sil(yol'u)", py=os.remove, cpp="ekin::dosya::sil({0})", aciklama="Dosyayı siler."),
    ],
)
