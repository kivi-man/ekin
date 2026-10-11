"""İnşa: üretilen C++ kodunu PC için derler ya da Arduino taslağına (sketch) çevirir."""

import os
import platform
import re
import shlex
import shutil
import subprocess

from .ekler import ascii_yap
from .hatalar import EkinHatasi

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALISMA_ZAMANI = os.path.join(KOK, "calisma_zamani")


def platform_adi():
    s = platform.system().lower()
    return {"darwin": "macos"}.get(s, s)


def guvenli_ad(ad):
    a = re.sub(r"[^A-Za-z0-9_]", "_", ascii_yap(ad))
    if not a or not a[0].isalpha():
        a = "p_" + a
    return a


def calisma_zamanini_kopyala(hedef_klasor, dosyalar=None):
    os.makedirs(hedef_klasor, exist_ok=True)
    for f in os.listdir(CALISMA_ZAMANI):
        if f.endswith(".hpp") and (dosyalar is None or f in dosyalar):
            shutil.copy2(os.path.join(CALISMA_ZAMANI, f), os.path.join(hedef_klasor, f))


# ------------------------------------------------------------------ PC
def cpp_derleyici_bul():
    ortam = os.environ.get("EKIN_CXX") or os.environ.get("CXX")
    if ortam:
        return shlex.split(ortam, posix=os.name != "nt")
    for ad in ("g++", "clang++", "c++"):
        yol = shutil.which(ad)
        if yol:
            return [yol]
    if os.name == "nt":
        if shutil.which("cl"):
            return ["cl"]
        if msvc_ortami() is not None:
            return ["cl"]
    return None


_MSVC_ORTAMI = []


def _vcvars_bul():
    """Kurulu Visual Studio'nun vcvars64.bat dosyasını bulur."""
    adaylar = []
    vswhere = os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                           "Microsoft Visual Studio", "Installer", "vswhere.exe")
    if os.path.isfile(vswhere):
        try:
            c = subprocess.run([vswhere, "-latest", "-products", "*", "-requires",
                                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property",
                                "installationPath"], capture_output=True, text=True)
            adaylar += [s.strip() for s in c.stdout.splitlines() if s.strip()]
        except OSError:
            pass
    for kok in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
        for surum in ("2022", "2019"):
            for tur in ("Community", "Professional", "Enterprise", "BuildTools"):
                adaylar.append(os.path.join(kok, "Microsoft Visual Studio", surum, tur))
    for a in adaylar:
        bat = os.path.join(a, "VC", "Auxiliary", "Build", "vcvars64.bat")
        if os.path.isfile(bat):
            return bat
    return None


def msvc_ortami():
    """Visual Studio C++ ortam değişkenlerini (INCLUDE, LIB, PATH) bir kez hazırlar."""
    if _MSVC_ORTAMI:
        return _MSVC_ORTAMI[0]
    ortam = None
    bat = _vcvars_bul() if os.name == "nt" else None
    if bat:
        try:
            c = subprocess.run(f'cmd /s /c ""{bat}" >nul 2>nul && set"', capture_output=True, text=True,
                               shell=False, errors="replace")
            ortam = dict(os.environ)
            for satir in c.stdout.splitlines():
                if "=" in satir:
                    k, v = satir.split("=", 1)
                    ortam[k] = v
            if not shutil.which("cl", path=ortam.get("PATH") or ortam.get("Path")):
                ortam = None
        except OSError:
            ortam = None
    _MSVC_ORTAMI.append(ortam)
    return ortam


def raylib_yolu():
    """RAYLIB_YOL ortam değişkeni; yoksa Windows'ta standart C:\\raylib klasörü."""
    yol = os.environ.get("RAYLIB_YOL")
    if yol:
        return yol
    if os.name == "nt" and os.path.isfile(r"C:\raylib\include\raylib.h"):
        return r"C:\raylib"
    return None


