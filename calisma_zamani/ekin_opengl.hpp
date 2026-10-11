// =====================================================================
//  ekin_opengl.hpp - 3B sahne ve OpenGL tarzı çizim (raylib rlgl)
//
//  rlgl, raylib'in OpenGL soyutlamasıdır: rlBegin / rlVertex3f / rlRotatef
//  çağrıları OpenGL 1.1 / 3.3 / ES2 üzerinde aynı şekilde çalışır.
//  Yüzler, yorumlayıcıdaki yazılımsal 3B çiziciyle aynı basit
//  ışıklandırmayla boyanır.
// =====================================================================
#pragma once
#include "ekin_grafik.hpp"
#include "rlgl.h"

namespace ekin {
namespace gl3 {

struct Durum {
    Camera3D kam;
    Durum() {
        kam.position = Vector3{6.0f, 5.0f, 8.0f};
        kam.target = Vector3{0.0f, 0.0f, 0.0f};
        kam.up = Vector3{0.0f, 1.0f, 0.0f};
        kam.fovy = 45.0f;
        kam.projection = CAMERA_PERSPECTIVE;
    }
};

inline Durum& d() {
    static Durum s;
    return s;
}

inline void kamera(ondalik x, ondalik y, ondalik z, ondalik hx = 0, ondalik hy = 0, ondalik hz = 0) {
    d().kam.position = Vector3{(float)x, (float)y, (float)z};
    d().kam.target = Vector3{(float)hx, (float)hy, (float)hz};
}
inline void gorus_acisi(ondalik a) { d().kam.fovy = (float)a; }

// Sahne boyunca arka yüz ayıklama kapalıdır: gl_başla ile çizilen yüzler iki
// taraftan görünür (yorumlayıcıdaki gibi); kapalı cisimlerin iç yüzlerini
// derinlik tamponu gizler.
inline void sahne_basla() {
    grafik::gerekli();
    BeginMode3D(d().kam);
    rlDisableBackfaceCulling();
}
inline void sahne_bitir() {
    // rlgl çizimleri toplar ve sonra gönderir; ayıklamayı geri açmadan önce
    // bekleyen çizimleri GPU'ya göndermezsek hepsi ayıklama açıkken çizilir.
    rlDrawRenderBatchActive();
    rlEnableBackfaceCulling();
    EndMode3D();
}

// yorumlayıcıdaki opengl.py ile aynı ışık
inline float golge(float nx, float ny, float nz) {
    const float lx = 0.32444284f, ly = 0.81110711f, lz = 0.48666426f;
    float k = nx * lx + ny * ly + nz * lz;
    return 0.55f + 0.45f * (k > 0 ? k : 0);
}
inline void boya(const Renk& r, float g) {
    rlColor4ub((unsigned char)(r.r * g), (unsigned char)(r.g * g), (unsigned char)(r.b * g), r.a);
}

inline void renk(const Renk& r) { rlColor4ub(r.r, r.g, r.b, r.a); }
inline void kose(ondalik x, ondalik y, ondalik z = 0) { rlVertex3f((float)x, (float)y, (float)z); }

inline void kutu(ondalik x, ondalik y, ondalik z, ondalik g, ondalik h, ondalik dd, Renk r = grafik::gecerli_renk()) {
    float gx = (float)g / 2, gy = (float)h / 2, gz = (float)dd / 2;
    rlPushMatrix();
    rlTranslatef((float)x, (float)y, (float)z);
    rlBegin(RL_QUADS);
    boya(r, golge(0, 0, 1));
    rlVertex3f(-gx, -gy, gz); rlVertex3f(gx, -gy, gz); rlVertex3f(gx, gy, gz); rlVertex3f(-gx, gy, gz);
    boya(r, golge(0, 0, -1));
    rlVertex3f(gx, -gy, -gz); rlVertex3f(-gx, -gy, -gz); rlVertex3f(-gx, gy, -gz); rlVertex3f(gx, gy, -gz);
    boya(r, golge(0, 1, 0));
    rlVertex3f(-gx, gy, gz); rlVertex3f(gx, gy, gz); rlVertex3f(gx, gy, -gz); rlVertex3f(-gx, gy, -gz);
    boya(r, golge(0, -1, 0));
    rlVertex3f(-gx, -gy, -gz); rlVertex3f(gx, -gy, -gz); rlVertex3f(gx, -gy, gz); rlVertex3f(-gx, -gy, gz);
    boya(r, golge(1, 0, 0));
    rlVertex3f(gx, -gy, gz); rlVertex3f(gx, -gy, -gz); rlVertex3f(gx, gy, -gz); rlVertex3f(gx, gy, gz);
    boya(r, golge(-1, 0, 0));
    rlVertex3f(-gx, -gy, -gz); rlVertex3f(-gx, -gy, gz); rlVertex3f(-gx, gy, gz); rlVertex3f(-gx, gy, -gz);
    rlEnd();
    rlPopMatrix();
}
inline void kup(ondalik x, ondalik y, ondalik z, ondalik b, Renk r = grafik::gecerli_renk()) { kutu(x, y, z, b, b, b, r); }

inline void kup_cerceve(ondalik x, ondalik y, ondalik z, ondalik b, Renk r = grafik::gecerli_renk()) {
    DrawCubeWires(Vector3{(float)x, (float)y, (float)z}, (float)b, (float)b, (float)b, grafik::rc(r));
}

inline void kure(ondalik x, ondalik y, ondalik z, ondalik yaricap, Renk r = grafik::gecerli_renk()) {
    const int halka = 10, dilim = 16;
    const float PI_F = 3.14159265f;
    float R = (float)yaricap;
    rlPushMatrix();
    rlTranslatef((float)x, (float)y, (float)z);
    rlBegin(RL_QUADS);
    for (int i = 0; i < halka; ++i) {
        for (int j = 0; j < dilim; ++j) {
            Vector3 p[4];
            int ii[4] = {i, i + 1, i + 1, i}, jj[4] = {j, j, j + 1, j + 1};
            float nx = 0, ny = 0, nz = 0;
            for (int k = 0; k < 4; ++k) {
                float en = PI_F * ii[k] / halka - PI_F / 2, boy = 2 * PI_F * jj[k] / dilim;
                p[k] = Vector3{cosf(en) * cosf(boy), sinf(en), cosf(en) * sinf(boy)};
                nx += p[k].x; ny += p[k].y; nz += p[k].z;
            }
            float n = sqrtf(nx * nx + ny * ny + nz * nz);
            if (n > 0) { nx /= n; ny /= n; nz /= n; }
            boya(r, golge(nx, ny, nz));
            for (int k = 0; k < 4; ++k) rlVertex3f(p[k].x * R, p[k].y * R, p[k].z * R);
        }
    }
    rlEnd();
    rlPopMatrix();
}

inline void silindir(ondalik x, ondalik y, ondalik z, ondalik yaricap, ondalik yukseklik,
                     Renk r = grafik::gecerli_renk()) {
    const int dilim = 16;
    const float PI_F = 3.14159265f;
    float R = (float)yaricap, H = (float)yukseklik;
    rlPushMatrix();
    rlTranslatef((float)x, (float)y, (float)z);
    rlBegin(RL_TRIANGLES);
    for (int j = 0; j < dilim; ++j) {
        float a1 = 2 * PI_F * j / dilim, a2 = 2 * PI_F * (j + 1) / dilim, am = (a1 + a2) / 2;
        float x1 = cosf(a1) * R, z1 = sinf(a1) * R, x2 = cosf(a2) * R, z2 = sinf(a2) * R;
        boya(r, golge(cosf(am), 0, sinf(am)));
        rlVertex3f(x1, 0, z1); rlVertex3f(x2, 0, z2); rlVertex3f(x2, H, z2);
        rlVertex3f(x1, 0, z1); rlVertex3f(x2, H, z2); rlVertex3f(x1, H, z1);
        boya(r, golge(0, 1, 0));
        rlVertex3f(0, H, 0); rlVertex3f(x1, H, z1); rlVertex3f(x2, H, z2);
        boya(r, golge(0, -1, 0));
        rlVertex3f(0, 0, 0); rlVertex3f(x2, 0, z2); rlVertex3f(x1, 0, z1);
    }
    rlEnd();
    rlPopMatrix();
}

inline void duzlem(ondalik x, ondalik y, ondalik z, ondalik g, ondalik dd, Renk r = grafik::gecerli_renk()) {
    float gx = (float)g / 2, gz = (float)dd / 2;
    rlBegin(RL_QUADS);
    boya(r, golge(0, 1, 0));
    rlVertex3f((float)x - gx, (float)y, (float)z - gz);
    rlVertex3f((float)x - gx, (float)y, (float)z + gz);
    rlVertex3f((float)x + gx, (float)y, (float)z + gz);
    rlVertex3f((float)x + gx, (float)y, (float)z - gz);
    rlEnd();
}

inline void izgara(tam adet, ondalik aralik) {
    float yarim = (float)(adet * aralik / 2);
    rlBegin(RL_LINES);
    rlColor4ub(110, 110, 110, 255);
    for (tam i = 0; i <= adet; ++i) {
        float v = -yarim + (float)(i * aralik);
        rlVertex3f(v, 0, -yarim); rlVertex3f(v, 0, yarim);
        rlVertex3f(-yarim, 0, v); rlVertex3f(yarim, 0, v);
    }
    rlEnd();
}

inline void cizgi3(ondalik x1, ondalik y1, ondalik z1, ondalik x2, ondalik y2, ondalik z2,
                   Renk r = grafik::gecerli_renk()) {
    DrawLine3D(Vector3{(float)x1, (float)y1, (float)z1}, Vector3{(float)x2, (float)y2, (float)z2}, grafik::rc(r));
}

}  // namespace gl3
}  // namespace ekin
