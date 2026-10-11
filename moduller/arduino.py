"""arduino: pinler, seri port, kesmeler, ton, servo, EEPROM.

Derlenmiş sürüm Arduino çekirdeğinin (Arduino.h) işlevlerine dönüşür. Yorumlayıcıda
bu komutlar bir **benzetim (simülasyon)** olarak çalışır: pin değişiklikleri ekrana
yazılır, okunacak değerler `sim_ayarla` ile verilebilir. Böylece kartı takmadan
program mantığını PC'de deneyebilirsiniz.

Arduino'nun burada Türkçe karşılığı olmayan her özelliği yine kullanılabilir:
C++ adları olduğu gibi aktarılır (ör. `Serial.println(x)`, `digitalWrite(13, HIGH)`),
herhangi bir kütüphane `kullan <Kutuphane.h>` ile eklenir.
"""

import sys
import time

from ekin.calisma import SECENEKLER, metne
from ekin.modul import Islev, Sabit, Modul

# ------------------------------------------------------------------ benzetim
_PIN = {}        # pin -> değer
_MOD = {}        # pin -> mod
_SIM_GIRIS = {}  # sim_ayarla ile verilen okumalar
_EEPROM = {}
_SERVO = {}
_KESME = {}

GIRIS, CIKIS, GIRIS_DIRENCLI = 0, 1, 2
_MOD_ADI = {0: "GİRİŞ", 1: "ÇIKIŞ", 2: "GİRİŞ_DİRENÇLİ"}
A_PINLERI = {f"A{i}": 14 + i for i in range(8)}


def _sim(ileti):
    if not SECENEKLER.get("sessiz_sim"):
        print(f"  [arduino] {ileti}", flush=True)


def _pin_adi(p):
    for ad, no in A_PINLERI.items():
        if no == p:
            return ad
    return str(p)


def _pin_modu(pin, mod=CIKIS):
    _MOD[pin] = mod
    _sim(f"pin {_pin_adi(pin)} -> {_MOD_ADI.get(mod, mod)}")


def _dijital_yaz(pin, deger):
    deger = 1 if deger else 0
    _PIN[pin] = deger
    _sim(f"pin {_pin_adi(pin)} = {'YÜKSEK' if deger else 'DÜŞÜK'}")


def _dijital_oku(pin):
    if pin in _SIM_GIRIS:
        return 1 if _SIM_GIRIS[pin] else 0
    if _MOD.get(pin) == GIRIS_DIRENCLI:
        return 1
    return _PIN.get(pin, 0)


def _analog_oku(pin):
    return int(_SIM_GIRIS.get(pin, 512))


def _analog_yaz(pin, deger):
    _PIN[pin] = deger
    _sim(f"pin {_pin_adi(pin)} PWM = {deger}")


def _tersle(pin):
    _dijital_yaz(pin, 0 if _PIN.get(pin, 0) else 1)


def _ton(pin, frekans, sure=None):
    _sim(f"pin {_pin_adi(pin)} ton {frekans} Hz" + (f", {sure} ms" if sure is not None else ""))


def _seri_satir_oku():
    try:
        return input().strip()
    except EOFError:
        return ""


def _servo_bagla(pin):
    _SERVO[pin] = 90
    _sim(f"servo bağlandı: pin {pin}")


def _servo_yaz(pin, aci):
    _SERVO[pin] = aci
    _sim(f"servo {pin} -> {aci}°")


def _kesme_bagla(pin, islev, mod=None):
    _KESME[pin] = islev
    _sim(f"pin {_pin_adi(pin)} kesmesi -> {getattr(islev, 'ad', 'işlev')}")


def _sim_ayarla(pin, deger):
    _SIM_GIRIS[pin] = deger
    if pin in _KESME:
        _KESME[pin]()


def _darbe_oku(pin, durum=1, zaman_asimi=1000000):
    return int(_SIM_GIRIS.get(("darbe", pin), 0))


