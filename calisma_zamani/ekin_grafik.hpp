// =====================================================================
//  ekin_grafik.hpp - pencere, 2B tuval, fare ve klavye (raylib / OpenGL)
//
//  Tuval mantığı: çizimler kalıcı bir dokuya (RenderTexture) yapılır ve
//  her karede ekrana basılır. `arkaplan` tuvali temizler. Böylece
//  yorumlayıcıdaki (tkinter) davranışla aynı sonuç elde edilir.
//
//  Gerekli: raylib 4.x / 5.x  (https://www.raylib.com)
// =====================================================================
#pragma once
#include "ekin.hpp"
#include "raylib.h"

namespace ekin {
namespace grafik {

struct Durum {
    bool acik = false;
    bool kapat = false;
    int gen = 800;
    int yuk = 600;
    RenderTexture2D tuval;
    Renk renk = {255, 255, 255, 255};
    float kalinlik = 1.0f;
    Font font;
    bool font_var = false;
    tam kare = 0;
};

inline Durum& d() {
    static Durum s;
    return s;
}

inline Color rc(const Renk& r) {
    Color c = {r.r, r.g, r.b, r.a};
    return c;
}

inline Renk gecerli_renk() { return d().renk; }

inline void gerekli() {
    if (!d().acik) hata("Önce bir pencere açın: pencere_aç 800, 600, \"Başlık\"");
}

inline void yazi_tipi_yukle() {
    static const char* yollar[] = {
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    };
    // ASCII + Latin-1 + Latin Genişletilmiş-A (Ğ ğ İ ı Ş ş ve diğer Avrupa harfleri)
    // + sık kullanılan noktalama (– — ‘ ’ “ ” • …) ve para birimleri (€ ₺)
    static int kodlar[512];
    int n = 0;
    for (int k = 32; k < 127; ++k) kodlar[n++] = k;
    for (int k = 160; k < 0x180; ++k) kodlar[n++] = k;
    int ek[] = {0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x20AC, 0x20BA};
    for (int k : ek) kodlar[n++] = k;
    for (const char* y : yollar) {
        if (FileExists(y)) {
            d().font = LoadFontEx(y, 64, kodlar, n);
            if (d().font.texture.id != 0) {
                SetTextureFilter(d().font.texture, TEXTURE_FILTER_BILINEAR);
                d().font_var = true;
                return;
            }
        }
    }
}

inline void pencere_ac(tam gen, tam yuk, const metin& baslik = "Ekin") {
    if (d().acik) return;
    SetTraceLogLevel(LOG_WARNING);
    SetConfigFlags(FLAG_MSAA_4X_HINT | FLAG_VSYNC_HINT);
    InitWindow((int)gen, (int)yuk, baslik.c_str());
    SetExitKey(0);
    SetTargetFPS(60);
    d().gen = (int)gen;
    d().yuk = (int)yuk;
    yazi_tipi_yukle();
    d().tuval = LoadRenderTexture((int)gen, (int)yuk);
    d().acik = true;
    BeginTextureMode(d().tuval);
    ClearBackground(BLACK);
}

inline void pencere_kapat() { d().kapat = true; }
inline void renk_sec(const Renk& r) { d().renk = r; }
inline void kalinlik(ondalik k) { d().kalinlik = (float)k; }
inline void kare_hizi(tam fps) { SetTargetFPS((int)fps); }

inline void arkaplan(const Renk& r) { gerekli(); ClearBackground(rc(r)); }

inline void daire(ondalik x, ondalik y, ondalik r, Renk c = gecerli_renk()) {
    gerekli();
    DrawCircleV(Vector2{(float)x, (float)y}, (float)r, rc(c));
}
inline void daire_cerceve(ondalik x, ondalik y, ondalik r, Renk c = gecerli_renk()) {
    gerekli();
    float k = d().kalinlik;
    DrawRing(Vector2{(float)x, (float)y}, (float)r - k / 2, (float)r + k / 2, 0, 360, 48, rc(c));
}
inline void elips(ondalik x, ondalik y, ondalik rx, ondalik ry, Renk c = gecerli_renk()) {
    gerekli();
    DrawEllipse((int)x, (int)y, (float)rx, (float)ry, rc(c));
}
inline void dikdortgen(ondalik x, ondalik y, ondalik g, ondalik h, Renk c = gecerli_renk()) {
    gerekli();
    DrawRectangleRec(Rectangle{(float)x, (float)y, (float)g, (float)h}, rc(c));
}
inline void dikdortgen_cerceve(ondalik x, ondalik y, ondalik g, ondalik h, Renk c = gecerli_renk()) {
    gerekli();
    DrawRectangleLinesEx(Rectangle{(float)x, (float)y, (float)g, (float)h}, d().kalinlik, rc(c));
}
inline void cizgi(ondalik x1, ondalik y1, ondalik x2, ondalik y2, Renk c = gecerli_renk()) {
    gerekli();
    DrawLineEx(Vector2{(float)x1, (float)y1}, Vector2{(float)x2, (float)y2}, d().kalinlik, rc(c));
}
inline void ucgen(ondalik x1, ondalik y1, ondalik x2, ondalik y2, ondalik x3, ondalik y3,
                  Renk c = gecerli_renk()) {
    gerekli();
    Vector2 a = {(float)x1, (float)y1}, b = {(float)x2, (float)y2}, e = {(float)x3, (float)y3};
    // raylib saat yönünün tersini ister; sırayı kendimiz düzeltelim
    float alan = (b.x - a.x) * (e.y - a.y) - (b.y - a.y) * (e.x - a.x);
    if (alan > 0) DrawTriangle(a, e, b, rc(c));
    else DrawTriangle(a, b, e, rc(c));
}
inline void nokta(ondalik x, ondalik y, Renk c = gecerli_renk()) {
    gerekli();
    DrawPixelV(Vector2{(float)x, (float)y}, rc(c));
}
inline void yazi(const metin& m, ondalik x, ondalik y, ondalik boyut = 20, Renk c = gecerli_renk()) {
    gerekli();
    if (d().font_var)
        DrawTextEx(d().font, m.c_str(), Vector2{(float)x, (float)y}, (float)boyut, (float)boyut / 12, rc(c));
    else
        DrawText(m.c_str(), (int)x, (int)y, (int)boyut, rc(c));
}
template <class T> inline void yazi(const T& m, ondalik x, ondalik y, ondalik boyut = 20, Renk c = gecerli_renk()) {
    yazi(metne(m), x, y, boyut, c);
}
inline tam yazi_genisligi(const metin& m, ondalik boyut = 20) {
    if (d().font_var) return (tam)MeasureTextEx(d().font, m.c_str(), (float)boyut, (float)boyut / 12).x;
    return (tam)MeasureText(m.c_str(), (int)boyut);
}

inline tam fare_x() { return (tam)GetMouseX(); }
inline tam fare_y() { return (tam)GetMouseY(); }
inline bool fare_basili() { return IsMouseButtonDown(MOUSE_BUTTON_LEFT); }
inline bool fare_tiklandi() { return IsMouseButtonPressed(MOUSE_BUTTON_LEFT); }
inline bool tus_basili(tam k) { return IsKeyDown((int)k); }
inline bool tusa_basildi(tam k) { return IsKeyPressed((int)k); }
inline tam genislik() { return d().gen; }
inline tam yukseklik() { return d().yuk; }
inline ondalik gecen_sure() { return (ondalik)GetFrameTime(); }
inline tam kare_sayisi() { return d().kare; }

// EKIN_GORUNTU=dosya.png ise tuvalin son halini kaydeder (testler için).
inline void goruntu_kaydet() {
    const char* yol = getenv("EKIN_GORUNTU");
    if (!yol || !*yol) return;
    Image img = LoadImageFromTexture(d().tuval.texture);
    ImageFlipVertical(&img);  // OpenGL dokuları alttan yukarı saklanır
    if (!ExportImage(img, yol)) fprintf(stderr, "[görüntü kaydedilemedi: %s]\n", yol);
    UnloadImage(img);
}

// Program sonunda çağrılır: pencere kapanana kadar her_karede bloğunu çalıştırır.
// EKIN_KARE=N ise N kare sonra durur (yorumlayıcıdaki --kare seçeneğinin karşılığı).
inline void calistir(void (*kare)()) {
    if (!d().acik) return;
    EndTextureMode();
    const char* sinir_metni = getenv("EKIN_KARE");
    long sinir = sinir_metni ? atol(sinir_metni) : 0;
    while (!WindowShouldClose() && !d().kapat) {
        if (kare) {
            BeginTextureMode(d().tuval);
            kare();
            EndTextureMode();
        }
        BeginDrawing();
        ClearBackground(BLACK);
        Texture2D t = d().tuval.texture;
        DrawTextureRec(t, Rectangle{0, 0, (float)t.width, (float)-t.height}, Vector2{0, 0}, WHITE);
        EndDrawing();
        d().kare++;
        if (sinir > 0 && d().kare >= sinir) break;
    }
    goruntu_kaydet();
    UnloadRenderTexture(d().tuval);
    if (d().font_var) UnloadFont(d().font);
    CloseWindow();
    d().acik = false;
}

}  // namespace grafik
}  // namespace ekin
