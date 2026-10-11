"""Ekin test paketi.

    python -m unittest discover testler          (proje klasöründe)

* Ek çözümleme, sözcük ayırma, yorumlayıcı çıktıları, hata iletileri
* C++ üretimi (PC ve Arduino hedefleri)
* Bir C++ derleyicisi varsa (g++/clang++ ya da EKIN_CXX): derlenmiş programın
  çıktısı yorumlayıcınınkiyle karşılaştırılır
* EKIN_ARDUINO_TEST=1 ve arduino-cli varsa: Arduino örnekleri Uno için derlenir
"""

import os
import subprocess
import sys
import tempfile
import unittest

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

from ekin.ekler import kok_bul, iyelik_coz, ek_coz, tr_buyuk, tr_kucuk, ek_oner  # noqa: E402
from ekin.sozcukler import ayir  # noqa: E402
from ekin.hatalar import EkinHatasi  # noqa: E402
from ekin.insa import cpp_derleyici_bul, arduino_cli_bul  # noqa: E402

BEKLENEN = os.path.join(KOK, "testler", "beklenen")

# (dosya, ek komut satırı seçenekleri)
ORNEKLER = [
    ("ornekler/01_merhaba.ekin", []),
    ("ornekler/02_temeller.ekin", []),
    ("ornekler/03_ekler.ekin", []),
    ("ornekler/kendi_modulum/hava_durumu.ekin", []),
    ("testler/ornekler/zor_durumlar.ekin", []),
    ("ornekler/arduino/01_led_yanip_sonme.ekin", ["--tur", "2", "--hızlı"]),
    ("ornekler/arduino/02_dugme_ve_kesme.ekin", ["--tur", "2", "--hızlı"]),
    ("ornekler/arduino/03_isik_sensoru.ekin", ["--tur", "3", "--hızlı"]),
]
PC_ORNEKLERI = [o for o, _ in ORNEKLER if "arduino" not in o]
ARDUINO_ORNEKLERI = [o for o, _ in ORNEKLER if "arduino" in o] + [
    "ornekler/arduino/04_servo_ve_ses.ekin", "ornekler/arduino/05_cpp_kutuphanesi.ekin"]
GRAFIK_ORNEKLERI = ["ornekler/grafik/01_tuval.ekin", "ornekler/grafik/02_ziplayan_toplar.ekin",
                    "ornekler/grafik/03_yilan_oyunu.ekin", "ornekler/grafik/04_opengl_kupler.ekin",
                    "ornekler/grafik/05_opengl_ozellikleri.ekin"]


def ekin(*args, girdi=None):
    ortam = dict(os.environ, PYTHONIOENCODING="utf-8")
    s = subprocess.run([sys.executable, os.path.join(KOK, "ekin.py"), *args], cwd=KOK,
                       capture_output=True, text=True, encoding="utf-8", input=girdi, env=ortam)
    return s.returncode, s.stdout.replace("\r\n", "\n"), s.stderr.replace("\r\n", "\n")


def beklenen_yolu(ornek):
    return os.path.join(BEKLENEN, os.path.basename(ornek).replace(".ekin", ".txt"))


class EkTestleri(unittest.TestCase):
    def test_kesmeli_ekler(self):
        self.assertEqual(ek_coz("yi"), ("i", False))
        self.assertEqual(ek_coz("ü"), ("i", False))
        self.assertEqual(ek_coz("ye"), ("e", False))
        self.assertEqual(ek_coz("ten"), ("den", False))
        self.assertEqual(ek_coz("deki"), ("de", False))
        self.assertEqual(ek_coz("nın"), ("in", False))
        self.assertEqual(ek_coz("yla"), ("le", False))
        self.assertEqual(ek_coz("sinin"), ("in", True))
        self.assertIsNone(ek_coz("ler"))

    def test_kok_bulma(self):
        bilinen = {"liste", "sayaç", "renk", "kitap", "pin", "meyveler", "ton"}
        self.assertEqual(kok_bul("listeyi", bilinen), ("liste", "i"))
        self.assertEqual(kok_bul("listeye", bilinen), ("liste", "e"))
        self.assertEqual(kok_bul("sayacı", bilinen), ("sayaç", "i"))      # ç -> c
        self.assertEqual(kok_bul("rengi", bilinen), ("renk", "i"))        # k -> g
        self.assertEqual(kok_bul("kitabın", bilinen), ("kitap", "in"))    # p -> b
        self.assertEqual(kok_bul("pine", bilinen), ("pin", "e"))
        self.assertEqual(kok_bul("meyvelerden", bilinen), ("meyveler", "den"))
        # ünlü uyumu bozuksa ek sayılmaz: tone (C++ adı) != ton + e
        self.assertIsNone(kok_bul("tone", bilinen))

    def test_iyelik(self):
        bilinen = {"uzunluk", "toplam", "harfler", "en_büyük"}
        self.assertEqual(iyelik_coz("uzunluğu", bilinen), ("uzunluk", None))
        self.assertEqual(iyelik_coz("uzunluğunu", bilinen), ("uzunluk", "i"))
        self.assertEqual(iyelik_coz("toplamı", bilinen), ("toplam", None))
        self.assertEqual(iyelik_coz("harflerinin", bilinen), ("harfler", "in"))
        self.assertEqual(iyelik_coz("en_büyüğü", bilinen), ("en_büyük", None))

    def test_turkce_harf_donusumu(self):
        self.assertEqual(tr_buyuk("istanbul ılık"), "İSTANBUL ILIK")
        self.assertEqual(tr_kucuk("İSTANBUL ILIK"), "istanbul ılık")

    def test_ek_onerisi(self):
        self.assertEqual(ek_oner("liste", "e"), "ye")
        self.assertEqual(ek_oner("kitap", "den"), "tan")
        self.assertEqual(ek_oner("göz", "i"), "ü")


