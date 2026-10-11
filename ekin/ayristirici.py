"""Ayrıştırıcı (parser): jetonlardan sözdizim ağacı üretir.

Cümle yapıları:
    yaz "merhaba"              eylem başta  (komut biçimi)
    "merhaba"'yı yaz           eylem sonda  (Türkçe SOV biçimi)
    5'i sayılar'a ekle         hal ekleri argüman rolünü belirler
    liste'nin uzunluğu         ilgi + iyelik -> uzunluk(liste)
    x > 5 ise: ...             eğer x > 5: ... ile aynı
    x < 10 iken: ...           iken x < 10: ... ile aynı
    5 kez tekrarla: ...
"""

from . import agac as A
from .ekler import kok_bul, iyelik_coz, IYELIK_EKLERI, ek_coz, ascii_yap
from .hatalar import SozdizimHatasi, EkinHatasi
from .sozcukler import SozcukAyirici

OZEL_BLOKLAR = {"kurulum": "kurulum", "döngü": "döngü", "dongu": "döngü",
                "her_karede": "her_karede"}

ATAMA_ISLECLERI = {"=", "+=", "-=", "*=", "/=", "%=", "//=", "**="}
KARSILASTIRMA = {"==", "!=", "<", ">", "<=", ">="}
CUMLE_SONU_ISLECLERI = {":", ")", "]", "}", ",", "->"} | ATAMA_ISLECLERI
IFADE_ANAHTARLARI = {"doğru", "yanlış", "boş", "bu", "değil"}


