"""grafik: pencere, 2B tuval çizimi, fare ve klavye. Kullanım: kullan grafik

Yorumlayıcı: tkinter (kurulum gerekmez).
Derlenmiş sürüm: raylib (OpenGL) - Windows, macOS, Linux.

Örnek:
    kullan grafik
    pencere_aç 640, 480, "Top"
    x = 0
    her_karede:
        arkaplan SİYAH
        daire x, 240, 30, KIRMIZI
        x += 3
"""

import random

from ekin.calisma import Renk
from ekin.modul import Islev, Sabit, Modul
from ekin.tuval_tk import TUVAL


def _renk(r, g, b, a=255):
    return Renk(r, g, b, a)


def _pencere_ac(gen, yuk, baslik="Ekin"):
    TUVAL.ac(gen, yuk, baslik)


def _bitis(yorum):
    if TUVAL.kok is None:
        return
    TUVAL.calistir(yorum.ozel.get("her_karede"))


def _baglama(platform):
    if platform == "windows":
        return ["-lraylib", "-lopengl32", "-lgdi32", "-lwinmm"]
    if platform == "macos":
        return ["-lraylib", "-framework", "OpenGL", "-framework", "Cocoa", "-framework", "IOKit",
                "-framework", "CoreVideo"]
    return ["-lraylib", "-lGL", "-lm", "-lpthread", "-ldl", "-lrt", "-lX11"]


RENKLER = {
    "SİYAH": (0, 0, 0), "BEYAZ": (255, 255, 255), "KIRMIZI": (230, 41, 55), "YEŞİL": (0, 200, 80),
    "MAVİ": (0, 121, 241), "SARI": (253, 249, 0), "TURUNCU": (255, 161, 0), "MOR": (150, 60, 200),
    "PEMBE": (255, 109, 194), "KAHVERENGİ": (127, 106, 79), "GRİ": (130, 130, 130),
    "AÇIK_GRİ": (200, 200, 200), "KOYU_GRİ": (60, 60, 60), "LACİVERT": (20, 30, 90),
    "TURKUAZ": (0, 190, 190), "ALTIN": (255, 203, 0), "GÖK_MAVİSİ": (102, 191, 255),
    "KOYU_YEŞİL": (0, 117, 44), "BORDO": (128, 0, 32),
}