MODUL = Modul(
    "arduino",
    "Arduino pinleri, seri port, kesmeler, ton, servo, EEPROM (yorumlayıcıda benzetim).",
    hedefler=("py", "arduino"),
    islevler=[
        # --- pin kipleri
        Islev("pin_modu(pin'i, kip'e)", py=_pin_modu, cpp="pinMode({0}, {1})",
              aciklama="Pin kipini ayarlar (GİRİŞ, ÇIKIŞ, GİRİŞ_DİRENÇLİ).", ornek="pin_modu(13, ÇIKIŞ)"),
        Islev("çıkış_yap(pin'i)", py=lambda p: _pin_modu(p, CIKIS), cpp="pinMode({0}, OUTPUT)",
              aciklama="Pini çıkış yapar.", ornek="13'ü çıkış_yap"),
        Islev("giriş_yap(pin'i)", py=lambda p: _pin_modu(p, GIRIS), cpp="pinMode({0}, INPUT)",
              aciklama="Pini giriş yapar."),
        Islev("dirençli_giriş_yap(pin'i)", py=lambda p: _pin_modu(p, GIRIS_DIRENCLI),
              cpp="pinMode({0}, INPUT_PULLUP)", aciklama="Pini dahili dirençli (pull-up) giriş yapar."),
        # --- dijital
        Islev("yak(pin'i)", py=lambda p: _dijital_yaz(p, 1), cpp="digitalWrite({0}, HIGH)",
              aciklama="Pini YÜKSEK yapar.", ornek="13'ü yak  |  led'i yak"),
        Islev("söndür(pin'i)", py=lambda p: _dijital_yaz(p, 0), cpp="digitalWrite({0}, LOW)",
              aciklama="Pini DÜŞÜK yapar.", ornek="13'ü söndür"),
        Islev("tersle(pin'i)", py=_tersle, cpp="digitalWrite({0}, !digitalRead({0}))",
              aciklama="Pinin durumunu tersine çevirir."),
        Islev("dijital_yaz(pin'e, değer'i)", py=_dijital_yaz, cpp="digitalWrite({0}, {1})",
              aciklama="Pine YÜKSEK/DÜŞÜK yazar.", ornek="YÜKSEK'i 13'e dijital_yaz"),
        Islev("dijital_oku(pin'i)", py=_dijital_oku, cpp="(ekin::tam)digitalRead({0})", donus="tam",
              aciklama="Pini okur (1 ya da 0)."),
        Islev("basılı_mı(pin'in)", py=lambda p: _dijital_oku(p) == 0, cpp="(digitalRead({0}) == LOW)",
              donus="mantık", aciklama="Dirençli girişe bağlı düğme basılıysa doğru."),
        # --- analog
        Islev("analog_oku(pin'i)", py=_analog_oku, cpp="(ekin::tam)analogRead({0})", donus="tam",
              aciklama="Analog değer okur (0-1023).", ornek="ışık = analog_oku(A0)"),
        Islev("analog_yaz(pin'e, değer'i)", py=_analog_yaz, cpp="analogWrite({0}, {1})",
              aciklama="PWM yazar (0-255).", ornek="128'i 9'a analog_yaz"),
        Islev("analog_referans(tip'i)", py=lambda t: None, cpp="analogReference({0})",
              aciklama="Analog referans gerilimini seçer."),
        # --- ses / darbe
        Islev("ton(pin'e, frekans'ı, süre?)", py=_ton, cpp="tone({*})", aciklama="Pinden ses çıkarır.",
              ornek="ton(8, 440, 200)"),
        Islev("ton_durdur(pin'i)", py=lambda p: _sim(f"pin {p} ton durdu"), cpp="noTone({0})",
              aciklama="Sesi durdurur."),
        Islev("darbe_oku(pin'i, durum?, zaman_aşımı?)", py=_darbe_oku, cpp="(ekin::tam)pulseIn({*})",
              donus="tam", aciklama="Darbe süresini mikrosaniye olarak ölçer (ör. HC-SR04)."),
        Islev("kaydırarak_gönder(veri_pini, saat_pini, sıra, değer)", py=lambda *a: _sim(f"shiftOut {a}"),
              cpp="shiftOut({0}, {1}, {2}, {3})", aciklama="Bir baytı bit bit gönderir (74HC595)."),
        Islev("kaydırarak_al(veri_pini, saat_pini, sıra)", py=lambda *a: 0, cpp="(ekin::tam)shiftIn({0}, {1}, {2})",
              donus="tam", aciklama="Bir baytı bit bit okur."),
        # --- kesmeler
        Islev("kesme_bağla(pin'e, işlev'i, kip'le?)", py=_kesme_bagla,
              cpp=lambda a, t: f"attachInterrupt(digitalPinToInterrupt({a[0]}), {a[1]}, {a[2] if len(a) > 2 else 'CHANGE'})",
              aciklama="Pin değişince işlevi çağırır.", ornek="kesme_bağla(2, düğmeye_basıldı, DÜŞEN)"),
        Islev("kesme_ayır(pin'i)", py=lambda p: _KESME.pop(p, None), cpp="detachInterrupt(digitalPinToInterrupt({0}))",
              aciklama="Pin kesmesini kaldırır."),
        Islev("kesmeleri_kapat()", py=lambda: None, cpp="noInterrupts()", aciklama="Tüm kesmeleri kapatır."),
        Islev("kesmeleri_aç()", py=lambda: None, cpp="interrupts()", aciklama="Kesmeleri açar."),
        # --- seri port
        Islev("seri_başlat(hız?)", py=lambda h=9600: _sim(f"seri port {h} baud"), cpp="Serial.begin({*})",
              ino=lambda a, t: f"Serial.begin({a[0] if a else 9600})", aciklama="Seri portu başlatır.",
              ornek="seri_başlat 115200"),
        Islev("seri_var()", py=lambda: False, cpp="(Serial.available() > 0)", donus="mantık",
              aciklama="Okunacak seri veri varsa doğru."),
        Islev("seri_oku()", py=lambda: -1, cpp="(ekin::tam)Serial.read()", donus="tam",
              aciklama="Seri porttan bir bayt okur (-1: veri yok)."),
        Islev("seri_satır_oku()", py=_seri_satir_oku, cpp="ekin::seri_satir_oku()", donus="metin",
              aciklama="Seri porttan bir satır okur."),
        Islev("seri_bayt_yaz(bayt'ı)", py=lambda b: _sim(f"seri bayt {b}"), cpp="Serial.write((uint8_t)({0}))",
              aciklama="Seri porta ham bayt yazar."),
        # --- servo
        Islev("servo_bağla(pin'e)", py=_servo_bagla, cpp="ekin::servo_bagla({0})", gerekir=["<Servo.h>"],
              aciklama="Pine bir servo motor bağlar.", ornek="9'a servo_bağla"),
        Islev("servo_yaz(pin'e, açı'yı)", py=_servo_yaz, cpp="ekin::servo_yaz({0}, {1})", gerekir=["<Servo.h>"],
              aciklama="Servoyu açıya (0-180) getirir.", ornek="90'ı 9'a servo_yaz"),
        # --- EEPROM
        Islev("eeprom_oku(adres'i)", py=lambda a: _EEPROM.get(a, 255), cpp="(ekin::tam)EEPROM.read({0})",
              donus="tam", gerekir=["<EEPROM.h>"], aciklama="Kalıcı bellekten bir bayt okur."),
        Islev("eeprom_yaz(değer'i, adres'e)", py=lambda d, a: _EEPROM.__setitem__(a, d & 255),
              cpp="EEPROM.update({1}, (uint8_t)({0}))", gerekir=["<EEPROM.h>"],
              aciklama="Kalıcı belleğe bir bayt yazar."),
        # --- benzetim yardımcısı
        Islev("sim_ayarla(pin'e, değer'i)", py=_sim_ayarla, cpp="((void)0)",
              aciklama="(Yalnız yorumlayıcı) Benzetimde pinden okunacak değeri belirler; kartta etkisizdir.",
              ornek="sim_ayarla(A0, 800)"),
    ],
    sabitler=[
        Sabit("YÜKSEK", 1, "HIGH", tip="tam", aciklama="Mantıksal 1"),
        Sabit("DÜŞÜK", 0, "LOW", tip="tam", aciklama="Mantıksal 0"),
        Sabit("GİRİŞ", GIRIS, "INPUT", tip="tam"),
        Sabit("ÇIKIŞ", CIKIS, "OUTPUT", tip="tam"),
        Sabit("GİRİŞ_DİRENÇLİ", GIRIS_DIRENCLI, "INPUT_PULLUP", tip="tam"),
        Sabit("DAHİLİ_LED", 13, "LED_BUILTIN", tip="tam", aciklama="Karttaki LED'in pini"),
        Sabit("YÜKSELEN", 3, "RISING", tip="tam", aciklama="Kesme: 0'dan 1'e geçiş"),
        Sabit("DÜŞEN", 2, "FALLING", tip="tam", aciklama="Kesme: 1'den 0'a geçiş"),
        Sabit("DEĞİŞEN", 1, "CHANGE", tip="tam", aciklama="Kesme: her değişim"),
        Sabit("LSB_ÖNCE", 0, "LSBFIRST", tip="tam"),
        Sabit("MSB_ÖNCE", 1, "MSBFIRST", tip="tam"),
    ] + [Sabit(ad, no, ad, tip="tam", aciklama="Analog pin") for ad, no in A_PINLERI.items()],
)
