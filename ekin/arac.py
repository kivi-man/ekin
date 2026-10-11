"""Komut satırı aracı: ekin <komut> [dosya] [seçenekler]"""

import argparse
import os
import subprocess
import sys

from . import SURUM
from .calisma import SECENEKLER
from .ekler import ascii_yap
from .hatalar import EkinHatasi
from .modul import Kayit
from .onyuz import program_yukle, Kaynak, kaynak_ayristir

KOMUTLAR = {
    "calistir": "calistir", "run": "calistir", "c": "calistir",
    "derle": "derle", "build": "derle", "d": "derle",
    "arduino": "arduino",
    "cpp": "cpp",
    "kutuphane": "kutuphane", "lib": "kutuphane",
    "etkilesimli": "etkilesimli", "repl": "etkilesimli",
    "moduller": "moduller", "modul": "moduller",
    "surum": "surum", "version": "surum",
    "yardim": "yardim", "help": "yardim",
}

YARDIM = f"""Ekin {SURUM} - Türkçe, ekli, derlenebilir ve yorumlanabilir programlama dili

Kullanım:  ekin <komut> [dosya.ekin] [seçenekler]

Komutlar:
  çalıştır  dosya.ekin            Yorumlayıcıyla çalıştırır (derleme gerekmez)
  derle     dosya.ekin            C++'a çevirip PC için derler
            --çalıştır             derledikten sonra çalıştırır
            -o program             çıktı dosyasının adı
  cpp       dosya.ekin            Üretilen C++ kodunu ekrana yazar
            --hedef arduino        Arduino için C++ kodu
  arduino   dosya.ekin            Arduino taslağı hazırlar ve derler
            --kart arduino:avr:uno kart (FQBN)
            --port COM3            port; --yükle ile karta yükler
            --portlar              bağlı kartları listeler
  kütüphane dosya.ekin            C++ başlık kütüphanesi (.hpp) üretir
  etkileşimli                     Komut komut deneme ortamı (REPL)
  modüller  [ad]                  Modülleri ve komutları listeler
  sürüm                           Sürümü yazar

Yorumlayıcı seçenekleri:
  --tur N      döngü: bloğunu en fazla N kez çalıştırır
  --kare N     her_karede: bloğunu N kare sonra durdurur
  --hızlı      bekle komutlarını atlar (benzetim/test için)
  --sessiz     Arduino benzetim iletilerini gizler

Örnek:   ekin çalıştır ornekler/01_merhaba.ekin
"""


def _hata_yaz(e, kaynak):
    metin = kaynak.metin(e.dosya) if (kaynak and e.dosya) else None
    print(e.bicimle(metin), file=sys.stderr)


def _ayristirici():
    p = argparse.ArgumentParser(prog="ekin", add_help=False)
    p.add_argument("komut", nargs="?")
    p.add_argument("dosya", nargs="?")
    p.add_argument("--hedef", default="pc")
    p.add_argument("-o", "--çıktı", "--cikti", dest="cikti")
    p.add_argument("--çalıştır", "--calistir", dest="calistir", action="store_true")
    p.add_argument("--kart", default="arduino:avr:uno")
    p.add_argument("--port")
    p.add_argument("--yükle", "--yukle", dest="yukle", action="store_true")
    p.add_argument("--portlar", action="store_true")
    p.add_argument("--tur", type=int)
    p.add_argument("--kare", type=int)
    p.add_argument("--hızlı", "--hizli", dest="hizli", action="store_true")
    p.add_argument("--sessiz", action="store_true")
    p.add_argument("--md", action="store_true")
    p.add_argument("--ayrıntılı", "--ayrintili", "-v", dest="ayrintili", action="store_true")
    p.add_argument("-h", "--help", "--yardım", "--yardim", dest="yardim", action="store_true")
    return p


def ana(argv=None):
    for akis in (sys.stdout, sys.stderr, sys.stdin):
        try:
            akis.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    argv = sys.argv[1:] if argv is None else argv
    args, kalan = _ayristirici().parse_known_args(argv)
    for k in kalan:
        print(f"Uyarı: tanınmayan seçenek yok sayıldı: {k}  "
              f"(Türkçe harf sorunu varsa ASCII yazın: --calistir, --yukle, --hizli)", file=sys.stderr)
    if args.yardim or not args.komut:
        print(YARDIM)
        return 0
    komut = KOMUTLAR.get(ascii_yap(args.komut).lower())
    if komut is None:
        if args.komut.endswith(".ekin"):
            args.dosya, komut = args.komut, "calistir"
        else:
            print(f"Bilinmeyen komut: {args.komut}\n", file=sys.stderr)
            print(YARDIM)
            return 2
    SECENEKLER["tur_siniri"] = args.tur
    SECENEKLER["kare_siniri"] = args.kare
    SECENEKLER["hizli"] = args.hizli
    SECENEKLER["sessiz_sim"] = args.sessiz
    try:
        if komut == "surum":
            print(f"Ekin {SURUM}")
            return 0
        if komut == "yardim":
            print(YARDIM)
            return 0
        if komut == "moduller":
            if args.md:
                return komut_belgesi(args.cikti or "KOMUTLAR.md")
            return moduller_komutu(args.dosya)
        if komut == "etkilesimli":
            return etkilesimli()
        if komut == "arduino" and args.portlar:
            from .insa import arduino_portlari
            print(arduino_portlari())
            return 0
        if not args.dosya:
            print("Bir .ekin dosyası belirtin. Örnek: ekin çalıştır merhaba.ekin", file=sys.stderr)
            return 2
        if komut == "calistir":
            return calistir(args.dosya)
        if komut == "cpp":
            return cpp_komutu(args.dosya, args.hedef)
        if komut == "derle":
            if args.hedef == "arduino":
                return arduino_komutu(args)
            return derle_komutu(args)
        if komut == "arduino":
            return arduino_komutu(args)
        if komut == "kutuphane":
            return kutuphane_komutu(args)
    except EkinHatasi as e:
        _hata_yaz(e, getattr(e, "_kaynak", None))
        return 1
    except KeyboardInterrupt:
        print("\n[durduruldu]", file=sys.stderr)
        return 130
    return 0