def _raylib_bayraklari(moduller, plat):
    """grafik/opengl modülleri için ek derleme ve bağlama bayrakları."""
    ekler, bagla = [], []
    gerekli = False
    for m in moduller:
        f = m.baglama.get("pc")
        if f:
            gerekli = True
            bagla += f(plat) if callable(f) else list(f)
    if not gerekli:
        return [], [], False
    yol = raylib_yolu()
    if yol:
        ekler += ["-I" + os.path.join(yol, "include")]
        bagla = ["-L" + os.path.join(yol, "lib")] + bagla
    elif plat in ("linux", "macos") and shutil.which("pkg-config"):
        try:
            c = subprocess.run(["pkg-config", "--cflags", "--libs", "raylib"], capture_output=True, text=True)
            if c.returncode == 0 and c.stdout.strip():
                bayrak = c.stdout.split()
                ekler += [b for b in bayrak if b.startswith("-I")]
                bagla = [b for b in bayrak if not b.startswith("-I")] + [b for b in bagla if b != "-lraylib"]
        except OSError:
            pass
    elif plat == "macos" and os.path.isdir("/opt/homebrew/include"):
        ekler += ["-I/opt/homebrew/include"]
        bagla = ["-L/opt/homebrew/lib"] + bagla
    return ekler, bagla, True


def pc_derle(cpp_yolu, cikti, moduller, optimizasyon="-O2", ayrintili=False):
    cxx = cpp_derleyici_bul()
    if cxx is None:
        raise EkinHatasi(
            "C++ derleyicisi bulunamadı. C++ kodu üretildi: " + cpp_yolu + "\n"
            "  Windows: https://github.com/skeeto/w64devkit (ya da MSYS2: pacman -S mingw-w64-ucrt-x86_64-gcc)\n"
            "  macOS:   xcode-select --install\n"
            "  Linux:   sudo apt install g++\n"
            "  Ya da EKIN_CXX ortam değişkeniyle derleyiciyi belirtin.")
    plat = platform_adi()
    ekler, bagla, grafik = _raylib_bayraklari(moduller, plat)
    for m in moduller:
        if m.klasor and os.path.abspath(m.klasor) != os.path.join(KOK, "moduller"):
            ekler = ["-I" + m.klasor] + ekler
    kaynak_klasoru = os.path.dirname(os.path.abspath(cpp_yolu))
    calistirma_ortami = None
    if os.path.basename(cxx[0]).lower() in ("cl", "cl.exe"):
        if not shutil.which("cl"):
            calistirma_ortami = msvc_ortami()
        nesne_klasoru = os.path.join(os.path.dirname(os.path.abspath(cikti)), "")
        komut = cxx + ["/nologo", "/std:c++17", "/EHsc", "/utf-8", "/O2", "/W3", "/D_CRT_SECURE_NO_WARNINGS",
                       "/I", CALISMA_ZAMANI, "/I", kaynak_klasoru] + \
            [e.replace("-I", "/I", 1) for e in ekler]
        if grafik:
            # raylib'in hazır MSVC paketi dinamik C çalışma zamanıyla (/MD) derlenmiştir
            komut.append("/MD")
        komut += [cpp_yolu, "/Fe:" + cikti, "/Fo:" + nesne_klasoru]
        if grafik:
            komut += ["/link", "raylib.lib", "opengl32.lib", "gdi32.lib", "winmm.lib", "user32.lib", "shell32.lib"]
            if raylib_yolu():
                komut.append("/LIBPATH:" + os.path.join(raylib_yolu(), "lib"))
    else:
        komut = cxx + ["-std=c++17", optimizasyon, "-I", CALISMA_ZAMANI, "-I", kaynak_klasoru] + ekler + \
            [cpp_yolu, "-o", cikti] + bagla
        if plat == "windows" and not grafik:
            komut.append("-static")
    if ayrintili:
        print("  $ " + " ".join(shlex.quote(k) for k in komut), flush=True)
    if calistirma_ortami is not None:
        # cl, PATH'te olmayabilir: hazırlanan ortamın PATH'inden tam yolunu bul
        komut[0] = shutil.which("cl", path=calistirma_ortami.get("PATH") or calistirma_ortami.get("Path")) or "cl"
    sonuc = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=calistirma_ortami)
    if sonuc.returncode != 0:
        ileti = (sonuc.stderr or sonuc.stdout).strip()
        bulunamadi = ("raylib.h" in ileti and ("C1083" in ileti or "No such file" in ileti)) or \
            ("raylib.lib" in ileti and "LNK1104" in ileti) or "cannot find -lraylib" in ileti
        if grafik and bulunamadi:
            ileti += ("\n\nraylib bulunamadı. Kurulum:\n"
                      "  Windows: https://github.com/raysan5/raylib/releases paketini (MSVC için *_win64_msvc16, "
                      "g++ için *_win64_mingw-w64) C:\\raylib klasörüne açın (include\\ ve lib\\ orada olmalı)\n"
                      "           ya da RAYLIB_YOL ortam değişkeniyle başka bir klasör gösterin\n"
                      "  macOS:   brew install raylib\n"
                      "  Linux:   sudo apt install libraylib-dev  (ya da kaynaktan derleyin)")
        raise EkinHatasi("C++ derlemesi başarısız oldu:\n" + ileti)
    return cikti


