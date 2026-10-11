"""opengl: 3B sahne, kamera, şekiller ve OpenGL tarzı köşe çizimi. Kullanım: kullan opengl

Derlenmiş sürüm gerçek OpenGL kullanır (raylib'in rlgl katmanı: rlBegin, rlVertex3f,
rlRotatef ...). Yorumlayıcıda aynı komutlar, kurulum gerektirmeyen yazılımsal bir 3B
çiziciyle tkinter tuvaline çizilir (önizleme kalitesinde).

Örnek:
    kullan opengl
    pencere_aç 800, 600, "Küp"
    açı = 0
    her_karede:
        arkaplan KOYU_GRİ
        sahne_başla
        ızgara 10, 1
        gl_kaydet
        gl_döndür açı, 0, 1, 0
        küp 0, 1, 0, 2, TURUNCU
        gl_geri
        sahne_bitir
        açı += 1
"""

import math

from ekin.calisma import Renk
from ekin.modul import Islev, Sabit, Modul
from ekin.tuval_tk import TUVAL

ISIK = (0.4, 1.0, 0.6)
_n = math.sqrt(sum(c * c for c in ISIK))
ISIK = tuple(c / _n for c in ISIK)


def golge(nx, ny, nz):
    """Derlenmiş sürümle aynı basit ışıklandırma."""
    return 0.55 + 0.45 * max(0.0, nx * ISIK[0] + ny * ISIK[1] + nz * ISIK[2])


def _birim():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def _carp(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _uygula(m, p):
    x, y, z = p
    return (m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
            m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
            m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3])


def _yon_uygula(m, v):
    x, y, z = v
    return (m[0][0] * x + m[0][1] * y + m[0][2] * z,
            m[1][0] * x + m[1][1] * y + m[1][2] * z,
            m[2][0] * x + m[2][1] * y + m[2][2] * z)


def _normal(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / n for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _fark(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _ara(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(len(a)))


def _uzunluk(a, b):
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in range(3)))


# Ressam algoritması yüzleri merkezlerine göre sıralar; zemin gibi büyük yüzlerde
# bu yanılır. Büyük yüzler ve çizgiler bu boydan küçük parçalara bölünür.
PARCA_BOYU = 1.0
EN_COK_PARCA = 24
# tkinter çokgenleri tek renklidir: köşe renkleri farklı bir yüz, OpenGL'deki
# renk geçişine benzesin diye en az bu kadar parçaya bölünür.
GECIS_PARCASI = 8


def _parca_sayisi(uzunluk, gecis):
    n = min(EN_COK_PARCA, max(1, math.ceil(uzunluk / PARCA_BOYU - 1e-9)))
    return max(n, GECIS_PARCASI) if gecis else n


def _renk_ara(renkler, agirliklar):
    return Renk(*(sum(r[k] * a for r, a in zip(renkler, agirliklar)) for k in range(4)))


def _yuzu_bol(pts, renkler):
    """Bir yüzü (3 ya da 4 köşe) küçük parçalara böler: [(köşeler, renk), ...]."""
    gecis = any(r != renkler[0] for r in renkler)
    if len(pts) == 4:
        n = _parca_sayisi(max(_uzunluk(pts[0], pts[1]), _uzunluk(pts[3], pts[2])), gecis)
        m = _parca_sayisi(max(_uzunluk(pts[0], pts[3]), _uzunluk(pts[1], pts[2])), gecis)
        if n == m == 1:
            return [(pts, renkler[0])]

        def nokta(u, v):
            return _ara(_ara(pts[0], pts[1], u), _ara(pts[3], pts[2], u), v)

        parcalar = []
        for i in range(n):
            for j in range(m):
                u0, u1, v0, v1 = i / n, (i + 1) / n, j / m, (j + 1) / m
                uo, vo = (u0 + u1) / 2, (v0 + v1) / 2
                renk = _renk_ara(renkler, ((1 - uo) * (1 - vo), uo * (1 - vo), uo * vo, (1 - uo) * vo))
                parcalar.append(([nokta(u0, v0), nokta(u1, v0), nokta(u1, v1), nokta(u0, v1)], renk))
        return parcalar
    if len(pts) == 3:
        a, b, c = pts
        n = _parca_sayisi(max(_uzunluk(a, b), _uzunluk(b, c), _uzunluk(c, a)), gecis)
        if n == 1:
            return [(pts, renkler[0])]

        def nokta(i, j):
            return tuple(a[k] + (b[k] - a[k]) * i / n + (c[k] - a[k]) * j / n for k in range(3))

        def renk(ucgen):
            i = sum(p[0] for p in ucgen) / 3 / n
            j = sum(p[1] for p in ucgen) / 3 / n
            return _renk_ara(renkler, (1 - i - j, i, j))

        parcalar = []
        for i in range(n):
            for j in range(n - i):
                u = [(i, j), (i + 1, j), (i, j + 1)]
                parcalar.append(([nokta(*p) for p in u], renk(u)))
                if i + j < n - 1:
                    d = [(i + 1, j), (i + 1, j + 1), (i, j + 1)]
                    parcalar.append(([nokta(*p) for p in d], renk(d)))
        return parcalar
    return [(pts, renkler[0])]


