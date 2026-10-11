// ekin_dosya.hpp - dosya ve sistem işlevleri (yalnız PC)
#pragma once
#include "ekin.hpp"
#include <fstream>
#include <sstream>
#include <cstdio>

namespace ekin {
namespace dosya {

inline metin oku(const metin& yol) {
    std::ifstream f(yol, std::ios::binary);
    if (!f) {
        metin m = "Dosya okunamadı: " + yol;
        hata(m.c_str());
    }
    std::ostringstream s;
    s << f.rdbuf();
    return s.str();
}

inline Liste<metin> satirlari_oku(const metin& yol) { return satirlar(oku(yol)); }

inline void yaz(const metin& yol, const metin& icerik, bool ekle) {
    std::ofstream f(yol, ekle ? (std::ios::binary | std::ios::app) : std::ios::binary);
    if (!f) {
        metin m = "Dosyaya yazılamadı: " + yol;
        hata(m.c_str());
    }
    f << icerik;
}

inline bool var(const metin& yol) {
    std::ifstream f(yol);
    return (bool)f;
}

inline void sil(const metin& yol) { std::remove(yol.c_str()); }

}  // namespace dosya

namespace sistem {

inline tam komut(const metin& k) {
    fflush(stdout);
    return (tam)std::system(k.c_str());
}

inline metin ortam(const metin& ad) {
    const char* d = std::getenv(ad.c_str());
    return d ? metin(d) : metin();
}

inline Liste<metin> argumanlar() { return program_argumanlari(); }

inline metin platform() {
#if defined(_WIN32)
    return "windows";
#elif defined(__APPLE__)
    return "macos";
#else
    return "linux";
#endif
}

}  // namespace sistem
}  // namespace ekin