# ------------------------------------------------------------------ Arduino
ARDUINO_CLI_YOLLARI = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"),
    r"C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe",
    "/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli",
    os.path.expanduser("~/.local/bin/arduino-cli"),
    "/usr/local/bin/arduino-cli",
]


def arduino_cli_bul():
    ortam = os.environ.get("EKIN_ARDUINO_CLI")
    if ortam and os.path.isfile(ortam):
        return ortam
    yol = shutil.which("arduino-cli")
    if yol:
        return yol
    for y in ARDUINO_CLI_YOLLARI:
        if y and os.path.isfile(y):
            return y
    return None


def arduino_taslagi(cpp_kodu, klasor, ad, moduller=()):
    """Arduino taslak klasörü oluşturur: <ad>/<ad>.ino + ekin_program.cpp + başlıklar.

    Kod .cpp dosyasına konur; böylece Arduino'nun .ino ön işlemcisinin otomatik
    ürettiği bildirimler (prototipler) yapılarla çakışmaz.
    """
    ad = guvenli_ad(ad)
    taslak = os.path.join(klasor, ad)
    os.makedirs(taslak, exist_ok=True)
    with open(os.path.join(taslak, ad + ".ino"), "w", encoding="utf-8") as f:
        f.write("// Bu taslak Ekin ile üretildi.\n"
                "// Program kodu: ekin_program.cpp (setup ve loop orada tanımlıdır).\n")
        for b in re.findall(r"^#include\s+(<[^>]+>)", cpp_kodu, re.M):
            if b != "<Arduino.h>":
                f.write(f"#include {b}\n")
    with open(os.path.join(taslak, "ekin_program.cpp"), "w", encoding="utf-8") as f:
        f.write(cpp_kodu)
    calisma_zamanini_kopyala(taslak, {"ekin.hpp", "ekin_servo.hpp"})
    for m in moduller:
        for b in m.basliklar.get("arduino", []):
            if b.startswith('"') and m.klasor:
                kaynak = os.path.join(m.klasor, b.strip('"'))
                if os.path.isfile(kaynak):
                    shutil.copy2(kaynak, os.path.join(taslak, os.path.basename(kaynak)))
    return taslak


def arduino_derle(taslak, kart="arduino:avr:uno", port=None, yukle=False):
    cli = arduino_cli_bul()
    if cli is None:
        raise EkinHatasi(
            "arduino-cli bulunamadı. Taslak hazır: " + taslak + "\n"
            "  Arduino IDE ile açıp yükleyebilir ya da arduino-cli kurabilirsiniz:\n"
            "  https://arduino.github.io/arduino-cli/latest/installation/")
    komut = [cli, "compile", "--fqbn", kart, taslak]
    for k in os.environ.get("EKIN_ARDUINO_KUTUPHANE", "").split(os.pathsep):
        if k:
            komut += ["--library", k]
    if yukle:
        if not port:
            raise EkinHatasi("Yüklemek için port gerekli: --port COM3 (Windows) ya da --port /dev/ttyACM0")
        komut += ["--upload", "-p", port]
    print("  $ " + " ".join(shlex.quote(k) for k in komut))
    sonuc = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8", errors="replace")
    cikti = (sonuc.stdout + "\n" + sonuc.stderr).strip()
    if sonuc.returncode != 0:
        eksik = re.findall(r"fatal error: ([\w\-/]+)\.h: No such file", cikti)
        if eksik:
            ad = eksik[0].split("/")[-1]
            cikti += (f"\n\n'{ad}' kütüphanesi kurulu değil. Kurmak için:\n"
                      f"  arduino-cli lib install \"{ad}\"\n"
                      f"  (ya da Arduino IDE > Kütüphane Yöneticisi'nde '{ad}' aratın)")
        raise EkinHatasi("Arduino derlemesi başarısız oldu:\n" + cikti)
    return cikti


def arduino_portlari():
    cli = arduino_cli_bul()
    if cli is None:
        raise EkinHatasi("arduino-cli bulunamadı.")
    return subprocess.run([cli, "board", "list"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout
