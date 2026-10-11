// ekin_servo.hpp - pin numarasıyla servo kullanımı (Arduino)
//   servo_bağla(9)  ->  ekin::servo_bagla(9)
//   servo_yaz(9, 90) ->  ekin::servo_yaz(9, 90)
#pragma once
#include <Servo.h>
#include "ekin.hpp"

namespace ekin {

const int SERVO_SAYISI = 8;

struct ServoKaydi {
    int pin;
    Servo servo;
};

inline ServoKaydi* servo_kayitlari() {
    static ServoKaydi k[SERVO_SAYISI];
    static bool hazir = false;
    if (!hazir) {
        for (int i = 0; i < SERVO_SAYISI; ++i) k[i].pin = -1;
        hazir = true;
    }
    return k;
}

inline Servo* servo_bul(tam pin) {
    ServoKaydi* k = servo_kayitlari();
    for (int i = 0; i < SERVO_SAYISI; ++i)
        if (k[i].pin == pin) return &k[i].servo;
    return 0;
}

inline void servo_bagla(tam pin) {
    if (servo_bul(pin)) return;
    ServoKaydi* k = servo_kayitlari();
    for (int i = 0; i < SERVO_SAYISI; ++i) {
        if (k[i].pin < 0) {
            k[i].pin = (int)pin;
            k[i].servo.attach((int)pin);
            return;
        }
    }
    hata("En fazla 8 servo bağlanabilir.");
}

inline void servo_yaz(tam pin, tam aci) {
    Servo* s = servo_bul(pin);
    if (!s) {
        servo_bagla(pin);
        s = servo_bul(pin);
    }
    s->write((int)aci);
}

}  // namespace ekin
