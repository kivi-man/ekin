// =====================================================================
//  ekin.hpp - Ekin çalışma zamanı kütüphanesi
//
//  Derleyicinin ürettiği C++ kodu bu dosyayı kullanır. Tek başına da
//  bir C++ projesine eklenebilir: tüm işlevler `ekin::` ad alanındadır.
//
//  * PC (Windows / macOS / Linux): C++11 ve üstü, standart kütüphane
//  * Arduino (AVR dahil): C++11, standart kütüphane GEREKMEZ
//
//  Metinler UTF-8'dir; uzunluk, harf, büyüt/küçült Türkçe harfleri
//  (ç ğ ı İ ö ş ü) doğru işler.
// =====================================================================
#pragma once

#if defined(ARDUINO)
#  define EKIN_ARDUINO 1
#  include <Arduino.h>
#  include <stdlib.h>
#  include <math.h>
#else
#  include <stdint.h>
#  include <stdio.h>
#  include <stdlib.h>
#  include <math.h>
#  include <string.h>
#  include <time.h>
#  include <cmath>
#  include <string>
#  include <vector>
#  include <algorithm>
#  include <random>
#  include <chrono>
#  include <thread>
#  include <cstddef>
#endif

#if defined(_WIN32) && !defined(EKIN_ARDUINO)
extern "C" __declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleCP(unsigned int);
#endif