def _yukle(dosya):
    kaynak = Kaynak()
    try:
        program, kayit, kaynak = program_yukle(dosya, kaynak=kaynak)
    except EkinHatasi as e:
        e._kaynak = kaynak
        raise
    return program, kayit, kaynak


def calistir(dosya):
    from .yorumlayici import Yorumlayici
    program, kayit, kaynak = _yukle(dosya)
    try:
        Yorumlayici(kayit, os.path.basename(dosya)).calistir(program)
    except EkinHatasi as e:
        e._kaynak = kaynak
        raise
    except SystemExit as s:
        return s.code or 0
    return 0


def _cpp_uret(dosya, hedef, kutuphane_adi=None):
    from .derleyici import derle
    program, kayit, kaynak = _yukle(dosya)
    try:
        kod, uyarilar = derle(program, kayit, hedef, os.path.basename(dosya), kutuphane_adi)
    except EkinHatasi as e:
        e._kaynak = kaynak
        raise
    for u in uyarilar:
        print(f"Uyarı: {u}", file=sys.stderr)
    return kod, kayit


def cpp_komutu(dosya, hedef):
    kod, _ = _cpp_uret(dosya, hedef)
    print(kod)
    return 0


def _derleme_klasoru(dosya):
    k = os.path.join(os.path.dirname(os.path.abspath(dosya)), "derleme")
    os.makedirs(k, exist_ok=True)
    return k


def derle_komutu(args):
    from .insa import pc_derle, guvenli_ad, calisma_zamanini_kopyala
    kod, kayit = _cpp_uret(args.dosya, "pc")
    ad = guvenli_ad(os.path.splitext(os.path.basename(args.dosya))[0])
    klasor = _derleme_klasoru(args.dosya)
    cpp = os.path.join(klasor, ad + ".cpp")
    with open(cpp, "w", encoding="utf-8") as f:
        f.write(kod)
    calisma_zamanini_kopyala(klasor)
    cikti = args.cikti or os.path.join(klasor, ad + (".exe" if os.name == "nt" else ""))
    print(f"C++ kodu: {cpp}", flush=True)
    pc_derle(cpp, cikti, list(kayit.moduller.values()), ayrintili=args.ayrintili)
    print(f"Program:  {cikti}", flush=True)
    if args.calistir:
        print("-" * 40, flush=True)
        ortam = None
        if args.kare:
            ortam = dict(os.environ, EKIN_KARE=str(args.kare))
        return subprocess.call([os.path.abspath(cikti)], env=ortam)
    return 0


def arduino_komutu(args):
    from .insa import arduino_taslagi, arduino_derle
    kod, kayit = _cpp_uret(args.dosya, "arduino")
    ad = os.path.splitext(os.path.basename(args.dosya))[0]
    taslak = arduino_taslagi(kod, _derleme_klasoru(args.dosya), ad, list(kayit.moduller.values()))
    print(f"Arduino taslağı: {taslak}", flush=True)
    cikti = arduino_derle(taslak, args.kart, args.port, args.yukle)
    for satir in cikti.splitlines():
        if "Sketch uses" in satir or "Global variables" in satir or "Taslak" in satir or "bayt" in satir:
            print("  " + satir)
    print("Karta yüklendi." if args.yukle else "Derleme başarılı. Yüklemek için: --port COM3 --yükle")
    return 0


def kutuphane_komutu(args):
    from .insa import guvenli_ad, calisma_zamanini_kopyala
    ad = guvenli_ad(os.path.splitext(os.path.basename(args.dosya))[0])
    kod, _ = _cpp_uret(args.dosya, "pc", kutuphane_adi=ad)
    klasor = args.cikti or os.path.join(_derleme_klasoru(args.dosya), ad + "_kutuphane")
    os.makedirs(klasor, exist_ok=True)
    yol = os.path.join(klasor, ad + ".hpp")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(kod)
    calisma_zamanini_kopyala(klasor, {"ekin.hpp", "ekin_dosya.hpp"})
    print(f"C++ kütüphanesi: {yol}")
    print(f"Kullanım (C++):  #include \"{ad}.hpp\"   ->   {ad}::islev_adi(...)")
    return 0