TUSLAR = {
    "TUŞ_SOL": 263, "TUŞ_SAĞ": 262, "TUŞ_YUKARI": 265, "TUŞ_AŞAĞI": 264, "TUŞ_BOŞLUK": 32,
    "TUŞ_ENTER": 257, "TUŞ_ESC": 256, "TUŞ_SİL": 259, "TUŞ_TAB": 258, "TUŞ_SHIFT": 340,
    "TUŞ_CTRL": 341,
}
TUSLAR.update({f"TUŞ_{c}": ord(c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"})


def _renk_cpp(rgb):
    return "ekin::Renk{%d, %d, %d, 255}" % rgb


G = "ekin::grafik::"

MODUL = Modul(
    "grafik",
    "Pencere, 2B tuval çizimi, fare ve klavye (raylib/OpenGL ile derlenir).",
    hedefler=("py", "pc"),
    basliklar={"pc": ['"ekin_grafik.hpp"']},
    baglama={"pc": _baglama},
    py_bitis=_bitis,
    kare_dongusu={"pc": G + "calistir({0});"},
    islevler=[
        Islev("pencere_aç(genişlik, yükseklik, başlık?)", py=_pencere_ac, cpp=G + "pencere_ac({*})",
              aciklama="Çizim penceresi açar.", ornek='pencere_aç 800, 600, "Oyunum"'),
        Islev("pencere_kapat()", py=TUVAL.kapat, cpp=G + "pencere_kapat()", aciklama="Pencereyi kapatır."),
        Islev("arkaplan(renk'i)", py=TUVAL.arkaplan, cpp=G + "arkaplan({0})",
              aciklama="Tuvali bir renkle temizler.", ornek="arkaplan SİYAH"),
        Islev("renk(kırmızı, yeşil, mavi, saydamlık?)", py=_renk, cpp="ekin::renk({*})", donus="renk",
              aciklama="0-255 değerlerinden renk.", ornek="turuncu = renk(255, 128, 0)"),
        Islev("rastgele_renk()", py=lambda: Renk(random.randint(40, 255), random.randint(40, 255),
                                                 random.randint(40, 255)),
              cpp="ekin::rastgele_renk()", donus="renk", aciklama="Rastgele parlak bir renk."),
        Islev("renk_seç(renk'i)", py=lambda r: setattr(TUVAL, "renk", r), cpp=G + "renk_sec({0})",
              aciklama="Renk verilmeyen çizimlerin rengini seçer."),
        Islev("kalınlık(k)", py=lambda k: setattr(TUVAL, "kalinlik", k), cpp=G + "kalinlik({0})",
              aciklama="Çizgi ve çerçeve kalınlığı."),
        Islev("daire(x, y, yarıçap, renk?)", py=TUVAL.daire, cpp=G + "daire({*})",
              aciklama="Dolu daire.", ornek="daire 100, 100, 40, KIRMIZI"),
        Islev("daire_çerçeve(x, y, yarıçap, renk?)", py=lambda x, y, r, c=None: TUVAL.daire(x, y, r, c, False),
              cpp=G + "daire_cerceve({*})", aciklama="İçi boş daire."),
        Islev("elips(x, y, yatay_yarıçap, dikey_yarıçap, renk?)", py=TUVAL.elips, cpp=G + "elips({*})",
              aciklama="Dolu elips."),
        Islev("dikdörtgen(x, y, genişlik, yükseklik, renk?)", py=TUVAL.dikdortgen, cpp=G + "dikdortgen({*})",
              aciklama="Dolu dikdörtgen (x, y sol üst köşe).", ornek="dikdörtgen 10, 10, 200, 50, MAVİ"),
        Islev("dikdörtgen_çerçeve(x, y, genişlik, yükseklik, renk?)",
              py=lambda x, y, g, h, c=None: TUVAL.dikdortgen(x, y, g, h, c, False),
              cpp=G + "dikdortgen_cerceve({*})", aciklama="İçi boş dikdörtgen."),
        Islev("çizgi(x1, y1, x2, y2, renk?)", py=TUVAL.cizgi, cpp=G + "cizgi({*})", aciklama="Çizgi."),
        Islev("üçgen(x1, y1, x2, y2, x3, y3, renk?)", py=TUVAL.ucgen, cpp=G + "ucgen({*})",
              aciklama="Dolu üçgen."),
        Islev("nokta(x, y, renk?)", py=TUVAL.nokta, cpp=G + "nokta({*})", aciklama="Tek piksel."),
        Islev("yazı(metin'i, x, y, boyut?, renk?)", py=TUVAL.yazi, cpp=G + "yazi({*})",
              aciklama="Tuvale yazı yazar (Türkçe harfler desteklenir).", ornek='yazı "Puan: {puan}", 10, 10, 24, BEYAZ'),
        Islev("yazı_genişliği(metin'in, boyut?)", py=TUVAL.yazi_genisligi, cpp=G + "yazi_genisligi({*})",
              donus="tam", aciklama="Yazının piksel genişliği."),
        Islev("kare_hızı(fps)", py=lambda f: setattr(TUVAL, "fps", max(1, int(f))), cpp=G + "kare_hizi({0})",
              aciklama="Saniyedeki kare sayısı (varsayılan 60)."),
        Islev("fare_x()", py=lambda: TUVAL.fare[0], cpp=G + "fare_x()", donus="tam", aciklama="Fare x konumu."),
        Islev("fare_y()", py=lambda: TUVAL.fare[1], cpp=G + "fare_y()", donus="tam", aciklama="Fare y konumu."),
        Islev("fare_basılı()", py=lambda: TUVAL.fare_basili, cpp=G + "fare_basili()", donus="mantık",
              aciklama="Sol fare tuşu basılı tutuluyorsa doğru."),
        Islev("fare_tıklandı()", py=lambda: TUVAL.fare_tik, cpp=G + "fare_tiklandi()", donus="mantık",
              aciklama="Bu karede tıklandıysa doğru."),
        Islev("tuş_basılı(tuş)", py=lambda k: k in TUVAL.basili, cpp=G + "tus_basili({0})", donus="mantık",
              aciklama="Tuş basılı tutuluyorsa doğru.", ornek="eğer tuş_basılı(TUŞ_SOL): x -= 5"),
        Islev("tuşa_basıldı(tuş)", py=lambda k: k in TUVAL.basildi, cpp=G + "tusa_basildi({0})", donus="mantık",
              aciklama="Tuşa bu karede basıldıysa doğru."),
        Islev("genişlik()", py=lambda: TUVAL.gen, cpp=G + "genislik()", donus="tam", aciklama="Pencere genişliği."),
        Islev("yükseklik()", py=lambda: TUVAL.yuk, cpp=G + "yukseklik()", donus="tam", aciklama="Pencere yüksekliği."),
        Islev("geçen_süre()", py=lambda: TUVAL.gecen, cpp=G + "gecen_sure()", donus="ondalık",
              aciklama="Önceki kareden beri geçen saniye."),
        Islev("kare_sayısı()", py=lambda: TUVAL.kare_no, cpp=G + "kare_sayisi()", donus="tam",
              aciklama="Şimdiye kadar çizilen kare sayısı."),
    ],
    sabitler=[Sabit(ad, Renk(*rgb), _renk_cpp(rgb), tip="renk", aciklama="Renk") for ad, rgb in RENKLER.items()]
    + [Sabit("SAYDAM", Renk(0, 0, 0, 0), "ekin::Renk{0, 0, 0, 0}", tip="renk")]
    + [Sabit(ad, kod, str(kod), tip="tam", aciklama="Tuş kodu") for ad, kod in TUSLAR.items()],
)