class Ayristirici:
    def __init__(self, jetonlar, kayit, dosya=None, ust=None):
        self.j = jetonlar
        self.p = 0
        self.kayit = kayit
        self.dosya = dosya
        if ust is not None:
            self.islev_adlari = ust.islev_adlari
            self.tanimli = ust.tanimli
        else:
            self.islev_adlari = set()
            self.tanimli = set(OZEL_BLOKLAR)
            self._on_tarama()

    # ------------------------------------------------------------ yardımcılar
    def hata(self, ileti, jeton=None):
        jeton = jeton or self.bak()
        raise SozdizimHatasi(ileti, jeton.satir, jeton.sutun, self.dosya)

    def bak(self, n=0):
        k = min(self.p + n, len(self.j) - 1)
        return self.j[k]

    def al(self):
        t = self.j[self.p]
        if self.p < len(self.j) - 1:
            self.p += 1
        return t

    def islec_mi(self, deger, n=0):
        t = self.bak(n)
        return t.tur == "ISLEC" and t.deger == deger

    def anahtar_mi(self, deger, n=0):
        t = self.bak(n)
        return t.tur == "ANAHTAR" and t.deger == deger

    def esles_islec(self, deger):
        if self.islec_mi(deger):
            return self.al()
        return None

    def esles_anahtar(self, deger):
        if self.anahtar_mi(deger):
            return self.al()
        return None

    def bekle_islec(self, deger, ileti=None):
        if not self.islec_mi(deger):
            self.hata(ileti or f"'{deger}' bekleniyordu, '{self._goster(self.bak())}' bulundu.")
        return self.al()

    def bekle_anahtar(self, deger, ileti=None):
        if not self.anahtar_mi(deger):
            self.hata(ileti or f"'{deger}' bekleniyordu, '{self._goster(self.bak())}' bulundu.")
        return self.al()

    def bekle_ad(self, ileti):
        if self.bak().tur != "AD":
            self.hata(ileti)
        return self.al()

    @staticmethod
    def _goster(t):
        if t.tur == "SATIR":
            return "satır sonu"
        if t.tur == "SON":
            return "dosya sonu"
        if t.tur in ("GIRINTI", "CIKINTI"):
            return "girinti"
        if t.tur == "METIN":
            return "metin"
        return str(t.deger)

    def satir_atla(self):
        while self.bak().tur == "SATIR":
            self.al()

    def satir_sonu(self):
        t = self.bak()
        if t.tur == "SATIR":
            self.al()
        elif t.tur in ("SON", "CIKINTI"):
            pass
        else:
            self.hata(f"Satır sonu bekleniyordu, '{self._goster(t)}' bulundu. "
                      f"Bir satıra tek komut yazılır.")

    # ------------------------------------------------------------ ön tarama
    def _on_tarama(self):
        """Tanımlı isimleri toplar (ekli sözcüklerin kökünü bulmak için) ve
        `kullan` edilen modülleri önceden yükler."""
        j = self.j
        param_derinlik = None
        for k, t in enumerate(j):
            sonraki = j[k + 1] if k + 1 < len(j) else t
            if t.tur == "ANAHTAR":
                if t.deger == "kullan":
                    m = k + 1
                    while m < len(j) and j[m].tur in ("AD", "ISLEC") and not (
                            j[m].tur == "ISLEC" and j[m].deger in ("<", '"')):
                        if j[m].tur == "AD":
                            try:
                                self.kayit.yukle(j[m].deger, j[m].satir)
                            except EkinHatasi as e:
                                raise SozdizimHatasi(e.ileti, j[m].satir, j[m].sutun, self.dosya)
                        elif j[m].deger != ",":
                            break
                        m += 1
                elif t.deger in ("işlev", "yapı") and sonraki.tur == "AD":
                    self.islev_adlari.add(sonraki.deger)
                    self.tanimli.add(sonraki.deger)
                    if t.deger == "işlev":
                        param_derinlik = 0
                elif t.deger in ("için", "her", "sabit") and sonraki.tur == "AD":
                    self.tanimli.add(sonraki.deger)
                continue
            if param_derinlik is not None and t.tur == "ISLEC":
                if t.deger == "(":
                    param_derinlik += 1
                elif t.deger == ")":
                    param_derinlik -= 1
                    if param_derinlik == 0:
                        param_derinlik = None
                continue
            if t.tur == "AD":
                if param_derinlik == 1 and j[k - 1].tur == "ISLEC" and j[k - 1].deger in ("(", ","):
                    self.tanimli.add(t.deger)
                elif sonraki.tur == "ISLEC" and sonraki.deger in ATAMA_ISLECLERI:
                    self.tanimli.add(t.deger)
                elif sonraki.tur == "ISLEC" and sonraki.deger == ":" and k + 2 < len(j) \
                        and j[k + 2].tur == "AD" and self._tip_ardindan_esittir(k + 2):
                    self.tanimli.add(t.deger)
                elif t.ek_ham is None and sonraki.tur == "ISLEC" and sonraki.deger == "->":
                    self.tanimli.add(t.deger)  # lambda parametresi

    def _tip_ardindan_esittir(self, k):
        j = self.j
        derinlik = 0
        while k < len(j):
            t = j[k]
            if t.tur == "ISLEC" and t.deger == "[":
                derinlik += 1
            elif t.tur == "ISLEC" and t.deger == "]":
                derinlik -= 1
            elif t.tur == "ISLEC" and t.deger == "=" and derinlik == 0:
                return True
            elif t.tur != "AD":
                return False
            k += 1
        return False

    def cagrilabilir(self, ad):
        return ad in self.islev_adlari or self.kayit.islev(ad) is not None

    def _bilinen(self, ad):
        return ad in self.tanimli or ad in self.islev_adlari or \
            self.kayit.islev(ad) is not None or self.kayit.sabit(ad) is not None

    def _tum_bilinenler(self):
        return self.tanimli | self.islev_adlari | self.kayit.tum_adlar()

    # ------------------------------------------------------------ program
    def program(self):
        govde = []
        self.satir_atla()
        while self.bak().tur != "SON":
            if self.bak().tur == "GIRINTI":
                self.hata("Beklenmeyen girinti. Bu satır bir bloğun içinde değil.")
            d = self.deyim(ust_duzey=True)
            if isinstance(d, A.Program):
                govde.extend(d.govde)
            else:
                govde.append(d)
            self.satir_atla()
        return A.Program(govde, satir=1)

    def blok(self):
        self.bekle_islec(":", "Bloktan önce ':' bekleniyordu.")
        if self.bak().tur == "SATIR":
            self.al()
            self.satir_atla()
            if self.bak().tur != "GIRINTI":
                self.hata("Bloğun içi girintili (en az bir boşluk içeride) yazılmalı.")
            self.al()
            govde = []
            while True:
                self.satir_atla()
                if self.bak().tur in ("CIKINTI", "SON"):
                    break
                govde.append(self.deyim())
            if self.bak().tur == "CIKINTI":
                self.al()
            return govde
        return [self.deyim()]

    # ------------------------------------------------------------ deyimler
    def deyim(self, ust_duzey=False):
        t = self.bak()
        s = t.satir
        if t.tur == "CPP":
            self.al()
            self.satir_sonu()
            return A.HamCpp(t.deger, satir=s)
        if t.tur == "ANAHTAR":
            d = t.deger
            if d == "eğer":
                self.al()
                kosul = self.cumle()
                return self._eger_devam([(kosul, self.blok())], s)
            if d == "iken":
                self.al()
                kosul = self.cumle()
                return A.Iken(kosul, self.blok(), satir=s)
            if d == "için":
                return self.icin_deyimi()
            if d == "her":
                return self.her_deyimi()
            if d == "tekrarla":
                self.al()
                sayi = self.ifade()
                self.bekle_anahtar("kez", "'tekrarla 5 kez:' biçiminde yazın.")
                return A.Tekrarla(sayi, self.blok(), satir=s)
            if d == "sürekli":
                self.al()
                return A.Surekli(self.blok(), satir=s)
            if d == "kır":
                self.al()
                self.satir_sonu()
                return A.Kir(satir=s)
            if d == "devam":
                self.al()
                self.satir_sonu()
                return A.Devam(satir=s)
            if d == "dön":
                self.al()
                if self.bak().tur in ("SATIR", "SON", "CIKINTI"):
                    self.satir_sonu()
                    return A.Don(None, satir=s)
                deger = self.cumle()
                self.satir_sonu()
                return A.Don(deger, satir=s)
            if d == "işlev":
                return self.islev_tanimi()
            if d == "yapı":
                return self.yapi_tanimi()
            if d == "kullan":
                return self.kullan_deyimi()
            if d == "dış":
                return self.dis_deyimi()
            if d == "sabit":
                self.al()
                ad = self.bekle_ad("'sabit' sözcüğünden sonra bir ad bekleniyordu.").deger
                tip = None
                if self.esles_islec(":"):
                    tip = self.tip_adi()
                self.bekle_islec("=", "Sabitin bir değeri olmalı: sabit PI = 3.14")
                deger = self.cumle()
                self.satir_sonu()
                return A.SabitTanim(ad, deger, tip, satir=s)
            if d in ("değilse", "yoksa"):
                self.hata(f"'{d}' bir 'eğer' bloğunun hemen ardından gelmeli.")
        if t.tur == "AD" and t.deger in OZEL_BLOKLAR and t.ek is None and self.islec_mi(":", 1):
            if not ust_duzey:
                self.hata(f"'{t.deger}:' bloğu yalnızca en dış düzeyde tanımlanabilir.")
            self.al()
            ad = OZEL_BLOKLAR[t.deger]
            return A.IslevTanim(ad, [], None, self.blok(), ad, satir=s)
        return self.basit_deyim()

    def basit_deyim(self):
        t = self.bak()
        s = t.satir
        # tip belirtilmiş atama: x: tam = 5
        if t.tur == "AD" and self.islec_mi(":", 1) and self.bak(2).tur == "AD" and \
                self._tip_ardindan_esittir(self.p + 2):
            self.al()
            self.al()
            tip = self.tip_adi()
            self.bekle_islec("=")
            deger = self.cumle()
            self.satir_sonu()
            return A.Atama(A.Ad(t.deger, satir=s), "=", deger, tip, satir=s)
        ifade = self.cumle()
        n = self.bak()
        if n.tur == "ISLEC" and n.deger in ATAMA_ISLECLERI:
            if not isinstance(ifade, (A.Ad, A.Sira, A.Uye)):
                self.hata("Atamanın sol yanı bir değişken, liste öğesi ya da alan olmalı.", n)
            ifade.ek = None
            self.al()
            deger = self.cumle()
            self.satir_sonu()
            return A.Atama(ifade, n.deger, deger, None, satir=s)
        if n.tur == "ANAHTAR":
            if n.deger == "ise":
                self.al()
                return self._eger_devam([(ifade, self.blok())], s)
            if n.deger == "iken":
                self.al()
                return A.Iken(ifade, self.blok(), satir=s)
            if n.deger == "kez":
                self.al()
                self.esles_anahtar("tekrarla")
                return A.Tekrarla(ifade, self.blok(), satir=s)
        if isinstance(ifade, A.Ad) and ifade.ek is None and self.cagrilabilir(ifade.ad):
            ifade = A.Cagri(ifade, [], satir=s)
        self.satir_sonu()
        return A.IfadeDeyimi(ifade, satir=s)

    def _eger_devam(self, dallar, s):
        degilse = None
        while self.bak().tur == "ANAHTAR" and self.bak().deger in ("değilse", "yoksa"):
            self.al()
            if self.islec_mi(":"):
                degilse = self.blok()
                break
            if self.esles_anahtar("eğer"):
                kosul = self.cumle()
                dallar.append((kosul, self.blok()))
                continue
            kosul = self.cumle()
            self.bekle_anahtar("ise", "'değilse <koşul> ise:' ya da 'değilse eğer <koşul>:' biçiminde yazın.")
            dallar.append((kosul, self.blok()))
        return A.Eger(dallar, degilse, satir=s)

    def icin_deyimi(self):
        s = self.al().satir
        degisken = self.bekle_ad("'için' sözcüğünden sonra döngü değişkeni bekleniyordu: için i 1'den 10'a:")
        if degisken.ek_ham:
            self.hata("Döngü değişkeni ek almaz.", degisken)
        bas = self.ifade()
        if bas.ek == "de":
            bas.ek = None
            return A.HerDongu(degisken.deger, bas, self.blok(), satir=s)
        if bas.ek != "den":
            self.hata("Aralık döngüsü 'için i 1'den 10'a:' biçiminde yazılır "
                      "(başlangıç -dan/-den, bitiş -a/-e ekiyle).")
        bas.ek = None
        son = self.ifade()
        if son.ek not in ("e", None):
            self.hata("Bitiş değeri -a/-e ekiyle yazılır: 10'a, 20'ye")
        son.ek = None
        self.esles_anahtar("kadar")
        adim = None
        if not self.islec_mi(":"):
            adim = self.ifade()
            adim.ek = None
            self.bekle_anahtar("adımla", "Adım '2 adımla' biçiminde yazılır: için i 0'dan 10'a 2 adımla:")
        return A.AralikDongu(degisken.deger, bas, son, adim, self.blok(), satir=s)

    def her_deyimi(self):
        s = self.al().satir
        degisken = self.bekle_ad("'her' sözcüğünden sonra bir ad bekleniyordu: her x liste'de:")
        self.esles_anahtar("için")
        kume = self.ifade()
        if kume.ek != "de":
            self.hata("'her x liste'de:' biçiminde yazın (kümeye -de/-da eki gelir).")
        kume.ek = None
        return A.HerDongu(degisken.deger, kume, self.blok(), satir=s)

    def tip_adi(self):
        t = self.bekle_ad("Tip adı bekleniyordu (tam, ondalık, metin, mantık, liste[tam] ...).")
        ad = t.deger
        if self.esles_islec("["):
            ic = self.tip_adi()
            self.bekle_islec("]")
            ad = f"{ad}[{ic}]"
        return ad

    def parametreler(self):
        self.bekle_islec("(", "Parametre listesi '(' ile başlamalı.")
        params = []
        while not self.islec_mi(")"):
            t = self.bekle_ad("Parametre adı bekleniyordu.")
            tip = None
            vars_ = None
            if self.esles_islec(":"):
                tip = self.tip_adi()
            if self.esles_islec("="):
                vars_ = self.ifade()
            params.append(A.Parametre(t.deger, t.ek, tip, vars_, satir=t.satir))
            if not self.esles_islec(","):
                break
        self.bekle_islec(")")
        return params

    def islev_tanimi(self, tur="normal"):
        s = self.al().satir
        ad = self.bekle_ad("'işlev' sözcüğünden sonra işlev adı bekleniyordu.").deger
        params = self.parametreler()
        donus = None
        if self.esles_islec("->"):
            donus = self.tip_adi()
        return A.IslevTanim(ad, params, donus, self.blok(), tur, satir=s)

    def yapi_tanimi(self):
        s = self.al().satir
        ad = self.bekle_ad("'yapı' sözcüğünden sonra bir ad bekleniyordu.").deger
        self.bekle_islec(":")
        alanlar, yontemler = [], []
        if self.bak().tur != "SATIR":
            # kısa biçim: yapı Nokta: x, y
            while True:
                a = self.bekle_ad("Alan adı bekleniyordu.")
                alanlar.append((a.deger, None, None))
                if not self.esles_islec(","):
                    break
            self.satir_sonu()
            return A.YapiTanim(ad, alanlar, yontemler, satir=s)
        self.al()
        self.satir_atla()
        if self.bak().tur != "GIRINTI":
            self.hata("Yapının içi girintili yazılmalı.")
        self.al()
        while True:
            self.satir_atla()
            if self.bak().tur in ("CIKINTI", "SON"):
                break
            if self.anahtar_mi("işlev"):
                yontemler.append(self.islev_tanimi("yöntem"))
                continue
            a = self.bekle_ad("Yapı içinde alan (x = 0) ya da işlev bekleniyordu.")
            tip = None
            vars_ = None
            if self.esles_islec(":"):
                tip = self.tip_adi()
            if self.esles_islec("="):
                vars_ = self.ifade()
            alanlar.append((a.deger, tip, vars_))
            self.satir_sonu()
        if self.bak().tur == "CIKINTI":
            self.al()
        return A.YapiTanim(ad, alanlar, yontemler, satir=s)

    def _baslik_al(self):
        """<Servo.h> biçimindeki C++ başlığını okur."""
        self.bekle_islec("<")
        parca = []
        while not self.islec_mi(">"):
            t = self.al()
            if t.tur in ("SATIR", "SON"):
                self.hata("'>' bekleniyordu.")
            parca.append(str(t.deger))
        self.al()
        return "<" + "".join(parca) + ">"

    def kullan_deyimi(self):
        s = self.al().satir
        sonuc = []
        while True:
            t = self.bak()
            if self.islec_mi("<"):
                sonuc.append(A.Kullan("baslik", self._baslik_al(), satir=s))
            elif t.tur == "METIN":
                self.al()
                yol = "".join(p[1] for p in t.deger if p[0] == "yazi")
                tur = "dosya" if yol.endswith(".ekin") else "baslik"
                sonuc.append(A.Kullan(tur, yol if tur == "dosya" else f'"{yol}"', satir=s))
            elif t.tur == "AD":
                self.al()
                sonuc.append(A.Kullan("modul", ascii_yap(t.deger), satir=s))
            else:
                self.hata("'kullan' sözcüğünden sonra modül adı (grafik), dosya (\"x.ekin\") "
                          "ya da C++ başlığı (<Servo.h>) bekleniyordu.")
            if not self.esles_islec(","):
                break
        self.satir_sonu()
        return sonuc[0] if len(sonuc) == 1 else A.Program(sonuc, satir=s)

    def dis_deyimi(self):
        s = self.al().satir
        if self.islec_mi("<") or self.bak().tur == "METIN":
            if self.islec_mi("<"):
                b = self._baslik_al()
            else:
                t = self.al()
                b = '"' + "".join(p[1] for p in t.deger if p[0] == "yazi") + '"'
            self.satir_sonu()
            return A.Kullan("baslik", b, satir=s)
        if self.esles_anahtar("işlev"):
            ad = self.bekle_ad("İşlev adı bekleniyordu.").deger
            self.islev_adlari.add(ad)
            params = self.parametreler()
            donus = "hiç"
            if self.esles_islec("->"):
                donus = self.tip_adi()
            sablon = None
            if self.esles_islec("="):
                t = self.al()
                if t.tur != "METIN":
                    self.hata("C++ şablonu bir metin olmalı: = \"sqrt({0})\"", t)
                sablon = "".join(p[1] if p[0] == "yazi" else "{" + p[1] + "}" for p in t.deger)
            self.satir_sonu()
            return A.DisIslev(ad, params, donus, sablon, satir=s)
        if self.esles_anahtar("sabit"):
            ad = self.bekle_ad("Sabit adı bekleniyordu.").deger
            tip = "harici"
            if self.esles_islec("->") or self.esles_islec(":"):
                tip = self.tip_adi()
            sablon = ad
            if self.esles_islec("="):
                t = self.al()
                if t.tur != "METIN":
                    self.hata("C++ ifadesi bir metin olmalı.", t)
                sablon = "".join(p[1] for p in t.deger if p[0] == "yazi")
            self.satir_sonu()
            return A.DisSabit(ad, tip, sablon, satir=s)
        self.hata("'dış' sözcüğünden sonra 'işlev', 'sabit' ya da bir C++ başlığı bekleniyordu.")

    # ------------------------------------------------------------ cümle
    def _komut_baslar_mi(self):
        """Eylem-başta biçimi (yaz x) için: sonraki jeton bir argüman başlatıyor mu?"""
        n = self.bak(1)
        if n.satir != self.bak().satir:
            return False
        if n.tur in ("SAYI", "METIN", "AD"):
            return True
        if n.tur == "ANAHTAR" and n.deger in IFADE_ANAHTARLARI:
            return True
        if n.tur == "ISLEC":
            if n.deger in ("(", "[") and n.bosluk:
                return True
            if n.deger == "-" and n.bosluk and not self.bak(2).bosluk:
                return True
        return False

    def _cumle_sonu(self, t):
        if t.tur in ("SATIR", "SON", "CIKINTI", "GIRINTI", "CPP"):
            return True
        if t.tur == "ISLEC" and t.deger in CUMLE_SONU_ISLECLERI:
            return True
        if t.tur == "ANAHTAR" and t.deger not in IFADE_ANAHTARLARI:
            return True
        return False

    def cumle(self):
        """Bir cümle: tek ifade, eylem-başta komut ya da eylem-sonda (ekli) çağrı."""
        t = self.bak()
        s = t.satir
        if t.tur == "AD" and t.ek_ham is None and self.cagrilabilir(t.deger) and self._komut_baslar_mi():
            self.al()
            args = []
            while True:
                e = self._oge_cumlesi(eylem_basta=False)
                args.append((e, e.ek))
                if not self.esles_islec(","):
                    break
            return A.Cagri(A.Ad(t.deger, satir=s), args, satir=s)
        return self._oge_cumlesi(eylem_basta=True)

    def _oge_cumlesi(self, eylem_basta):
        """Virgüle ya da satır sonuna kadar olan öğeler: tek ifade ya da ekli çağrı."""
        t = self.bak()
        s = t.satir
        ogeler = [self.ifade()]
        while not self._cumle_sonu(self.bak()):
            ogeler.append(self.ifade())
        if len(ogeler) == 1:
            return ogeler[0]
        son = ogeler[-1]
        if isinstance(son, A.Ad) and son.ek is None and self.cagrilabilir(son.ad):
            args = [(e, e.ek) for e in ogeler[:-1]]
            return A.Cagri(A.Ad(son.ad, satir=son.satir), args, satir=s)
        ilk = ogeler[0]
        if eylem_basta and isinstance(ilk, A.Ad) and ilk.ek is None and self.cagrilabilir(ilk.ad):
            args = [(e, e.ek) for e in ogeler[1:]]
            return A.Cagri(A.Ad(ilk.ad, satir=ilk.satir), args, satir=s)
        if isinstance(son, A.Ad):
            m = self.kayit.oner(son.ad)
            if m:
                self.hata(f"'{son.ad}' komutu '{m}' modülünde. Dosyanın başına 'kullan {m}' yazın.",
                          self.bak(-1) if self.p else None)
            self.hata(f"'{son.ad}' adında bir işlev bulunamadı. Ekli cümlelerde eylem "
                      f"(işlev adı) cümlenin sonunda olmalı.", self.bak(-1) if self.p else None)
        self.hata("Bu cümle anlaşılamadı. Eylem (işlev adı) cümlenin başında ya da sonunda olmalı; "
                  "örn. 'yaz x' ya da \"x'i yaz\".", t)

    # ------------------------------------------------------------ ifadeler
    def ifade(self):
        t = self.bak()
        # lambda: x -> ...   ya da  (a, b) -> ...
        if t.tur == "AD" and self.islec_mi("->", 1):
            self.al()
            self.al()
            return A.Lambda([t.deger], self.ifade(), satir=t.satir)
        if self.islec_mi("("):
            k = 1
            adlar = []
            while self.bak(k).tur == "AD":
                adlar.append(self.bak(k).deger)
                k += 1
                if self.islec_mi(",", k):
                    k += 1
                else:
                    break
            if self.islec_mi(")", k) and self.islec_mi("->", k + 1) and (adlar or k == 1):
                for _ in range(k + 2):
                    self.al()
                return A.Lambda(adlar, self.ifade(), satir=t.satir)
        return self.veya()

    @staticmethod
    def _ikili(sol, islec, sag, satir):
        d = A.IkiliIslem(sol, islec, sag, satir=satir)
        if sag.ek:
            d.ek = sag.ek
            sag.ek = None
        return d

    def veya(self):
        sol = self.ve()
        while sol.ek is None and self.anahtar_mi("veya"):
            s = self.al().satir
            sol = self._ikili(sol, "veya", self.ve(), s)
        return sol

    def ve(self):
        sol = self.degil()
        while sol.ek is None and self.anahtar_mi("ve"):
            s = self.al().satir
            sol = self._ikili(sol, "ve", self.degil(), s)
        return sol

    def degil(self):
        if self.anahtar_mi("değil"):
            s = self.al().satir
            d = self.degil()
            n = A.TekliIslem("değil", d, satir=s)
            n.ek, d.ek = d.ek, None
            return n
        return self.karsilastirma()

    def karsilastirma(self):
        sol = self.toplama()
        t = self.bak()
        if sol.ek is None and t.tur == "ISLEC" and t.deger in KARSILASTIRMA:
            self.al()
            sol = self._ikili(sol, t.deger, self.toplama(), t.satir)
        return sol

    def toplama(self):
        sol = self.carpma()
        while sol.ek is None and self.bak().tur == "ISLEC" and self.bak().deger in ("+", "-"):
            t = self.bak()
            # 'f x -1' gibi durumlar: boşluklu '-' ve bitişik sayı -> yeni öğe
            if t.deger == "-" and t.bosluk and not self.bak(1).bosluk and isinstance(sol, A.Ad) \
                    and self.cagrilabilir(sol.ad):
                break
            self.al()
            sol = self._ikili(sol, t.deger, self.carpma(), t.satir)
        return sol

    def carpma(self):
        sol = self.tekli()
        while sol.ek is None and self.bak().tur == "ISLEC" and self.bak().deger in ("*", "/", "//", "%"):
            t = self.al()
            sol = self._ikili(sol, t.deger, self.tekli(), t.satir)
        return sol

    def tekli(self):
        t = self.bak()
        if t.tur == "ISLEC" and t.deger in ("-", "+"):
            self.al()
            d = self.tekli()
            if t.deger == "+":
                return d
            if isinstance(d, A.Sayi):
                d.deger = -d.deger
                return d
            n = A.TekliIslem("-", d, satir=t.satir)
            n.ek, d.ek = d.ek, None
            return n
        return self.us()

    def us(self):
        sol = self.sonek()
        if sol.ek is None and self.islec_mi("**"):
            t = self.al()
            sol = self._ikili(sol, "**", self.tekli(), t.satir)
        return sol

    def sonek(self):
        d = self.birincil()
        while True:
            t = self.bak()
            if d.ek == "in" and t.tur == "AD" and t.satir == self.bak(-1).satir:
                d = self._iyelik(d)
                continue
            if d.ek is not None:
                break
            if t.tur == "ISLEC" and t.deger == "(" and not t.bosluk:
                self.al()
                args = []
                while not self.islec_mi(")"):
                    e = self.cumle()
                    args.append((e, e.ek))
                    if not self.esles_islec(","):
                        break
                kapa = self.bekle_islec(")", "Çağrı ')' ile kapatılmalı.")
                d = A.Cagri(d, args, satir=t.satir, ek=kapa.ek)
                continue
            if t.tur == "ISLEC" and t.deger == "[" and not t.bosluk:
                self.al()
                sira = self.ifade()
                kapa = self.bekle_islec("]")
                d = A.Sira(d, sira, satir=t.satir, ek=kapa.ek)
                continue
            if t.tur == "ISLEC" and t.deger == "." and self.bak(1).tur == "AD":
                self.al()
                a = self.al()
                d = A.Uye(d, a.deger, satir=a.satir, ek=a.ek)
                continue
            break
        return d

    def _iyelik(self, nesne):
        t = self.al()
        if t.ek_ham:
            ek = t.ek_ham
            if ek in IYELIK_EKLERI:
                rol = None
            else:
                c = ek_coz(ek)
                rol = c[0] if c else None
            ad = t.deger
        else:
            ad, rol = iyelik_coz(t.deger, self._tum_bilinenler())
        nesne.ek = None
        return A.Iyelik(nesne, ad, satir=t.satir, ek=rol)

    def birincil(self):
        t = self.bak()
        s = t.satir
        if t.tur == "SAYI":
            self.al()
            return A.Sayi(t.deger, satir=s, ek=t.ek)
        if t.tur == "METIN":
            self.al()
            return A.Metin(self._metin_parcalari(t), satir=s, ek=t.ek)
        if t.tur == "AD":
            self.al()
            if t.ek_ham:
                return A.Ad(t.deger, satir=s, ek=t.ek)
            ad, ek = t.deger, None
            if not self._bilinen(ad):
                c = kok_bul(ad, self._tum_bilinenler())
                if c:
                    ad, ek = c
            return A.Ad(ad, satir=s, ek=ek)
        if t.tur == "ANAHTAR":
            if t.deger in ("doğru", "yanlış"):
                self.al()
                return A.Mantik(t.deger == "doğru", satir=s, ek=t.ek)
            if t.deger == "boş":
                self.al()
                return A.Bos(satir=s, ek=t.ek)
            if t.deger == "bu":
                self.al()
                return A.Bu(satir=s, ek=t.ek)
        if t.tur == "ISLEC":
            if t.deger == "(":
                self.al()
                ic = self.cumle()
                kapa = self.bekle_islec(")", "Parantez kapatılmamış: ')' bekleniyordu.")
                if kapa.ek:
                    ic.ek = kapa.ek
                return ic
            if t.deger == "[":
                self.al()
                ogeler = []
                while not self.islec_mi("]"):
                    while self.bak().tur in ("SATIR", "GIRINTI", "CIKINTI"):
                        self.al()
                    if self.islec_mi("]"):
                        break
                    ogeler.append(self.ifade())
                    if not self.esles_islec(","):
                        break
                kapa = self.bekle_islec("]", "Liste ']' ile kapatılmalı.")
                return A.Liste(ogeler, satir=s, ek=kapa.ek)
        self.hata(f"Burada bir değer bekleniyordu, '{self._goster(t)}' bulundu.")

    def _metin_parcalari(self, t):
        parcalar = []
        for p in t.deger:
            if p[0] == "yazi":
                parcalar.append(("yazi", p[1]))
            else:
                _, kaynak, satir, sutun = p
                jetonlar = SozcukAyirici(kaynak, self.dosya, satir_ici=True, ilk_satir=satir).ayir()
                alt = Ayristirici(jetonlar, self.kayit, self.dosya, ust=self)
                e = alt.cumle()
                if alt.bak().tur != "SON":
                    alt.hata("Metin içindeki ifade anlaşılamadı.")
                parcalar.append(("ifade", e))
        return parcalar


def ayristir(kaynak, kayit, dosya=None):
    from .sozcukler import ayir
    jetonlar = ayir(kaynak, dosya)
    return Ayristirici(jetonlar, kayit, dosya).program()