class SozcukTestleri(unittest.TestCase):
    def test_ekli_jetonlar(self):
        j = ayir("5'i liste'ye ekle\n")
        self.assertEqual((j[0].deger, j[0].ek), (5, "i"))
        self.assertEqual((j[1].deger, j[1].ek), ("liste", "e"))
        self.assertEqual(j[2].deger, "ekle")

    def test_girinti(self):
        turler = [t.tur for t in ayir("eğer x:\n    yaz x\nyaz y\n")]
        self.assertIn("GIRINTI", turler)
        self.assertIn("CIKINTI", turler)

    def test_ascii_anahtar_sozcukler(self):
        j = ayir("eger dogru:\n    don\n")
        self.assertEqual((j[0].tur, j[0].deger), ("ANAHTAR", "eğer"))
        self.assertEqual(j[1].deger, "doğru")

    def test_kivrik_kesme(self):
        j = ayir("13’ü yak\n")
        self.assertEqual((j[0].deger, j[0].ek), (13, "i"))


class YorumlayiciTestleri(unittest.TestCase):
    def test_ornek_ciktilari(self):
        for ornek, secenek in ORNEKLER:
            with self.subTest(ornek=ornek):
                rc, out, err = ekin("çalıştır", ornek, *secenek)
                self.assertEqual(rc, 0, err)
                with open(beklenen_yolu(ornek), encoding="utf-8") as f:
                    self.assertEqual(out, f.read())

    def test_hata_iletileri(self):
        durumlar = [
            ("13'ü yak\n", "kullan arduino"),
            ("yaz y\n", "'y' tanımlı değil"),
            ("eğer 1 > 0\n    yaz 1\n", "':' bekleniyordu"),
            ("x = 5\nx = \"a\"\n", "tek bir tipte"),
            ("l = [1]\nyaz l[3]\n", "dışarıda"),
            ("yaz \"açık\n", "kapatılmamış"),
            ("yaz 1 / 0\n", "Sıfıra bölme"),
            ("x = 5\nyaz x'ler\n", "eki tanınmadı"),
        ]
        with tempfile.TemporaryDirectory() as k:
            for kod, beklenen in durumlar:
                with self.subTest(kod=kod):
                    yol = os.path.join(k, "h.ekin")
                    with open(yol, "w", encoding="utf-8") as f:
                        f.write(kod)
                    rc, out, err = ekin("çalıştır", yol)
                    self.assertNotEqual(rc, 0)
                    self.assertIn(beklenen, err)

    def test_etkilesimli(self):
        rc, out, _ = ekin("etkileşimli", girdi="x = 6\nx * 7\n\"ışık\"'ı büyüt\nçık\n")
        self.assertIn("42", out)
        self.assertIn('"IŞIK"', out)


class DerleyiciTestleri(unittest.TestCase):
    def test_cpp_uretimi(self):
        for ornek in PC_ORNEKLERI + GRAFIK_ORNEKLERI:
            with self.subTest(ornek=ornek):
                rc, out, err = ekin("cpp", ornek)
                self.assertEqual(rc, 0, err)
                self.assertIn('#include "ekin.hpp"', out)
        for ornek in ARDUINO_ORNEKLERI:
            with self.subTest(ornek=ornek):
                rc, out, err = ekin("cpp", ornek, "--hedef", "arduino")
                self.assertEqual(rc, 0, err)
                self.assertIn("void setup()", out)

    def test_kutuphane(self):
        with tempfile.TemporaryDirectory() as k:
            rc, out, err = ekin("kütüphane", "ornekler/kutuphane/geometri.ekin", "-o", k)
            self.assertEqual(rc, 0, err)
            with open(os.path.join(k, "geometri.hpp"), encoding="utf-8") as f:
                kod = f.read()
            self.assertIn("namespace geometri", kod)
            self.assertIn("inline ekin::ondalik uzaklik(", kod)

    @unittest.skipUnless(cpp_derleyici_bul(), "C++ derleyicisi yok")
    def test_grafik_sozdizimi(self):
        """Grafik/OpenGL çıktısı raylib API'sine (testler/sahte) göre sözdizimi denetiminden geçer."""
        from ekin.insa import msvc_ortami, CALISMA_ZAMANI
        import shutil
        cxx = cpp_derleyici_bul()
        msvc = os.path.basename(cxx[0]).lower() in ("cl", "cl.exe")
        sahte = os.path.join(KOK, "testler", "sahte")
        for ornek in GRAFIK_ORNEKLERI:
            with self.subTest(ornek=ornek):
                rc, kod, err = ekin("cpp", ornek)
                self.assertEqual(rc, 0, err)
                with tempfile.TemporaryDirectory() as k:
                    cpp = os.path.join(k, "g.cpp")
                    with open(cpp, "w", encoding="utf-8") as f:
                        f.write(kod)
                    if msvc:
                        ortam = None if shutil.which("cl") else msvc_ortami()
                        cl = shutil.which("cl", path=(ortam or os.environ).get("PATH")) or "cl"
                        komut = [cl, "/nologo", "/std:c++17", "/EHsc", "/utf-8", "/Zs", "/I", CALISMA_ZAMANI,
                                 "/I", sahte, cpp]
                    else:
                        ortam = None
                        komut = cxx + ["-std=c++17", "-fsyntax-only", "-I", CALISMA_ZAMANI, "-I", sahte, cpp]
                    s = subprocess.run(komut, capture_output=True, text=True, errors="replace", env=ortam)
                    self.assertEqual(s.returncode, 0, s.stdout + s.stderr)

    @unittest.skipUnless(cpp_derleyici_bul(), "C++ derleyicisi yok")
    def test_derlenmis_cikti_ayni(self):
        for ornek in PC_ORNEKLERI:
            with self.subTest(ornek=ornek):
                with tempfile.TemporaryDirectory() as k:
                    cikti = os.path.join(k, "p.exe" if os.name == "nt" else "p")
                    rc, _, err = ekin("derle", ornek, "-o", cikti)
                    self.assertEqual(rc, 0, err)
                    s = subprocess.run([cikti], capture_output=True, text=True, encoding="utf-8")
                    with open(beklenen_yolu(ornek), encoding="utf-8") as f:
                        self.assertEqual(s.stdout.replace("\r\n", "\n"), f.read())


@unittest.skipUnless(os.environ.get("EKIN_GRAFIK_TEST") and cpp_derleyici_bul(),
                     "EKIN_GRAFIK_TEST=1, kurulu raylib ve C++ derleyicisi gerekli (pencere açar)")
class RaylibTestleri(unittest.TestCase):
    def test_gercek_pencere(self):
        """Grafik örnekleri gerçek raylib/OpenGL ile derlenir, birkaç kare çizer ve görüntü kaydeder."""
        for ornek in GRAFIK_ORNEKLERI:
            with self.subTest(ornek=ornek):
                with tempfile.TemporaryDirectory() as k:
                    cikti = os.path.join(k, "p.exe" if os.name == "nt" else "p")
                    rc, _, err = ekin("derle", ornek, "-o", cikti)
                    self.assertEqual(rc, 0, err)
                    resim = os.path.join(k, "kare.png")
                    s = subprocess.run([cikti], capture_output=True, text=True, errors="replace", timeout=60,
                                       env=dict(os.environ, EKIN_KARE="5", EKIN_GORUNTU=resim))
                    self.assertEqual(s.returncode, 0, s.stdout + s.stderr)
                    self.assertTrue(os.path.isfile(resim), "görüntü kaydedilmedi")
                    try:
                        from PIL import Image
                    except ImportError:
                        continue
                    with Image.open(resim) as im:
                        renkler = im.convert("RGB").getcolors(maxcolors=1 << 20)
                    self.assertGreater(len(renkler), 2, "pencere boş çizilmiş")


@unittest.skipUnless(os.environ.get("EKIN_ARDUINO_TEST") and arduino_cli_bul(),
                     "EKIN_ARDUINO_TEST=1 ve arduino-cli gerekli")
class ArduinoTestleri(unittest.TestCase):
    def test_uno_derlemesi(self):
        for ornek in ARDUINO_ORNEKLERI[:3]:
            with self.subTest(ornek=ornek):
                rc, out, err = ekin("arduino", ornek)
                self.assertEqual(rc, 0, err)
                self.assertIn("Derleme başarılı", out)


if __name__ == "__main__":
    unittest.main()