namespace ekin {

// ------------------------------------------------------------------ tipler
#ifdef EKIN_ARDUINO
typedef long tam;          // 32 bit
typedef double ondalik;    // AVR'de 32 bit
typedef String metin;
#else
typedef long long tam;     // 64 bit
typedef double ondalik;
typedef std::string metin;
#endif

const double pi_sayisi = 3.14159265358979323846;
const double e_sayisi = 2.71828182845904523536;
inline double sonsuz() { return INFINITY; }

struct Renk {
    uint8_t r, g, b, a;
};

inline Renk renk(tam r, tam g, tam b, tam a = 255) {
    struct S { static uint8_t k(tam v) { return (uint8_t)(v < 0 ? 0 : (v > 255 ? 255 : v)); } };
    Renk x = {S::k(r), S::k(g), S::k(b), S::k(a)};
    return x;
}

// ------------------------------------------------------------------ liste
#ifdef EKIN_ARDUINO
// Arduino'da STL olmadığı için küçük bir dinamik dizi.
template <class T>
class Liste {
    T* v_;
    tam n_, c_;
    void yer_ac_(tam istenen) {
        if (istenen <= c_) return;
        tam c = c_ ? c_ * 2 : 4;
        while (c < istenen) c *= 2;
        T* y = new T[c];
        for (tam i = 0; i < n_; ++i) y[i] = v_[i];
        delete[] v_;
        v_ = y;
        c_ = c;
    }

public:
    typedef T value_type;
    Liste() : v_(0), n_(0), c_(0) {}
    Liste(const Liste& o) : v_(0), n_(0), c_(0) { *this = o; }
    Liste(Liste&& o) : v_(o.v_), n_(o.n_), c_(o.c_) { o.v_ = 0; o.n_ = o.c_ = 0; }
    Liste& operator=(const Liste& o) {
        if (this == &o) return *this;
        yer_ac_(o.n_);
        for (tam i = 0; i < o.n_; ++i) v_[i] = o.v_[i];
        n_ = o.n_;
        return *this;
    }
    Liste& operator=(Liste&& o) {
        if (this != &o) {
            delete[] v_;
            v_ = o.v_; n_ = o.n_; c_ = o.c_;
            o.v_ = 0; o.n_ = o.c_ = 0;
        }
        return *this;
    }
    ~Liste() { delete[] v_; }
    tam size() const { return n_; }
    bool empty() const { return n_ == 0; }
    void push_back(const T& x) { yer_ac_(n_ + 1); v_[n_++] = x; }
    void pop_back() { if (n_) --n_; }
    void clear() { n_ = 0; }
    void reserve(tam n) { yer_ac_(n); }
    T& operator[](tam i) { return v_[i]; }
    const T& operator[](tam i) const { return v_[i]; }
    T* begin() { return v_; }
    T* end() { return v_ + n_; }
    const T* begin() const { return v_; }
    const T* end() const { return v_ + n_; }
    void sil_(tam i) { for (tam j = i; j + 1 < n_; ++j) v_[j] = v_[j + 1]; --n_; }
    void araya_(tam i, const T& x) {
        yer_ac_(n_ + 1);
        for (tam j = n_; j > i; --j) v_[j] = v_[j - 1];
        v_[i] = x;
        ++n_;
    }
    bool operator==(const Liste& o) const {
        if (n_ != o.n_) return false;
        for (tam i = 0; i < n_; ++i) if (!(v_[i] == o.v_[i])) return false;
        return true;
    }
    bool operator!=(const Liste& o) const { return !(*this == o); }
};
template <class T> inline void liste_sil_(Liste<T>& l, tam i) { l.sil_(i); }
template <class T> inline void liste_araya_(Liste<T>& l, tam i, const T& x) { l.araya_(i, x); }
#else
template <class T> using Liste = std::vector<T>;
template <class T> inline void liste_sil_(Liste<T>& l, tam i) { l.erase(l.begin() + (std::ptrdiff_t)i); }
template <class T> inline void liste_araya_(Liste<T>& l, tam i, const T& x) { l.insert(l.begin() + (std::ptrdiff_t)i, x); }
#endif

// ------------------------------------------------------------------ çıktı
#ifdef EKIN_ARDUINO
inline void cikti_yaz(const metin& s) { Serial.print(s); }
inline void cikti_yaz(const char* s) { Serial.print(s); }
inline void cikti_satir() { Serial.println(); }
#else
inline void cikti_yaz(const metin& s) { fwrite(s.data(), 1, s.size(), stdout); }
inline void cikti_yaz(const char* s) { fputs(s, stdout); }
inline void cikti_satir() { fputc('\n', stdout); fflush(stdout); }
#endif

[[noreturn]] inline void hata(const char* ileti) {
#ifdef EKIN_ARDUINO
    Serial.print("Calisma hatasi: ");
    Serial.println(ileti);
    Serial.flush();
    noInterrupts();
    while (true) {}
#else
    fflush(stdout);
    fprintf(stderr, "Çalışma hatası: %s\n", ileti);
    exit(1);
#endif
}

// ------------------------------------------------------------------ UTF-8
inline int u8_boy(unsigned char c) {
    if (c < 0x80) return 1;
    if ((c >> 5) == 6) return 2;
    if ((c >> 4) == 14) return 3;
    if ((c >> 3) == 30) return 4;
    return 1;
}

inline unsigned long u8_coz(const char* p, int& boy) {
    const unsigned char* s = (const unsigned char*)p;
    boy = u8_boy(s[0]);
    switch (boy) {
        case 2: return ((unsigned long)(s[0] & 0x1F) << 6) | (s[1] & 0x3F);
        case 3: return ((unsigned long)(s[0] & 0x0F) << 12) | ((unsigned long)(s[1] & 0x3F) << 6) | (s[2] & 0x3F);
        case 4: return ((unsigned long)(s[0] & 0x07) << 18) | ((unsigned long)(s[1] & 0x3F) << 12) |
                       ((unsigned long)(s[2] & 0x3F) << 6) | (s[3] & 0x3F);
        default: return s[0];
    }
}

inline void u8_ekle(metin& m, unsigned long k) {
    char b[5] = {0, 0, 0, 0, 0};
    if (k < 0x80) { b[0] = (char)k; }
    else if (k < 0x800) { b[0] = (char)(0xC0 | (k >> 6)); b[1] = (char)(0x80 | (k & 0x3F)); }
    else if (k < 0x10000) {
        b[0] = (char)(0xE0 | (k >> 12)); b[1] = (char)(0x80 | ((k >> 6) & 0x3F)); b[2] = (char)(0x80 | (k & 0x3F));
    } else {
        b[0] = (char)(0xF0 | (k >> 18)); b[1] = (char)(0x80 | ((k >> 12) & 0x3F));
        b[2] = (char)(0x80 | ((k >> 6) & 0x3F)); b[3] = (char)(0x80 | (k & 0x3F));
    }
    m += b;
}

inline metin bayt_parca(const metin& s, tam bas, tam uzun) {
#ifdef EKIN_ARDUINO
    return s.substring((unsigned int)bas, (unsigned int)(bas + uzun));
#else
    return s.substr((size_t)bas, (size_t)uzun);
#endif
}

inline tam bayt_bul(const metin& s, const metin& p, tam bas = 0) {
#ifdef EKIN_ARDUINO
    return s.indexOf(p, (unsigned int)bas);
#else
    size_t r = s.find(p, (size_t)bas);
    return r == std::string::npos ? -1 : (tam)r;
#endif
}

// bayt konumunu harf konumuna çevirir
inline tam harf_sirasi(const metin& s, tam bayt) {
    const char* p = s.c_str();
    tam n = 0;
    for (tam i = 0; i < bayt; i += u8_boy((unsigned char)p[i])) ++n;
    return n;
}

// harf konumunu bayt konumuna çevirir
inline tam bayt_sirasi(const metin& s, tam harf) {
    const char* p = s.c_str();
    tam L = (tam)s.length(), i = 0;
    while (harf > 0 && i < L) { i += u8_boy((unsigned char)p[i]); --harf; }
    return i;
}

// ------------------------------------------------------------------ metne
inline metin metne(const metin& s) { return s; }
inline metin metne(const char* s) { return metin(s); }
inline metin metne(char c) { char b[2] = {c, 0}; return metin(b); }
inline metin metne(bool b) { return b ? metin("doğru") : metin("yanlış"); }

#ifdef EKIN_ARDUINO
inline metin metne(int x) { return String(x); }
inline metin metne(long x) { return String(x); }
inline metin metne(unsigned int x) { return String(x); }
inline metin metne(unsigned long x) { return String(x); }
inline metin metne(unsigned char x) { return String((unsigned int)x); }
inline metin metne(long long x) {
    if (x >= -2147483647LL && x <= 2147483647LL) return String((long)x);
    char b[24]; char* p = b + 23; *p = 0;
    bool eksi = x < 0;
    unsigned long long u = eksi ? (unsigned long long)(-(x + 1)) + 1 : (unsigned long long)x;
    do { *--p = (char)('0' + (int)(u % 10)); u /= 10; } while (u);
    if (eksi) *--p = '-';
    return String(p);
}
inline metin metne(double x) {
    if (isnan(x)) return "nan";
    if (isinf(x)) return x > 0 ? "sonsuz" : "-sonsuz";
    String s = String(x, 6);
    int nokta = s.indexOf('.');
    if (nokta >= 0) {
        int son = s.length() - 1;
        while (son > nokta && s[son] == '0') --son;
        if (son == nokta) --son;
        s = s.substring(0, son + 1);
    }
    if (s == "-0") s = "0";
    return s;
}
#else
inline metin metne(long long x) { char b[32]; snprintf(b, sizeof b, "%lld", x); return b; }
inline metin metne(unsigned long long x) { char b[32]; snprintf(b, sizeof b, "%llu", x); return b; }
inline metin metne(int x) { return metne((long long)x); }
inline metin metne(long x) { return metne((long long)x); }
inline metin metne(short x) { return metne((long long)x); }
inline metin metne(unsigned int x) { return metne((unsigned long long)x); }
inline metin metne(unsigned long x) { return metne((unsigned long long)x); }
inline metin metne(unsigned short x) { return metne((unsigned long long)x); }
inline metin metne(unsigned char x) { return metne((unsigned long long)x); }
inline metin metne(signed char x) { return metne((long long)x); }
inline metin metne(double x) {
    if (std::isnan(x)) return "nan";
    if (std::isinf(x)) return x > 0 ? "sonsuz" : "-sonsuz";
    char b[40];
    snprintf(b, sizeof b, "%.10g", x);
    return b;
}
inline metin metne(std::nullptr_t) { return "boş"; }
#endif
inline metin metne(float x) { return metne((double)x); }

inline metin metne(const Renk& r) {
    metin s = metin("renk(") + metne((int)r.r) + ", " + metne((int)r.g) + ", " + metne((int)r.b);
    if (r.a != 255) s += metin(", ") + metne((int)r.a);
    return s + ")";
}
inline bool operator==(const Renk& a, const Renk& b) { return a.r == b.r && a.g == b.g && a.b == b.b && a.a == b.a; }
inline bool operator!=(const Renk& a, const Renk& b) { return !(a == b); }

template <class T> metin metne(const Liste<T>& l);

// liste/yapı içinde gösterim: metinler tırnaklı
template <class T> inline metin metne_ic(const T& x) { return metne(x); }
inline metin metne_ic(const metin& s) { return metin("\"") + s + "\""; }
inline metin metne_ic(const char* s) { return metin("\"") + s + "\""; }

template <class T> metin metne(const Liste<T>& l) {
    metin s = "[";
    bool ilk = true;
    for (const auto& x : l) {
        if (!ilk) s += ", ";
        ilk = false;
        s += metne_ic(x);
    }
    return s + "]";
}

// ------------------------------------------------------------------ yaz / sor
inline void yaz_hepsi() {}
template <class T, class... R> void yaz_hepsi(const T& x, const R&... r) {
    cikti_yaz(metne(x));
    if (sizeof...(r) > 0) cikti_yaz(" ");
    yaz_hepsi(r...);
}
template <class... A> void yaz(const A&... a) { yaz_hepsi(a...); cikti_satir(); }
template <class... A> void yaz_satirsiz(const A&... a) {
    yaz_hepsi(a...);
#ifndef EKIN_ARDUINO
    fflush(stdout);
#endif
}

#ifdef EKIN_ARDUINO
inline metin seri_satir_oku() {
    String s;
    while (true) {
        while (!Serial.available()) {}
        int c = Serial.read();
        if (c == '\n') break;
        if (c != '\r') s += (char)c;
    }
    return s;
}
inline metin sor(const metin& soru = "") { Serial.print(soru); return seri_satir_oku(); }
#else
inline metin sor(const metin& soru = "") {
    cikti_yaz(soru);
    fflush(stdout);
    metin s;
    int c;
    while ((c = fgetc(stdin)) != EOF && c != '\n') s += (char)c;
    if (!s.empty() && s[s.size() - 1] == '\r') s.erase(s.size() - 1);
    return s;
}
#endif

// ------------------------------------------------------------------ dönüşümler
template <class T> inline tam tam_yap(T x) { return (tam)x; }
inline tam tam_yap(const metin& s) {
#ifdef EKIN_ARDUINO
    return (tam)s.toFloat();
#else
    return (tam)strtod(s.c_str(), 0);
#endif
}
inline tam tam_yap(const char* s) { return tam_yap(metin(s)); }

template <class T> inline ondalik ondalik_yap(T x) { return (ondalik)x; }
inline ondalik ondalik_yap(const metin& s) {
    metin t = s;
#ifdef EKIN_ARDUINO
    t.replace(",", ".");
    return t.toFloat();
#else
    for (auto& c : t) if (c == ',') c = '.';
    return strtod(t.c_str(), 0);
#endif
}
inline ondalik ondalik_yap(const char* s) { return ondalik_yap(metin(s)); }

template <class T> inline bool mantik_yap(T x) { return x != 0; }
inline bool mantik_yap(bool b) { return b; }
inline bool mantik_yap(const metin& s) {
    return s == "doğru" || s == "dogru" || s == "evet" || s == "1" || s == "true";
}

// ------------------------------------------------------------------ uzunluk / harf
inline tam uzunluk(const metin& s) {
    const char* p = s.c_str();
    tam L = (tam)s.length(), n = 0;
    for (tam i = 0; i < L; i += u8_boy((unsigned char)p[i])) ++n;
    return n;
}
template <class T> inline tam uzunluk(const Liste<T>& l) { return (tam)l.size(); }

template <class T> inline bool bos_mu(const Liste<T>& l) { return l.size() == 0; }
inline bool bos_mu(const metin& s) { return s.length() == 0; }

inline Liste<metin> harfler(const metin& s) {
    Liste<metin> l;
    const char* p = s.c_str();
    tam L = (tam)s.length();
    for (tam i = 0; i < L;) {
        int b = u8_boy((unsigned char)p[i]);
        l.push_back(bayt_parca(s, i, b));
        i += b;
    }
    return l;
}

inline metin harf(const metin& s, tam i) {
    if (i < 0 || i >= uzunluk(s)) hata("Harf sırası metnin dışında.");
    tam b = bayt_sirasi(s, i);
    return bayt_parca(s, b, u8_boy((unsigned char)s.c_str()[b]));
}

// liste öğesine erişim (PC'de sınır denetimi yapılır)
template <class L> inline auto sira(L&& l, tam i) -> decltype(l[0]) {
#ifndef EKIN_ARDUINO
    if (i < 0 || i >= (tam)l.size()) {
        char b[160];
        snprintf(b, sizeof b, "Sıra numarası %lld dışarıda (uzunluk %lld). İlk öğe 0'dır.",
                 (long long)i, (long long)l.size());
        hata(b);
    }
#endif
    return l[(size_t)i];
}

// ------------------------------------------------------------------ matematik
inline ondalik bol(ondalik a, ondalik b) {
#ifndef EKIN_ARDUINO
    if (b == 0) hata("Sıfıra bölme.");
#endif
    return a / b;
}
inline tam tam_bol(tam a, tam b) {
    if (b == 0) hata("Sıfıra bölme.");
    tam q = a / b;
    if ((a % b != 0) && ((a < 0) != (b < 0))) --q;
    return q;
}
inline ondalik taban_bol(ondalik a, ondalik b) {
    if (b == 0) hata("Sıfıra bölme.");
    return floor(a / b);
}
inline tam mod_tam(tam a, tam b) {
    if (b == 0) hata("Sıfıra bölme (mod).");
    tam r = a % b;
    if (r != 0 && ((r < 0) != (b < 0))) r += b;
    return r;
}
inline ondalik mod_ond(ondalik a, ondalik b) {
    if (b == 0) hata("Sıfıra bölme (mod).");
    ondalik r = fmod(a, b);
    if (r != 0 && ((r < 0) != (b < 0))) r += b;
    return r;
}
inline tam us_tam(tam a, tam b) {
    if (b < 0) return 0;
    tam r = 1;
    while (b) { if (b & 1) r *= a; a *= a; b >>= 1; }
    return r;
}
inline ondalik us_ond(ondalik a, ondalik b) { return pow(a, b); }

template <class T> inline T mutlak(T x) { return x < 0 ? -x : x; }
template <class T> inline tam isaret(T x) { return (x > 0) - (x < 0); }
inline tam yuvarla(ondalik x) { return x >= 0 ? (tam)floor(x + 0.5) : -(tam)floor(-x + 0.5); }
inline ondalik yuvarla(ondalik x, tam basamak) {
    ondalik k = pow(10.0, (double)basamak);
    return (x >= 0 ? floor(x * k + 0.5) : -floor(-x * k + 0.5)) / k;
}
template <class T> inline T sinirla(T x, T alt, T ust) { return x < alt ? alt : (x > ust ? ust : x); }
inline ondalik olcekle(ondalik x, ondalik a1, ondalik b1, ondalik a2, ondalik b2) {
    return (x - a1) * (b2 - a2) / (b1 - a1) + a2;
}
inline tam olcekle_tam(tam x, tam a1, tam b1, tam a2, tam b2) { return (x - a1) * (b2 - a2) / (b1 - a1) + a2; }

template <class T, class A> inline T en_buyuk(A a) { return (T)a; }
template <class T, class A, class... R> inline T en_buyuk(A a, R... r) {
    T b = en_buyuk<T>(r...);
    return (T)a > b ? (T)a : b;
}
template <class T, class A> inline T en_kucuk(A a) { return (T)a; }
template <class T, class A, class... R> inline T en_kucuk(A a, R... r) {
    T b = en_kucuk<T>(r...);
    return (T)a < b ? (T)a : b;
}
template <class T> inline T en_buyuk_liste(const Liste<T>& l) {
    if (l.size() == 0) hata("Boş listenin en büyük öğesi yok.");
    T m = l[0];
    for (const auto& x : l) if (m < x) m = x;
    return m;
}
template <class T> inline T en_kucuk_liste(const Liste<T>& l) {
    if (l.size() == 0) hata("Boş listenin en küçük öğesi yok.");
    T m = l[0];
    for (const auto& x : l) if (x < m) m = x;
    return m;
}

inline bool asal_mi(tam n) {
    if (n < 2) return false;
    for (tam i = 2; i * i <= n; ++i) if (n % i == 0) return false;
    return true;
}
inline tam faktoriyel(tam n) { tam r = 1; for (tam i = 2; i <= n; ++i) r *= i; return r; }
inline tam ebob(tam a, tam b) { a = mutlak(a); b = mutlak(b); while (b) { tam t = a % b; a = b; b = t; } return a; }
inline tam ekok(tam a, tam b) { return (a && b) ? mutlak(a * b) / ebob(a, b) : 0; }

template <class T> inline T adim_denetle(T adim) {
    if (adim == 0) hata("Döngü adımı sıfır olamaz.");
    return adim;
}

// ------------------------------------------------------------------ rastgele
#ifdef EKIN_ARDUINO
inline tam rastgele(tam a, tam b) { if (a > b) { tam t = a; a = b; b = t; } return random(a, b + 1); }
inline ondalik rastgele_ondalik() { return random(0, 1000000L) / 1000000.0; }
inline void rastgele_tohum(tam t) { randomSeed((unsigned long)t); }
#else
inline std::mt19937_64& uretec() {
    static std::mt19937_64 u{std::random_device{}()};
    return u;
}
inline tam rastgele(tam a, tam b) {
    if (a > b) std::swap(a, b);
    return std::uniform_int_distribution<long long>(a, b)(uretec());
}
inline ondalik rastgele_ondalik() { return std::uniform_real_distribution<double>(0.0, 1.0)(uretec()); }
inline void rastgele_tohum(tam t) { uretec().seed((unsigned long long)t); }
#endif

inline Renk rastgele_renk() { return renk(rastgele(40, 255), rastgele(40, 255), rastgele(40, 255)); }

// ------------------------------------------------------------------ metin işlemleri
inline unsigned long tr_buyuk_harf(unsigned long k) {
    if (k == 'i') return 0x130;            // i -> İ
    if (k == 0x131) return 'I';            // ı -> I
    if (k >= 'a' && k <= 'z') return k - 32;
    if (k >= 0xE0 && k <= 0xFE && k != 0xF7) return k - 0x20;
    if (k == 0x11F || k == 0x15F) return k - 1;   // ğ ş
    return k;
}
inline unsigned long tr_kucuk_harf(unsigned long k) {
    if (k == 'I') return 0x131;            // I -> ı
    if (k == 0x130) return 'i';            // İ -> i
    if (k >= 'A' && k <= 'Z') return k + 32;
    if (k >= 0xC0 && k <= 0xDE && k != 0xD7) return k + 0x20;
    if (k == 0x11E || k == 0x15E) return k + 1;   // Ğ Ş
    return k;
}
inline metin harf_donustur_(const metin& s, bool buyuk) {
    metin r;
    const char* p = s.c_str();
    tam L = (tam)s.length();
    for (tam i = 0; i < L;) {
        int b;
        unsigned long k = u8_coz(p + i, b);
        u8_ekle(r, buyuk ? tr_buyuk_harf(k) : tr_kucuk_harf(k));
        i += b;
    }
    return r;
}
inline metin buyut(const metin& s) { return harf_donustur_(s, true); }
inline metin kucult(const metin& s) { return harf_donustur_(s, false); }

inline bool bosluk_mu_(char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f'; }

inline metin kirp(const metin& s) {
    const char* p = s.c_str();
    tam L = (tam)s.length(), a = 0, b = L;
    while (a < b && bosluk_mu_(p[a])) ++a;
    while (b > a && bosluk_mu_(p[b - 1])) --b;
    return bayt_parca(s, a, b - a);
}

inline Liste<metin> parcala(const metin& s) {
    Liste<metin> l;
    const char* p = s.c_str();
    tam L = (tam)s.length(), i = 0;
    while (i < L) {
        while (i < L && bosluk_mu_(p[i])) ++i;
        tam bas = i;
        while (i < L && !bosluk_mu_(p[i])) ++i;
        if (i > bas) l.push_back(bayt_parca(s, bas, i - bas));
    }
    return l;
}
inline Liste<metin> parcala(const metin& s, const metin& ayrac) {
    if (ayrac.length() == 0) return parcala(s);
    Liste<metin> l;
    tam bas = 0, A = (tam)ayrac.length();
    while (true) {
        tam k = bayt_bul(s, ayrac, bas);
        if (k < 0) { l.push_back(bayt_parca(s, bas, (tam)s.length() - bas)); break; }
        l.push_back(bayt_parca(s, bas, k - bas));
        bas = k + A;
    }
    return l;
}

template <class T> inline metin birlestir(const Liste<T>& l, const metin& ayrac = "") {
    metin r;
    bool ilk = true;
    for (const auto& x : l) {
        if (!ilk) r += ayrac;
        ilk = false;
        r += metne(x);
    }
    return r;
}

inline bool icerir(const metin& kaynak, const metin& aranan) { return bayt_bul(kaynak, aranan) >= 0; }
template <class T, class U> inline bool icerir(const Liste<T>& l, const U& x) {
    for (const auto& y : l) if (y == x) return true;
    return false;
}
inline tam bul(const metin& kaynak, const metin& aranan) {
    tam b = bayt_bul(kaynak, aranan);
    return b < 0 ? -1 : harf_sirasi(kaynak, b);
}
template <class T, class U> inline tam bul(const Liste<T>& l, const U& x) {
    for (tam i = 0; i < (tam)l.size(); ++i) if (l[i] == x) return i;
    return -1;
}
inline metin degistir(const metin& k, const metin& eski, const metin& yeni) {
    if (eski.length() == 0) return k;
    metin r;
    tam bas = 0, E = (tam)eski.length();
    while (true) {
        tam i = bayt_bul(k, eski, bas);
        if (i < 0) { r += bayt_parca(k, bas, (tam)k.length() - bas); break; }
        r += bayt_parca(k, bas, i - bas);
        r += yeni;
        bas = i + E;
    }
    return r;
}
inline bool baslar(const metin& m, const metin& o) {
    return o.length() <= m.length() && bayt_parca(m, 0, (tam)o.length()) == o;
}
inline bool biter(const metin& m, const metin& s) {
    return s.length() <= m.length() && bayt_parca(m, (tam)(m.length() - s.length()), (tam)s.length()) == s;
}
inline metin ters(const metin& s) {
    Liste<metin> h = harfler(s);
    metin r;
    for (tam i = (tam)h.size() - 1; i >= 0; --i) r += h[i];
    return r;
}
template <class T> inline Liste<T> ters(const Liste<T>& l) {
    Liste<T> r;
    for (tam i = (tam)l.size() - 1; i >= 0; --i) r.push_back(l[i]);
    return r;
}
inline metin alt_metin(const metin& s, tam bas, tam uzun = -1) {
    tam n = uzunluk(s);
    if (bas < 0) bas = 0;
    if (bas > n) bas = n;
    if (uzun < 0 || bas + uzun > n) uzun = n - bas;
    tam b1 = bayt_sirasi(s, bas), b2 = bayt_sirasi(s, bas + uzun);
    return bayt_parca(s, b1, b2 - b1);
}
inline bool sayi_mi(const metin& s) {
    metin t = kirp(s);
    if (t.length() == 0) return false;
    const char* p = t.c_str();
    char* son = 0;
    strtod(p, &son);
    return son && *son == 0;
}
inline tam karakter_kodu(const metin& s) {
    if (s.length() == 0) return 0;
    int b;
    return (tam)u8_coz(s.c_str(), b);
}
inline metin koddan_karakter(tam k) { metin r; u8_ekle(r, (unsigned long)k); return r; }
inline metin cogalt(const metin& s, tam n) { metin r; for (tam i = 0; i < n; ++i) r += s; return r; }
inline Liste<metin> satirlar(const metin& s) {
    Liste<metin> l = parcala(s, metin("\n"));
    for (auto& x : l) {
        tam L = (tam)x.length();
        if (L && x.c_str()[L - 1] == '\r') x = bayt_parca(x, 0, L - 1);
    }
    if (l.size() && l[l.size() - 1].length() == 0) l.pop_back();
    return l;
}
inline tam say(const metin& s, const metin& p) {
    if (p.length() == 0) return uzunluk(s) + 1;
    tam n = 0, bas = 0;
    while (true) {
        tam i = bayt_bul(s, p, bas);
        if (i < 0) return n;
        ++n;
        bas = i + (tam)p.length();
    }
}
template <class T, class U> inline tam say(const Liste<T>& l, const U& x) {
    tam n = 0;
    for (const auto& y : l) if (y == x) ++n;
    return n;
}

// ------------------------------------------------------------------ liste işlemleri
template <class T> inline void liste_yap_(Liste<T>&) {}
template <class T, class A, class... R> inline void liste_yap_(Liste<T>& l, const A& a, const R&... r) {
    l.push_back(T(a));
    liste_yap_(l, r...);
}
template <class T, class... A> inline Liste<T> liste_yap(const A&... a) {
    Liste<T> l;
    l.reserve(sizeof...(a));
    liste_yap_(l, a...);
    return l;
}
template <class T, class U> inline void ekle(Liste<T>& l, const U& x) { l.push_back(T(x)); }
template <class T, class U> inline bool cikar(Liste<T>& l, const U& x) {
    for (tam i = 0; i < (tam)l.size(); ++i)
        if (l[i] == x) { liste_sil_(l, i); return true; }
    return false;
}
template <class T> inline T sil(Liste<T>& l, tam i) {
    if (i < 0 || i >= (tam)l.size()) hata("Silinecek sıra listenin dışında.");
    T x = l[i];
    liste_sil_(l, i);
    return x;
}
template <class T, class U> inline void araya_ekle(Liste<T>& l, tam i, const U& x) {
    if (i < 0) i = 0;
    if (i > (tam)l.size()) i = (tam)l.size();
    liste_araya_(l, i, T(x));
}
template <class T> inline void temizle(Liste<T>& l) { l.clear(); }

template <class T> inline Liste<T> sirala(Liste<T> l) {
#ifdef EKIN_ARDUINO
    for (tam i = 1; i < (tam)l.size(); ++i) {
        T x = l[i];
        tam j = i - 1;
        while (j >= 0 && x < l[j]) { l[j + 1] = l[j]; --j; }
        l[j + 1] = x;
    }
#else
    std::stable_sort(l.begin(), l.end());
#endif
    return l;
}
template <class T> inline Liste<T> ters_sirala(const Liste<T>& l) { return ters(sirala(l)); }
template <class T> inline Liste<T> karistir(Liste<T> l) {
    for (tam i = (tam)l.size() - 1; i > 0; --i) {
        tam j = rastgele(0, i);
        T t = l[i]; l[i] = l[j]; l[j] = t;
    }
    return l;
}
template <class T> inline T topla(const Liste<T>& l) { T t = T(); for (const auto& x : l) t = t + x; return t; }
template <class T> inline T carp(const Liste<T>& l) { T t = T(1); for (const auto& x : l) t = t * x; return t; }
template <class T> inline ondalik ortalama(const Liste<T>& l) {
    if (l.size() == 0) hata("Boş listenin ortalaması alınamaz.");
    return (ondalik)topla(l) / (ondalik)l.size();
}
template <class T> inline Liste<T> dilim(const Liste<T>& l, tam bas, tam son) {
    Liste<T> r;
    if (bas < 0) bas = 0;
    if (son >= (tam)l.size()) son = (tam)l.size() - 1;
    for (tam i = bas; i <= son; ++i) r.push_back(l[i]);
    return r;
}
template <class T, class F> inline Liste<T> suz(const Liste<T>& l, F f) {
    Liste<T> r;
    for (const auto& x : l) if (f(x)) r.push_back(x);
    return r;
}
template <class T, class F> inline auto esle(const Liste<T>& l, F f) -> Liste<decltype(f(l[0]))> {
    Liste<decltype(f(l[0]))> r;
    r.reserve(l.size());
    for (const auto& x : l) r.push_back(f(x));
    return r;
}
template <class T, class F> inline bool hepsi(const Liste<T>& l, F f) { for (const auto& x : l) if (!f(x)) return false; return true; }
template <class T, class F> inline bool biri(const Liste<T>& l, F f) { for (const auto& x : l) if (f(x)) return true; return false; }
template <class T> inline T ilk(const Liste<T>& l) { if (l.size() == 0) hata("Boş listenin ilk öğesi yok."); return l[0]; }
template <class T> inline T son(const Liste<T>& l) { if (l.size() == 0) hata("Boş listenin son öğesi yok."); return l[l.size() - 1]; }
template <class U> inline Liste<U> doldur(tam n, const U& x) { Liste<U> l; for (tam i = 0; i < n; ++i) l.push_back(x); return l; }
inline Liste<metin> doldur(tam n, const char* x) { return doldur(n, metin(x)); }
template <class T> inline Liste<T> liste_birlestir(Liste<T> a, const Liste<T>& b) {
    for (const auto& x : b) a.push_back(x);
    return a;
}
inline Liste<tam> aralik(tam a, tam b, tam adim = 1) {
    Liste<tam> l;
    adim_denetle(adim);
    for (tam i = a; adim > 0 ? i <= b : i >= b; i += adim) l.push_back(i);
    return l;
}

// ------------------------------------------------------------------ zaman
#ifdef EKIN_ARDUINO
inline void bekle(tam ms) { delay((unsigned long)ms); }
inline tam milisaniye() { return (tam)millis(); }
#else
inline std::chrono::steady_clock::time_point& baslangic_ani() {
    static std::chrono::steady_clock::time_point t = std::chrono::steady_clock::now();
    return t;
}
inline void bekle(tam ms) { if (ms > 0) std::this_thread::sleep_for(std::chrono::milliseconds(ms)); }
inline void mikro_bekle(tam us) { if (us > 0) std::this_thread::sleep_for(std::chrono::microseconds(us)); }
inline tam milisaniye() {
    return (tam)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - baslangic_ani()).count();
}
inline tam mikrosaniye() {
    return (tam)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - baslangic_ani()).count();
}
inline tam zaman_damgasi() { return (tam)time(0); }
inline tam saat_al(int k) {
    time_t t = time(0);
    struct tm* y = localtime(&t);
    switch (k) {
        case 0: return y->tm_hour;
        case 1: return y->tm_min;
        case 2: return y->tm_sec;
        case 3: return y->tm_mday;
        case 4: return y->tm_mon + 1;
        default: return y->tm_year + 1900;
    }
}
inline metin zaman_bicimle_(const char* b) {
    time_t t = time(0);
    char s[64];
    strftime(s, sizeof s, b, localtime(&t));
    return s;
}
inline metin tarih_metni() { return zaman_bicimle_("%d.%m.%Y"); }
inline metin saat_metni() { return zaman_bicimle_("%H:%M:%S"); }
#endif

// ------------------------------------------------------------------ program
#ifndef EKIN_ARDUINO
inline Liste<metin>& program_argumanlari() { static Liste<metin> a; return a; }
#endif

inline void iddia(bool kosul, const metin& ileti = "iddia başarısız") {
    if (!kosul) {
        metin m = metin("İddia başarısız: ") + ileti;
        hata(m.c_str());
    }
}

inline void cik(tam kod = 0) {
#ifdef EKIN_ARDUINO
    (void)kod;
    Serial.flush();
    while (true) {}
#else
    fflush(stdout);
    exit((int)kod);
#endif
}

#ifdef EKIN_ARDUINO
inline void baslat() {
#  ifdef EKIN_SERI
    Serial.begin(9600);
#  endif
}
#else
inline void baslat(int argc = 0, char** argv = 0) {
#  ifdef _WIN32
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);
#  endif
    baslangic_ani();
    for (int i = 1; i < argc; ++i) program_argumanlari().push_back(argv[i]);
}
#endif

}  // namespace ekin