class Sahne:
    def __init__(self):
        self.goz = (6.0, 5.0, 8.0)
        self.hedef = (0.0, 0.0, 0.0)
        self.aci = 45.0
        self.yigin = [_birim()]
        self.ilkeller = []
        self.acik = False
        self.gl_mod = None
        self.gl_renk = Renk(255, 255, 255)
        self.gl_koseler = []

    @property
    def m(self):
        return self.yigin[-1]

    def carp(self, t):
        self.yigin[-1] = _carp(self.yigin[-1], t)

    # ---------------------------------------------------- matris
    def tasi(self, x, y, z):
        t = _birim()
        t[0][3], t[1][3], t[2][3] = x, y, z
        self.carp(t)

    def olcekle(self, x, y, z):
        t = _birim()
        t[0][0], t[1][1], t[2][2] = x, y, z
        self.carp(t)

    def dondur(self, aci, x, y, z):
        x, y, z = _normal((x, y, z))
        a = math.radians(aci)
        c, s = math.cos(a), math.sin(a)
        t = 1 - c
        r = [[t * x * x + c, t * x * y - s * z, t * x * z + s * y, 0],
             [t * x * y + s * z, t * y * y + c, t * y * z - s * x, 0],
             [t * x * z - s * y, t * y * z + s * x, t * z * z + c, 0],
             [0, 0, 0, 1]]
        self.carp(r)

    def kaydet(self):
        self.yigin.append([row[:] for row in self.m])

    def geri(self):
        if len(self.yigin) > 1:
            self.yigin.pop()

    # ---------------------------------------------------- ilkeller
    def yuz(self, koseler, renk, yerel_normal=None, renkler=None):
        """renkler: köşe başına renk (gl_renk ile); verilmezse tek renk."""
        dunya = [_uygula(self.m, p) for p in koseler]
        if yerel_normal is not None:
            g = golge(*yerel_normal)
            dn = _normal(_yon_uygula(self.m, yerel_normal))
        else:
            g, dn = 1.0, None
        for parca, parca_rengi in _yuzu_bol(dunya, renkler or [renk] * len(dunya)):
            self.ilkeller.append(("yuz", parca, parca_rengi, g, dn))

    def cizgi(self, a, b, renk, renk_b=None):
        a, b = _uygula(self.m, a), _uygula(self.m, b)
        renk_b = renk if renk_b is None else renk_b
        n = _parca_sayisi(_uzunluk(a, b), renk_b != renk)
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            parca_rengi = _renk_ara((renk, renk_b), (1 - (t0 + t1) / 2, (t0 + t1) / 2))
            self.ilkeller.append(("cizgi", [_ara(a, b, t0), _ara(a, b, t1)], parca_rengi, 1.0, None))

    def kutu(self, x, y, z, g, h, d, renk):
        gx, gy, gz = g / 2, h / 2, d / 2
        yuzler = [
            ((0, 0, 1), [(-gx, -gy, gz), (gx, -gy, gz), (gx, gy, gz), (-gx, gy, gz)]),
            ((0, 0, -1), [(gx, -gy, -gz), (-gx, -gy, -gz), (-gx, gy, -gz), (gx, gy, -gz)]),
            ((0, 1, 0), [(-gx, gy, gz), (gx, gy, gz), (gx, gy, -gz), (-gx, gy, -gz)]),
            ((0, -1, 0), [(-gx, -gy, -gz), (gx, -gy, -gz), (gx, -gy, gz), (-gx, -gy, gz)]),
            ((1, 0, 0), [(gx, -gy, gz), (gx, -gy, -gz), (gx, gy, -gz), (gx, gy, gz)]),
            ((-1, 0, 0), [(-gx, -gy, -gz), (-gx, -gy, gz), (-gx, gy, gz), (-gx, gy, -gz)]),
        ]
        for n, pts in yuzler:
            self.yuz([(px + x, py + y, pz + z) for px, py, pz in pts], renk, n)

    def kutu_cerceve(self, x, y, z, g, h, d, renk):
        gx, gy, gz = g / 2, h / 2, d / 2
        k = [(x + sx * gx, y + sy * gy, z + sz * gz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        for i in range(8):
            for j in range(i + 1, 8):
                if bin(i ^ j).count("1") == 1:
                    self.cizgi(k[i], k[j], renk)

    def kure(self, x, y, z, r, renk, halka=10, dilim=16):
        def nokta(i, j):
            enlem = math.pi * i / halka - math.pi / 2
            boylam = 2 * math.pi * j / dilim
            return (math.cos(enlem) * math.cos(boylam), math.sin(enlem), math.cos(enlem) * math.sin(boylam))
        for i in range(halka):
            for j in range(dilim):
                ps = [nokta(i, j), nokta(i + 1, j), nokta(i + 1, j + 1), nokta(i, j + 1)]
                n = _normal(tuple(sum(p[k] for p in ps) for k in range(3)))
                self.yuz([(x + p[0] * r, y + p[1] * r, z + p[2] * r) for p in ps], renk, n)

    def silindir(self, x, y, z, r, h, renk, dilim=16):
        for j in range(dilim):
            a1 = 2 * math.pi * j / dilim
            a2 = 2 * math.pi * (j + 1) / dilim
            p1 = (math.cos(a1) * r, math.sin(a1) * r)
            p2 = (math.cos(a2) * r, math.sin(a2) * r)
            am = (a1 + a2) / 2
            self.yuz([(x + p1[0], y, z + p1[1]), (x + p2[0], y, z + p2[1]),
                      (x + p2[0], y + h, z + p2[1]), (x + p1[0], y + h, z + p1[1])],
                     renk, (math.cos(am), 0, math.sin(am)))
            self.yuz([(x, y + h, z), (x + p1[0], y + h, z + p1[1]), (x + p2[0], y + h, z + p2[1])], renk, (0, 1, 0))
            self.yuz([(x, y, z), (x + p2[0], y, z + p2[1]), (x + p1[0], y, z + p1[1])], renk, (0, -1, 0))

    # ---------------------------------------------------- çizim
    def ciz(self):
        if TUVAL.tuval is None:
            return
        en, boy = TUVAL.gen, TUVAL.yuk
        f_ = _normal(_fark(self.hedef, self.goz))
        s_ = _normal(_cross(f_, (0, 1, 0)))
        u_ = _cross(s_, f_)

        def gor(p):
            d = _fark(p, self.goz)
            return (_dot(d, s_), _dot(d, u_), -_dot(d, f_))

        odak = 1 / math.tan(math.radians(self.aci) / 2)
        oran = en / boy
        cizilecek = []
        for tur, pts, renk, g, dn in self.ilkeller:
            if dn is not None:
                merkez = tuple(sum(p[k] for p in pts) / len(pts) for k in range(3))
                if _dot(dn, _fark(self.goz, merkez)) <= 0:
                    continue  # arka yüz
            kp = [gor(p) for p in pts]
            if any(p[2] > -0.05 for p in kp):
                continue
            ekran = []
            for x, y, z in kp:
                ekran += [(odak / oran * x / -z + 1) / 2 * en, (1 - odak * y / -z) / 2 * boy]
            derinlik = sum(p[2] for p in kp) / len(kp)
            if tur == "cizgi":
                # zemin parçasının kenarındaki çizgi, önündeki parçanın altında kalmasın
                derinlik += PARCA_BOYU * 0.6
            cizilecek.append((derinlik, tur, ekran, renk, g))
        cizilecek.sort(key=lambda c: c[0])
        for _, tur, ekran, renk, g in cizilecek:
            r = Renk(renk[0] * g, renk[1] * g, renk[2] * g).onaltilik
            if tur == "cizgi":
                TUVAL.tuval.create_line(*ekran, fill=r, width=TUVAL.kalinlik)
            else:
                TUVAL.tuval.create_polygon(*ekran, fill=r, outline=r)


S = Sahne()


def _r(renk):
    return renk if renk is not None else TUVAL.renk


def _kamera(x, y, z, hx=0, hy=0, hz=0):
    S.goz, S.hedef = (x, y, z), (hx, hy, hz)


def _sahne_basla():
    TUVAL.gerekli()
    S.acik = True
    S.ilkeller = []
    S.yigin = [_birim()]


def _sahne_bitir():
    S.ciz()
    S.acik = False
    S.ilkeller = []


def _gl_basla(mod):
    S.gl_mod = mod
    S.gl_koseler = []


def _gl_kose(x, y, z=0):
    S.gl_koseler.append(((x, y, z), S.gl_renk))


def _gl_bitir():
    adim = {1: 2, 4: 3, 7: 4}.get(S.gl_mod, 3)
    k = S.gl_koseler
    for i in range(0, len(k) - adim + 1, adim):
        grup = k[i:i + adim]
        if adim == 2:
            S.cizgi(grup[0][0], grup[1][0], grup[0][1], grup[1][1])
        else:
            S.yuz([p for p, _ in grup], grup[0][1], renkler=[r for _, r in grup])
    S.gl_koseler = []


def _izgara(adet, aralik):
    yarim = adet * aralik / 2
    renk = Renk(110, 110, 110)
    for i in range(adet + 1):
        v = -yarim + i * aralik
        S.cizgi((v, 0, -yarim), (v, 0, yarim), renk)
        S.cizgi((-yarim, 0, v), (yarim, 0, v), renk)


O = "ekin::gl3::"

MODUL = Modul(
    "opengl",
    "3B sahne, kamera, şekiller ve OpenGL tarzı köşe çizimi (rlgl/OpenGL ile derlenir).",
    hedefler=("py", "pc"),
    basliklar={"pc": ['"ekin_opengl.hpp"']},
    bagimliliklar=["grafik"],
    islevler=[
        Islev("kamera(x, y, z, hedef_x?, hedef_y?, hedef_z?)", py=_kamera, cpp=O + "kamera({*})",
              aciklama="Kameranın yerini ve baktığı noktayı ayarlar.", ornek="kamera 6, 5, 8, 0, 0, 0"),
        Islev("görüş_açısı(derece)", py=lambda d: setattr(S, "aci", d), cpp=O + "gorus_acisi({0})",
              aciklama="Dikey görüş açısı (varsayılan 45)."),
        Islev("sahne_başla()", py=_sahne_basla, cpp=O + "sahne_basla()", aciklama="3B çizime başlar."),
        Islev("sahne_bitir()", py=_sahne_bitir, cpp=O + "sahne_bitir()", aciklama="3B çizimi bitirir."),
        Islev("küp(x, y, z, boyut, renk?)", py=lambda x, y, z, b, c=None: S.kutu(x, y, z, b, b, b, _r(c)),
              cpp=O + "kup({*})", aciklama="Küp (x, y, z merkez).", ornek="küp 0, 1, 0, 2, KIRMIZI"),
        Islev("kutu(x, y, z, genişlik, yükseklik, derinlik, renk?)",
              py=lambda x, y, z, g, h, d, c=None: S.kutu(x, y, z, g, h, d, _r(c)), cpp=O + "kutu({*})",
              aciklama="Dikdörtgenler prizması."),
        Islev("küp_çerçeve(x, y, z, boyut, renk?)",
              py=lambda x, y, z, b, c=None: S.kutu_cerceve(x, y, z, b, b, b, _r(c)), cpp=O + "kup_cerceve({*})",
              aciklama="Küpün tel çerçevesi."),
        Islev("küre(x, y, z, yarıçap, renk?)", py=lambda x, y, z, r, c=None: S.kure(x, y, z, r, _r(c)),
              cpp=O + "kure({*})", aciklama="Küre."),
        Islev("silindir(x, y, z, yarıçap, yükseklik, renk?)",
              py=lambda x, y, z, r, h, c=None: S.silindir(x, y, z, r, h, _r(c)), cpp=O + "silindir({*})",
              aciklama="Dik silindir (taban merkezi x, y, z)."),
        Islev("düzlem(x, y, z, genişlik, derinlik, renk?)",
              py=lambda x, y, z, g, d, c=None: S.yuz([(x - g / 2, y, z - d / 2), (x - g / 2, y, z + d / 2),
                                                      (x + g / 2, y, z + d / 2), (x + g / 2, y, z - d / 2)],
                                                     _r(c), (0, 1, 0)),
              cpp=O + "duzlem({*})", aciklama="Yatay düzlem (zemin)."),
        Islev("ızgara(adet, aralık)", py=_izgara, cpp=O + "izgara({0}, {1})", aciklama="Zemin ızgarası."),
        Islev("çizgi3(x1, y1, z1, x2, y2, z2, renk?)",
              py=lambda a, b, c, d, e, f, r=None: S.cizgi((a, b, c), (d, e, f), _r(r)), cpp=O + "cizgi3({*})",
              aciklama="3B çizgi."),
        Islev("gl_kaydet()", py=S.kaydet, cpp="rlPushMatrix()", aciklama="Dönüşüm matrisini saklar (glPushMatrix)."),
        Islev("gl_geri()", py=S.geri, cpp="rlPopMatrix()", aciklama="Saklanan matrise döner (glPopMatrix)."),
        Islev("gl_taşı(x, y, z)", py=S.tasi, cpp="rlTranslatef((float)({0}), (float)({1}), (float)({2}))",
              aciklama="Öteleme (glTranslatef)."),
        Islev("gl_döndür(açı, x, y, z)", py=S.dondur,
              cpp="rlRotatef((float)({0}), (float)({1}), (float)({2}), (float)({3}))",
              aciklama="Eksen etrafında derece cinsinden döndürme (glRotatef).", ornek="gl_döndür açı, 0, 1, 0"),
        Islev("gl_ölçekle(x, y, z)", py=S.olcekle, cpp="rlScalef((float)({0}), (float)({1}), (float)({2}))",
              aciklama="Ölçekleme (glScalef)."),
        Islev("gl_başla(kip)", py=_gl_basla, cpp="rlBegin({0})", aciklama="Köşe çizimine başlar (glBegin).",
              ornek="gl_başla GL_ÜÇGENLER"),
        Islev("gl_renk(renk'i)", py=lambda r: setattr(S, "gl_renk", r), cpp=O + "renk({0})",
              aciklama="Sonraki köşelerin rengi (glColor)."),
        Islev("gl_köşe(x, y, z?)", py=_gl_kose, cpp=O + "kose({*})", aciklama="Bir köşe ekler (glVertex3f)."),
        Islev("gl_bitir()", py=_gl_bitir, cpp="rlEnd()", aciklama="Köşe çizimini bitirir (glEnd)."),
    ],
    sabitler=[
        Sabit("GL_ÇİZGİLER", 1, "RL_LINES", tip="tam", aciklama="Her 2 köşe bir çizgi"),
        Sabit("GL_ÜÇGENLER", 4, "RL_TRIANGLES", tip="tam", aciklama="Her 3 köşe bir üçgen"),
        Sabit("GL_DÖRTGENLER", 7, "RL_QUADS", tip="tam", aciklama="Her 4 köşe bir dörtgen"),
    ],
)