def moduller_komutu(ad=None):
    kayit = Kayit()
    adlar = Kayit.tum_modul_adlari()
    if ad is None:
        print("Modüller ('kullan <ad>' ile eklenir; * otomatik yüklenir):\n")
        for a in adlar:
            m = kayit.yukle(a)
            yildiz = "*" if m.otomatik else " "
            hedef = ", ".join(sorted(h for h in m.hedefler if h != "py"))
            print(f" {yildiz} {a:<10} {len(m.islevler):>3} komut  [{hedef}]  {m.aciklama}")
        toplam = sum(len(kayit.yukle(a).islevler) for a in adlar)
        print(f"\nToplam {toplam} komut. Ayrıntı için: ekin modüller <ad>")
        return 0
    m = kayit.yukle(ad)
    print(f"{m.ad}: {m.aciklama}\n")
    for i in m.islevler:
        print(f"  {i.imza:<55} {i.aciklama}")
        if i.ornek:
            print(f"  {'':<55}   örnek: {i.ornek}")
    if m.sabitler:
        print("\nSabitler: " + ", ".join(s.ad for s in m.sabitler))
    return 0


def komut_belgesi(yol):
    """Tüm modüllerin komut başvurusunu Markdown olarak yazar."""
    kayit = Kayit()
    s = ["# Ekin Komut Başvurusu", "",
         "Bu dosya `ekin modüller --md` ile modül tanımlarından otomatik üretilir.", "",
         "Sütunlar: **Komut** (imzadaki ekler argümanın rolünü gösterir), **Döner**, **Açıklama**. "
         "Hedef: hangi sürümlerde kullanılabildiği (py = yorumlayıcı).", ""]
    toplam = 0
    for ad in Kayit.tum_modul_adlari():
        m = kayit.yukle(ad)
        hedef = ", ".join(sorted(m.hedefler))
        oto = " (otomatik yüklenir)" if m.otomatik else f" — `kullan {ad}`"
        s += [f"## {ad}{oto}", "", f"{m.aciklama}  ", f"Hedef: {hedef}", "",
              "| Komut | Döner | Açıklama |", "|---|---|---|"]
        for i in m.islevler:
            donus = i.donus if isinstance(i.donus, str) else "(argümana göre)"
            donus = {"hiç": "—", "$0": "(1. argümanın tipi)", "$0[]": "(listenin öğesi)"}.get(donus, donus)
            aciklama = i.aciklama
            if i.ornek:
                aciklama += f"<br>örnek: `{i.ornek.replace('|', '¦')}`"
            if i.ino is False:
                aciklama += " *(Arduino'da yok)*"
            imza = i.imza.replace("|", "¦")
            s.append(f"| `{imza}` | {donus} | {aciklama} |")
            toplam += 1
        if m.sabitler:
            s += ["", "Sabitler: " + ", ".join(f"`{x.ad}`" for x in m.sabitler)]
        s.append("")
    s.insert(4, f"Toplam **{toplam}** komut.")
    s.insert(5, "")
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(s))
    print(f"{toplam} komut yazıldı: {yol}")
    return 0


def etkilesimli():
    from .yorumlayici import Yorumlayici
    from .calisma import metne
    print(f"Ekin {SURUM} etkileşimli ortam. Çıkmak için: çık  (ya da Ctrl+C)")
    print("Blok yazarken (':' ile biten satır) boş satırla bitirin.")
    kayit = Kayit([os.path.join(os.getcwd(), "moduller")])
    yorum = Yorumlayici(kayit, "<etkileşimli>")
    islevler = set()
    while True:
        try:
            satir = input("ekin> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if satir.strip() in ("çık", "cik", "exit", "quit"):
            return 0
        if not satir.strip():
            continue
        kaynak = satir
        if satir.rstrip().endswith(":"):
            while True:
                try:
                    devam = input("....  ")
                except (EOFError, KeyboardInterrupt):
                    break
                if not devam.strip():
                    break
                kaynak += "\n" + devam
        try:
            program = kaynak_ayristir(kaynak + "\n", kayit, "<etkileşimli>", islevler)
            yorum._modulleri_baslat()
            yorum.tanimlari_kaydet(program.govde)
            yorum.kuresel_adlari_bul(program.govde)
            from . import agac as A
            for d in program.govde:
                if isinstance(d, A.IfadeDeyimi):
                    sonuc = yorum.degerlendir(d.ifade, None)
                    if sonuc is not None:
                        print(metne(sonuc, True))
                elif not isinstance(d, (A.IslevTanim, A.YapiTanim)):
                    yorum.deyim(d, None)
        except EkinHatasi as e:
            print(e.bicimle(kaynak))
        except SystemExit:
            return 0
