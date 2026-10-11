"""Yorumlayıcının grafik arka ucu: tkinter tuvali (Python ile birlikte gelir).

Tuval mantığı (Processing gibi): çizilen her şey ekranda kalır; `arkaplan` tuvali
temizler. `her_karede:` bloğu saniyede `kare_hızı` kez çağrılır.
Derlenmiş sürüm aynı komutları raylib (OpenGL) ile çizer.
"""

import os
import time

from .calisma import Renk, SECENEKLER
from .hatalar import CalismaHatasi

# raylib tuş kodları (derlenmiş sürümle aynı sayılar)
TUS_KODLARI = {
    "Left": 263, "Right": 262, "Up": 265, "Down": 264, "space": 32, "Return": 257,
    "Escape": 256, "BackSpace": 259, "Tab": 258, "Shift_L": 340, "Shift_R": 344,
    "Control_L": 341, "Control_R": 345,
}


def _tus_kodu(olay):
    k = olay.keysym
    if k in TUS_KODLARI:
        return TUS_KODLARI[k]
    if len(k) == 1 and k.isalnum():
        return ord(k.upper())
    return None


class TkTuval:
    def __init__(self):
        self.kok = None
        self.tuval = None
        self.gen = 800
        self.yuk = 600
        self.renk = Renk(255, 255, 255)
        self.kalinlik = 1
        self.fps = 60
        self.basili = set()
        self.basildi = set()
        self.fare = (0, 0)
        self.fare_basili = False
        self.fare_tik = False
        self.kare_no = 0
        self.gecen = 1 / 60
        self.kapandi = False
        self._hata = None

    # ---------------------------------------------------------- pencere
    def ac(self, gen, yuk, baslik="Ekin"):
        import tkinter as tk
        if self.kok is not None:
            return
        self.gen, self.yuk = int(gen), int(yuk)
        self.kok = tk.Tk()
        self.kok.title(str(baslik))
        self.kok.resizable(False, False)
        self.tuval = tk.Canvas(self.kok, width=self.gen, height=self.yuk, bg="black",
                               highlightthickness=0)
        self.tuval.pack()
        self.kok.protocol("WM_DELETE_WINDOW", self.kapat)
        self.kok.bind("<KeyPress>", self._tus_bas)
        self.kok.bind("<KeyRelease>", self._tus_birak)
        self.tuval.bind("<Motion>", self._fare_hareket)
        self.tuval.bind("<B1-Motion>", self._fare_hareket)
        self.tuval.bind("<ButtonPress-1>", self._fare_bas)
        self.tuval.bind("<ButtonRelease-1>", self._fare_birak)
        self.tuval.focus_set()

    def acik_mi(self):
        return self.kok is not None and not self.kapandi

    def gerekli(self):
        if self.kok is None:
            raise CalismaHatasi("Önce bir pencere açın: pencere_aç 800, 600, \"Başlık\"")

    def kapat(self):
        if not self.kapandi and self.kok is not None:
            self.kapandi = True
            try:
                self.kok.destroy()
            except Exception:
                pass

    # ---------------------------------------------------------- olaylar
    def _tus_bas(self, o):
        k = _tus_kodu(o)
        if k is not None:
            if k not in self.basili:
                self.basildi.add(k)
            self.basili.add(k)

    def _tus_birak(self, o):
        k = _tus_kodu(o)
        if k is not None:
            self.basili.discard(k)

    def _fare_hareket(self, o):
        self.fare = (o.x, o.y)

    def _fare_bas(self, o):
        self.fare = (o.x, o.y)
        self.fare_basili = True
        self.fare_tik = True

    def _fare_birak(self, o):
        self.fare_basili = False

    # ---------------------------------------------------------- çizim
    def _r(self, renk):
        return (renk or self.renk).onaltilik

    def arkaplan(self, renk):
        self.gerekli()
        self.tuval.delete("all")
        self.tuval.configure(bg=renk.onaltilik)

    def daire(self, x, y, r, renk=None, dolu=True):
        self.gerekli()
        c = self._r(renk)
        self.tuval.create_oval(x - r, y - r, x + r, y + r, fill=c if dolu else "", outline=c,
                               width=1 if dolu else self.kalinlik)

    def elips(self, x, y, rx, ry, renk=None, dolu=True):
        self.gerekli()
        c = self._r(renk)
        self.tuval.create_oval(x - rx, y - ry, x + rx, y + ry, fill=c if dolu else "", outline=c)

    def dikdortgen(self, x, y, g, h, renk=None, dolu=True):
        self.gerekli()
        c = self._r(renk)
        if dolu:
            self.tuval.create_rectangle(x, y, x + g, y + h, fill=c, outline="", width=0)
        else:
            self.tuval.create_rectangle(x, y, x + g, y + h, outline=c, width=self.kalinlik)

    def cizgi(self, x1, y1, x2, y2, renk=None):
        self.gerekli()
        self.tuval.create_line(x1, y1, x2, y2, fill=self._r(renk), width=self.kalinlik)

    def ucgen(self, x1, y1, x2, y2, x3, y3, renk=None):
        self.gerekli()
        c = self._r(renk)
        self.tuval.create_polygon(x1, y1, x2, y2, x3, y3, fill=c, outline="")

    def cokgen(self, noktalar, renk, cerceve=None):
        self.tuval.create_polygon(*noktalar, fill=renk, outline=cerceve or "")

    def nokta(self, x, y, renk=None):
        self.gerekli()
        self.tuval.create_rectangle(x, y, x + 1, y + 1, fill=self._r(renk), outline="")

    def yazi(self, m, x, y, boyut=20, renk=None):
        self.gerekli()
        self.tuval.create_text(x, y, text=str(m), anchor="nw", fill=self._r(renk),
                               font=("Segoe UI", -int(boyut)))

    def yazi_genisligi(self, m, boyut=20):
        import tkinter.font as tkf
        if self.kok is None:
            return int(len(str(m)) * boyut * 0.55)
        return tkf.Font(family="Segoe UI", size=-int(boyut)).measure(str(m))

    def _goruntu_kaydet(self):
        """EKIN_GORUNTU=dosya.png ise son kareyi kaydeder (testler için; Pillow gerekir)."""
        yol = os.environ.get("EKIN_GORUNTU")
        if not yol:
            return
        try:
            from PIL import ImageGrab
            # ImageGrab ekranın o bölgesini alır: pencere başka pencerelerin
            # altında kalırsa onlar kaydedilir. Önce pencereyi en üste getir.
            self.kok.deiconify()
            self.kok.lift()
            self.kok.attributes("-topmost", True)
            self.kok.update()
            time.sleep(0.3)
            self.kok.update()
            x, y = self.tuval.winfo_rootx(), self.tuval.winfo_rooty()
            ImageGrab.grab(bbox=(x, y, x + self.gen, y + self.yuk)).save(yol)
        except Exception as e:  # noqa: BLE001
            print(f"[görüntü kaydedilemedi: {e}]")

    # ---------------------------------------------------------- döngü
    def calistir(self, kare):
        """Pencere kapanana kadar `kare`yi (her_karede bloğu) çağırır."""
        if self.kok is None:
            return
        sinir = SECENEKLER.get("kare_siniri")
        son = [time.perf_counter()]

        def tik():
            if self.kapandi:
                return
            t0 = time.perf_counter()
            self.gecen = max(1e-6, t0 - son[0])
            son[0] = t0
            try:
                if kare is not None:
                    kare()
            except BaseException as e:  # noqa: BLE001 - hatayı mainloop dışına taşı
                self._hata = e
                self.kapat()
                return
            self.basildi.clear()
            self.fare_tik = False
            self.kare_no += 1
            if sinir is not None and self.kare_no >= sinir:
                self._goruntu_kaydet()
                self.kapat()
                return
            gecen_ms = (time.perf_counter() - t0) * 1000
            self.kok.after(max(1, int(1000 / self.fps - gecen_ms)), tik)

        self.kok.after(1, tik)
        try:
            self.kok.mainloop()
        except KeyboardInterrupt:
            self.kapat()
        if self._hata is not None:
            h, self._hata = self._hata, None
            raise h


TUVAL = TkTuval()
