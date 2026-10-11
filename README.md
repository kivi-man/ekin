# Ekin — Kullanım Kitapçığı

**Ekin**, Türkçenin eklemeli yapısı üzerine kurulmuş bir programlama dilidir. Aynı kaynak kod iki şekilde çalışır:

| Sürüm | Komut | Ne yapar |
|---|---|---|
| **Yorumlanan** | `ekin çalıştır dosya.ekin` | Kodu hemen çalıştırır. Derleyici gerekmez. Arduino komutlarını benzetimle, grafiği ve 3B'yi kurulum gerektirmeden çizer. |
| **Derlenen** | `ekin derle dosya.ekin` | Kodu okunabilir **C++**'a çevirir ve derler. C++ hızında çalışır. PC (Windows/macOS/Linux) ve **Arduino** (Uno, Nano, Mega, ESP32, ESP8266…) hedeflenebilir. |

```ekin
kullan arduino

kurulum:
    13'ü çıkış_yap

döngü:
    13'ü yak
    500 bekle
    13'ü söndür
    500 bekle
```

Bu program PC'de `ekin çalıştır` ile benzetim olarak çalışır, `ekin arduino --port COM3 --yükle` ile karta yüklenir.

---

## İçindekiler

1. [Kurulum](#1-kurulum)
2. [İlk program](#2-ilk-program)
3. [Dilin temelleri](#3-dilin-temelleri)
4. [Türkçe ek yapısı](#4-türkçe-ek-yapısı)
5. [Koşullar ve döngüler](#5-koşullar-ve-döngüler)
6. [İşlevler](#6-işlevler)
7. [Listeler](#7-listeler)
8. [Yapılar](#8-yapılar)
9. [Modüller ve komutlar](#9-modüller-ve-komutlar)
10. [Arduino](#10-arduino)
11. [Grafik, tuval ve OpenGL](#11-grafik-tuval-ve-opengl)
12. [C++ ile birlikte çalışma](#12-c-ile-birlikte-çalışma)
13. [Kendi modülünüzü yazmak](#13-kendi-modülünüzü-yazmak)
14. [Komut satırı başvurusu](#14-komut-satırı-başvurusu)
15. [Kurallar: iki sürüm neden aynı sonucu verir](#15-kurallar-iki-sürüm-neden-aynı-sonucu-verir)
16. [Platformlar ve yeni hedef eklemek (PS3 dahil)](#16-platformlar-ve-yeni-hedef-eklemek)
17. [Proje yapısı ve testler](#17-proje-yapısı-ve-testler)
18. [Sık karşılaşılan hatalar](#18-sık-karşılaşılan-hatalar)

---

## 1. Kurulum

**Gerekli:** Python 3.8 veya üstü. Yorumlayıcı başka bir şey istemez; grafik penceresi Python ile gelen tkinter'ı kullanır.

```bash
python ekin.py sürüm
```

Her yerden yalnızca `ekin` yazabilmek için:

- **Windows:** Bu klasörü PATH'e ekleyin. `ekin.bat` kısayolu hazırdır.
- **macOS / Linux:** `chmod +x ekin.sh`, ardından `ln -s "$(pwd)/ekin.sh" ~/.local/bin/ekin` komutunu çalıştırın.

Bu kitapçıktaki komutlar `ekin ...` biçiminde yazılmıştır. Kısayolu kurmadıysanız `python ekin.py ...` yazın.

### Derlenen sürüm için (isteğe bağlı)

| Ne için | Gerekli | Kurulum |
|---|---|---|
| PC programı | C++17 derleyicisi | **Windows:** Visual Studio (C++ iş yükü) ya da Build Tools kuruluysa **kendiliğinden bulunur**; ya da [w64devkit](https://github.com/skeeto/w64devkit) / MSYS2 (`pacman -S mingw-w64-ucrt-x86_64-gcc`) · **macOS:** `xcode-select --install` · **Linux:** `sudo apt install g++` |
| Grafik / OpenGL | [raylib](https://www.raylib.com) 4.x–6.x | **Windows:** [sürüm sayfasından](https://github.com/raysan5/raylib/releases) Visual Studio için `raylib-*_win64_msvc16.zip`, g++ için `raylib-*_win64_mingw-w64.zip` paketini `C:\raylib` klasörüne açın (`C:\raylib\include`, `C:\raylib\lib`); Ekin orayı kendiliğinden bulur. Başka bir klasör için `RAYLIB_YOL` tanımlayın · **macOS:** `brew install raylib` · **Linux:** `sudo apt install libraylib-dev` ya da kaynaktan derleyin |
| Arduino | Arduino IDE 2 ya da `arduino-cli` | Arduino IDE kuruluysa içindeki `arduino-cli` kendiliğinden bulunur |

Derleyiciyi elle seçmek için `EKIN_CXX` ortam değişkenini kullanın, ör. `EKIN_CXX=clang++`.

---

## 2. İlk program

`merhaba.ekin`:

```ekin
yaz "Merhaba, dünya!"
ad = sor "Adın ne? "
yaz "Hoş geldin {ad}!"
```

```bash
ekin çalıştır merhaba.ekin            # yorumlayıcı
ekin derle merhaba.ekin --çalıştır    # C++'a çevir, derle, çalıştır
ekin cpp merhaba.ekin                 # üretilen C++ kodunu göster
```

`ornekler/` klasöründe çalışan örnekler bulunur:

| Dosya | Konu |
|---|---|
| `01_merhaba.ekin` | Yazma, metin içinde ifade, Türkçe büyük/küçük harf |
| `02_temeller.ekin` | Değişken, koşul, döngü, işlev, liste, yapı |
| `03_ekler.ekin` | Türkçe ek yapısının tüm biçimleri |
| `arduino/01…05` | LED, düğme ve kesme, sensör, servo ve ses, LCD (C++ kütüphanesi) |
| `grafik/01…04` | Tuval resmi, zıplayan toplar, yılan oyunu, OpenGL 3B sahne |
| `kutuphane/geometri.ekin` | Ekin'de yazıp C++ kütüphanesi üretmek |
| `kendi_modulum/` | Kendi modülünüzü (Python + C++) yazmak |
| `coklu_dosya/` | Programı birden çok dosyaya bölmek |

---

## 3. Dilin temelleri

### Satırlar, yorumlar, girinti

- Her satıra bir komut yazılır. Noktalı virgül yoktur.
- `#` işaretinden sonrası yorumdur.
- Bloklar `:` ile başlar ve **girintiyle** belirlenir (4 boşluk önerilir).
- Tek komutluk blok aynı satıra yazılabilir: `x > 5 ise: yaz x`

### Değişkenler ve tipler

Tip yazmak gerekmez; derleyici tipi kendisi bulur. İsterseniz yazabilirsiniz.

```ekin
yaş = 30                    # tam
boy = 1.75                  # ondalık
ad = "Ayşe"                 # metin
evli = yanlış               # mantık (doğru / yanlış)
notlar = [90, 75, 60]       # liste[tam]
r = renk(255, 128, 0)       # renk

sayaç: tam = 0              # tipi açıkça yazmak
isimler: liste[metin] = []  # boş listenin tipi
```

| Tip | C++ (PC) | C++ (Arduino) | Örnek |
|---|---|---|---|
| `tam` | `int64_t` | `long` (32 bit) | `42`, `0xFF`, `0b1010`, `1_000_000` |
| `ondalık` | `double` | `double` | `3.14`, `1e-3` |
| `metin` | `std::string` (UTF-8) | `String` | `"çay"` |
| `mantık` | `bool` | `bool` | `doğru`, `yanlış` |
| `liste[T]` | `std::vector<T>` | Ekin'in küçük dizisi | `[1, 2, 3]` |
| `renk` | `ekin::Renk` | `ekin::Renk` | `KIRMIZI`, `renk(0, 200, 80)` |
| yapı adı | `struct` | `struct` | `Nokta(1, 2)` |

> **Kural:** Bir değişken tek bir tipte değer tutar. Tamsayıdan ondalığa geçiş serbesttir. `x = 5` dedikten sonra `x = "beş"` hata verir; iki sürümde de aynı hata.

### İşleçler

| İşleç | Anlam | Not |
|---|---|---|
| `+ - *` | toplama, çıkarma, çarpma | `"a" + 5` → `"a5"`, `"-" * 3` → `"---"`, `[1] + [2]` → `[1, 2]` |
| `/` | bölme | **Her zaman ondalık:** `7 / 2` → `3.5` |
| `//` | tam bölme (aşağı yuvarlar) | `-7 // 2` → `-4` |
| `%` | mod (sonuç bölenin işaretini alır) | `-7 % 3` → `2` |
| `**` | üs | `2 ** 10` → `1024` |
| `== != < > <= >=` | karşılaştırma | Metinler ve listeler de karşılaştırılabilir |
| `ve`, `veya`, `değil` | mantık | `x > 0 ve değil bitti` |
| `+= -= *= /= //= %= **=` | birleşik atama | |

### Metinler

```ekin
ad = "Deniz"
yaz "Merhaba {ad}, adın {uzunluk(ad)} harfli."      # { } içine her ifade yazılabilir
yaz "Süslü parantez: {{ }}"                          # {{ ve }} -> { }
yaz "satır1\nsatır2\t(sekme)  \"tırnak\""
```

Metin işlemleri Türkçe kurallarına uyar: `büyüt("istanbul")` → `İSTANBUL`, `küçült("IŞIK")` → `ışık`. `uzunluk("çğıöşü")` sonucu 6'dır, bayt değil harf sayılır.

### Türkçe klavyesi olmayanlar için

Tüm anahtar sözcüklerin ve yerleşik komutların ASCII yazımı da geçerlidir: `eger`, `degilse`, `icin`, `islev`, `don`, `dogru`, `yanlis`, `kucult`, `cizgi`, `buyut`… Kendi değişken adlarınızda ise Türkçe harf de kullanabilirsiniz, ASCII de; ikisi farklı ad sayılır.

---

## 4. Türkçe ek yapısı

Ekin'in temel fikri şudur: **Hal ekleri bir değerin cümledeki görevini söyler.** Bu yüzden argümanların sırası serbesttir ve eylem (işlev adı) Türkçede olduğu gibi cümlenin sonuna gelebilir.

| Ek | Hâl | Soru | Örnek |
|---|---|---|---|
| `-ı -i -u -ü` (`-yı`…) | belirtme | neyi? | `liste'yi`, `13'ü` |
| `-a -e` (`-ya -ye`) | yönelme | neye? | `liste'ye`, `10'a` |
| `-da -de -ta -te` (`-daki`…) | bulunma | nerede? | `liste'de`, `metin'deki` |
| `-dan -den -tan -ten` | ayrılma | nereden? | `0'dan`, `liste'den` |
| `-ın -in -un -ün` (`-nın`…) | ilgi | kimin? | `liste'nin`, `ad'ın` |
| `-la -le` (`-yla -yle`) | vasıta | neyle? | `","'le`, `koşul'la` |

### Üç cümle biçimi

```ekin
ekle(5, sayılar)            # 1. klasik çağrı (parantez, işlev adına BİTİŞİK yazılır)
5'i sayılar'a ekle          # 2. eylem sonda (Türkçe cümle)
sayılar'a 5'i ekle          #    sıra serbest: ekler görevi belirler
yaz "merhaba", ad           # 3. eylem başta (komut biçimi), argümanlar virgülle
```

### Kesme işaretli ve işaretsiz yazım

- **Kesme işaretiyle** (`liste'ye`, `13'ü`, `"metin"'i`) her sözcük ek alabilir. `'` ve `’` aynıdır.
- **Kesme işaretsiz** (`listeye`, `meyvelerden`, `kitabın`) yazımda Ekin, programda **tanımlı** bir adın kökünü kendisi bulur:
  - Ünlü uyumu denetlenir: `tone` bir C++ adı olarak kalır, `ton` + `e` diye okunmaz.
  - Ünsüz yumuşaması tanınır: `kitabı` → `kitap`, `rengi` → `renk`, `sayacı` → `sayaç`.

### İlgi + iyelik: "x'in y'si"

`A'nın B'si` yazımı `B(A)` anlamına gelir. A bir yapıysa ve B onun alanıysa `A.B` olur.

```ekin
yaz sayılar'ın toplamı          # topla(sayılar)
yaz sayılar'ın en_büyüğü         # en_büyük(sayılar)
yaz kitabın uzunluğu             # uzunluk(kitap)
yaz mesaj'ın harflerinin uzunluğu  # uzunluk(harfler(mesaj)) - zincirlenebilir
yaz nokta'nın x'i                # nokta.x
```

Bazı komutların ad hâlleri de tanımlıdır: `toplam` → `topla`, `çarpım` → `çarp`, `sıralı` → `sırala`.

### Kendi işlevlerinizde ekler

Parametreye ek yazarak rolünü belirleyin:

```ekin
işlev taşı(eşya'yı, nereden'den, nereye'ye):
    yaz "{eşya}: {nereden} -> {nereye}"

"kutu"'yu "salon"'dan "mutfak"'a taşı
"mutfak"'a "salon"'dan "masa"'yı taşı      # aynı anlam, farklı sıra
taşı("kalem", "çanta", "masa")             # klasik çağrı da çalışır
```

Ek taşıyan argüman aynı ekli parametreye gider; eksiz argümanlar kalan yerleri soldan sağa doldurur.

### Parantez kuralı

İşlev çağrısında parantez işlev adına **bitişik** yazılır: `kare(5)`. Araya boşluk girerse komut biçimi anlaşılır: `yaz (a + b) * 2` ifadesi `yaz((a + b) * 2)` demektir.

---

## 5. Koşullar ve döngüler

### Koşul

```ekin
eğer not_ >= 85:
    yaz "pekiyi"
değilse eğer not_ >= 70:
    yaz "iyi"
değilse:
    yaz "geçer"

# Türkçe sıralı biçim: "koşul ise"
not_ >= 85 ise:
    yaz "pekiyi"
değilse not_ >= 70 ise:
    yaz "iyi"
yoksa:
    yaz "geçer"
```

`değilse` ve `yoksa` aynı anlamdadır.

### Döngüler

```ekin
için i 1'den 5'e:              # 1 2 3 4 5   (İKİ UÇ DA DAHİL)
için i 0'dan 100'e kadar 10 adımla:
için i 10'dan 1'e -1 adımla:    # geri sayım: NEGATİF adım
için x liste'de:               # her öğe için (aşağıdakiyle aynı)
her x liste'de:
her harf "merhaba"'da:          # metnin harfleri
5 kez tekrarla:                # ya da: tekrarla 5 kez:
x < 10 iken:                   # ya da: iken x < 10:
sürekli:                       # sonsuz döngü (kır ile çıkılır)
```

- `kır` döngüden çıkar, `devam` sonraki tura geçer.
- Aralık döngüsünde yön **adımın işaretinden** gelir; varsayılan adım +1'dir. `0'dan n-1'e` yazımı n = 0 iken hiç çalışmaz. Bu güvenli bir davranıştır.
- Döngü değişkeni işlev içindeyse yereldir.

---

## 6. İşlevler

```ekin
işlev kare(x):
    dön x * x

işlev selamla(ad, ünvan = "Sayın"):          # varsayılan değer
    dön "{ünvan} {ad}"

işlev ortalama_al(a: ondalık, b: ondalık) -> ondalık:   # tipler isteğe bağlı
    dön (a + b) / 2

yaz kare(7), selamla("Ali"), ortalama_al(3, 4)
```

- Tipler yazılmazsa çağrıldıkları yerden bulunur (tip çıkarımı).
- Değer döndürmeyen işlev `dön` ile erken bitirilebilir.
- Parametresiz işlev yalnızca adıyla çağrılabilir: `temizle_ekran`.

**Lambda (adsız işlev):** `x -> x * 2`, `(a, b) -> a + b`

```ekin
çiftler = süz(sayılar, x -> x % 2 == 0)
kareler = eşle(sayılar, x -> x * x)
kökler  = eşle(sayılar, karekök)          # işlev adı da verilebilir
```

---

## 7. Listeler

```ekin
sayılar = [5, 3, 8]
yaz sayılar[0]                    # ilk öğe (sıra 0'dan başlar)
sayılar[1] = 30
4'ü sayılar'a ekle                # sona ekle
sayılar'dan 0'ı sil               # 0. sıradaki öğeyi sil (silineni döndürür)
8'i sayılar'dan çıkar             # 8 değerini çıkar
yaz uzunluk(sayılar), sırala(sayılar), sayılar'ın toplamı
matris = [[1, 2], [3, 4]]
yaz matris[1][0]
```

Liste komutları: `ekle, çıkar, sil, araya_ekle, içinde, sırala, ters_sırala, karıştır, topla, çarp, ortalama, temizle, dilim, süz, eşle, hepsi, biri, ilk, son, doldur, kopya, bul, say, ters, uzunluk, en_büyük, en_küçük, aralık, birleştir` (bkz. [KOMUTLAR.md](KOMUTLAR.md)).

> **Değer semantiği:** Listeler ve yapılar **kopyalanarak** atanır, C++'taki gibi. `b = a` yaptıktan sonra `b` değişirse `a` değişmez. İşleve verilen liste de kopyadır.

---

## 8. Yapılar

```ekin
yapı Nokta:
    x = 0.0
    y = 0.0

    işlev uzaklık(öbür):
        dön karekök((x - öbür.x) ** 2 + (y - öbür.y) ** 2)

    işlev taşı(dx, dy):
        x += dx                 # alanlara doğrudan (ya da bu.x ile) erişilir
        y += dy

a = Nokta(3.0, 4.0)             # alan sırasıyla değer verilir
b = Nokta()                     # varsayılan değerler
a.taşı(1, 1)
yaz a, a.uzaklık(b), a == b     # yazdırma ve karşılaştırma hazırdır

yapı Kişi: ad, yaş              # kısa biçim (tipler kullanımdan bulunur)
```

### Sabitler

```ekin
sabit KAT = 3
sabit SELAM = "Merhaba"
```

### Kapsam kuralı

En dışta atanan değişkenler **küreseldir**. İşlevler bunları okuyabilir ve değiştirebilir. İşlev içinde ilk kez atanan değişken ise **yereldir**.

---

## 9. Modüller ve komutlar

Komutlar modüllerde toplanır. Beşi kendiliğinden yüklenir; diğerleri `kullan` ile eklenir.

| Modül | Komut | Yükleme | Hedef | İçerik |
|---|---|---|---|---|
| `temel` | 15 | otomatik | hepsi | `yaz`, `sor`, `uzunluk`, dönüşümler, `aralık` |
| `matematik` | 33 | otomatik | hepsi | `karekök`, trigonometri, `yuvarla`, `rastgele`, `ölçekle`, `asal_mı`, `PI` |
| `metin` | 20 | otomatik | hepsi | `büyüt`, `parçala`, `birleştir`, `değiştir`, `bul`, `harfler` |
| `liste` | 21 | otomatik | hepsi | `ekle`, `sırala`, `süz`, `eşle`, `topla`, `ortalama` |
| `zaman` | 14 | otomatik | hepsi | `bekle`, `milisaniye`, `saat`, `tarih` |
| `arduino` | 32 | `kullan arduino` | Arduino | pinler, analog, PWM, kesme, ton, seri port, servo, EEPROM |
| `grafik` | 28 | `kullan grafik` | PC | pencere, şekiller, yazı, fare, klavye, 19 renk, tuş sabitleri |
| `opengl` | 21 | `kullan opengl` | PC | 3B sahne, kamera, küp/küre/silindir, `gl_döndür`, `gl_köşe` |
| `dosya` | 6 | `kullan dosya` | PC | dosya okuma ve yazma |
| `sistem` | 4 | `kullan sistem` | PC | komut çalıştırma, ortam değişkeni, argümanlar |

**Toplam 195 komut.** Tam liste için [KOMUTLAR.md](KOMUTLAR.md) dosyasına bakın ya da terminalde:

```bash
ekin modüller            # özet
ekin modüller grafik     # bir modülün komutları ve örnekleri
ekin modüller --md       # KOMUTLAR.md dosyasını yeniden üretir
```

Diğer `kullan` biçimleri:

```ekin
kullan grafik, opengl         # birden çok modül
kullan "araclar.ekin"         # başka bir Ekin dosyası (programı bölmek için)
kullan <Servo.h>              # C++ başlığı (derlenen sürüm)
```

---

## 10. Arduino

### Program yapısı

```ekin
kullan arduino

LED = 13          # en dışta atanan değişkenler küreseldir
sayaç = 0

kurulum:          # setup(): bir kez çalışır
    LED'i çıkış_yap
    seri_başlat 9600

döngü:            # loop(): sürekli tekrarlanır
    LED'i tersle
    sayaç += 1
    yaz "tur {sayaç}"
    1000 bekle
```

### PC'de benzetim (kart takmadan deneme)

```bash
ekin çalıştır led.ekin --tur 5        # döngü bloğunu 5 kez çalıştır
ekin çalıştır led.ekin --hızlı        # bekle komutlarını atla
```

Benzetim, pin değişikliklerini ekrana yazar (`[arduino] pin 13 = YÜKSEK`). Sensörden okunacak değeri `sim_ayarla(A0, 800)` ile verirsiniz; bu komut kartta etkisizdir.

### Karta yükleme

```bash
ekin arduino led.ekin                               # derle (varsayılan kart: Uno)
ekin arduino led.ekin --portlar                     # bağlı kartları listele
ekin arduino led.ekin --port COM3 --yükle           # derle ve yükle
ekin arduino led.ekin --kart arduino:avr:nano --port /dev/ttyUSB0 --yükle
ekin arduino led.ekin --kart esp32:esp32:esp32      # ESP32
```

Ekin, `derleme/<ad>/` klasöründe bir Arduino taslağı (sketch) oluşturur. Bu taslağı Arduino IDE ile de açabilirsiniz.

### Arduino'nun tüm özellikleri

1. **Türkçe komutlar:** `yak, söndür, tersle, dijital_yaz/oku, analog_yaz/oku, pin_modu, çıkış_yap, giriş_yap, dirençli_giriş_yap, basılı_mı, ton, ton_durdur, darbe_oku, kaydırarak_gönder/al, kesme_bağla/ayır, kesmeleri_kapat/aç, seri_başlat, seri_var, seri_oku, seri_satır_oku, seri_bayt_yaz, servo_bağla, servo_yaz, eeprom_oku/yaz, analog_referans, bayt` ve sabitler `YÜKSEK, DÜŞÜK, GİRİŞ, ÇIKIŞ, GİRİŞ_DİRENÇLİ, DAHİLİ_LED, A0…A7, YÜKSELEN, DÜŞEN, DEĞİŞEN`.
2. **Arduino/C++ adları doğrudan:** Ekin'de tanımlı olmayan her ad C++'a olduğu gibi aktarılır: `digitalWrite(13, HIGH)`, `Serial.println(x)`, `millis()`.
3. **Her kütüphane:** `kullan <Kütüphane.h>` yazın. C++ nesneleri kurucu argümanlarıyla oluşturulur: `lcd = LiquidCrystal(12, 11, 5, 4, 3, 2)`.
4. **Türkçe ad verme:** `dış işlev ekrana_yaz(ekran, metin'i) = "{0}.print({1})"`
5. **Ham C++:** `cpp:` bloğunun içi olduğu gibi aktarılır.

Ayrıntılı örnek: `ornekler/arduino/05_cpp_kutuphanesi.ekin`.

Kütüphane fonksiyonlarına geçen sayılar `long` tipindedir, çünkü Ekin'in `tam` tipi Arduino'da `long` olarak derlenir. Bir C++ işlevinin aynı adla birden çok sürümü varsa derleyici `ambiguous` (belirsiz) hatası verir. Örneğin `Wire.beginTransmission(uint8_t)` ile `Wire.beginTransmission(int)` böyledir. Bu durumda değeri `bayt(...)` ile çevirin:

```
kullan <Wire.h>
için adres 1'den 126'ya:
    Wire.beginTransmission(bayt(adres))
    sonuç = Wire.endTransmission()
    sonuç == 0 ise: yaz "Cihaz bulundu:", adres
```

Başka bir tip gerekirse kendiniz tanımlayabilirsiniz: `dış işlev kısa(x) -> tam = "(int)({0})"`. Ekin bu hatayı gördüğünde aynı çözümü kendisi de önerir.

**Notlar:**

- `kesme_bağla` ile verilen işlevin değiştirdiği küresel sayılar otomatik olarak `volatile` yapılır.
- Arduino Uno'da 2 KB RAM vardır; büyük listelerden kaçının. `tam` 32 bittir.
- Kurulu olmayan kütüphane için Ekin kurulum komutunu önerir: `arduino-cli lib install "Servo"`.

---

## 11. Grafik, tuval ve OpenGL

### 2B tuval

```ekin
kullan grafik

pencere_aç 800, 600, "Oyunum"
x = 0.0

her_karede:                      # saniyede 60 kez çalışır
    arkaplan SİYAH               # tuvali temizler
    daire x, 300, 30, KIRMIZI
    yazı "x = {yuvarla(x)}", 10, 10, 24, BEYAZ
    tuş_basılı(TUŞ_SAĞ) ise: x += 5
    fare_tıklandı() ise: x = ondalık(fare_x())
```

- **Tuval mantığı:** Çizilen her şey ekranda kalır, `arkaplan` tuvali temizler. `her_karede:` bloğu olmayan program bir kez çizer ve pencere kapanana kadar bekler.
- **Şekiller:** `daire, daire_çerçeve, elips, dikdörtgen, dikdörtgen_çerçeve, çizgi, üçgen, nokta, yazı`. Renk verilmezse `renk_seç` ile seçilen renk kullanılır. `kalınlık` çizgi kalınlığını ayarlar.
- **Girdi:** `fare_x, fare_y, fare_basılı, fare_tıklandı, tuş_basılı, tuşa_basıldı` ve `TUŞ_SOL, TUŞ_SAĞ, TUŞ_YUKARI, TUŞ_AŞAĞI, TUŞ_BOŞLUK, TUŞ_ENTER, TUŞ_ESC, TUŞ_A…TUŞ_Z, TUŞ_0…TUŞ_9`.
- **Zaman:** `kare_hızı(30)`, `geçen_süre()`, `kare_sayısı()`.
- **Renkler:** `SİYAH, BEYAZ, KIRMIZI, YEŞİL, MAVİ, SARI, TURUNCU, MOR, PEMBE, KAHVERENGİ, GRİ, AÇIK_GRİ, KOYU_GRİ, LACİVERT, TURKUAZ, ALTIN, GÖK_MAVİSİ, KOYU_YEŞİL, BORDO, SAYDAM`, `renk(k, y, m, saydamlık?)`, `rastgele_renk()`.
- Yazılardaki Türkçe harfler iki sürümde de desteklenir.

### 3B ve OpenGL

```ekin
kullan opengl                    # grafik modülünü de yükler

pencere_aç 800, 600, "3B"
kamera 7, 6, 9, 0, 1, 0          # göz (x, y, z) ve bakılan nokta
açı = 0.0

her_karede:
    arkaplan KOYU_GRİ
    sahne_başla
    ızgara 12, 1
    gl_kaydet
    gl_döndür açı, 0, 1, 0       # glRotatef
    küp 0, 1, 0, 2, TURUNCU
    gl_geri
    gl_başla GL_ÜÇGENLER         # glBegin
    gl_renk KIRMIZI
    gl_köşe -1, 0, 3
    gl_köşe 1, 0, 3
    gl_köşe 0, 2, 3
    gl_bitir                     # glEnd
    sahne_bitir
    açı += 1
```

| | Yorumlayıcı | Derlenen |
|---|---|---|
| 2B | tkinter (kurulum gerekmez) | raylib (OpenGL) |
| 3B | Yazılımsal 3B çizici (önizleme kalitesi) | Gerçek OpenGL (raylib `rlgl`: OpenGL 1.1/3.3/ES2) |
| Derinlik | Yüzler uzaktan yakına sıralanır (ressam algoritması); büyük yüzler küçük parçalara bölünür | Derinlik tamponu (piksel kadar doğru) |
| Köşe renkleri | Renk geçişi, yüz küçük parçalara bölünerek taklit edilir | Gerçek renk geçişi |
| Hız | Basit sahnelerde akıcı (≈15–20 kare/sn) | Ekran kartı hızında (60 kare/sn) |

Tüm komutları bir arada gösteren sahne: `ornekler/grafik/05_opengl_ozellikleri.ekin`.

`gl_başla` ile çizilen yüzler iki taraftan da görünür (arka yüz ayıklama sahne boyunca kapalıdır). Hazır cisimlerin (küp, küre…) arkada kalan yüzleri iki sürümde de görünmez.

---

## 12. C++ ile birlikte çalışma

### Ekin → C++ kodu

`ekin cpp dosya.ekin` okunabilir C++ üretir. Türkçe adlar ASCII'ye çevrilir: `sayı` → `sayi`, `uzaklık` → `uzaklik`. C++ ile çakışan adlara `_` eklenir: `int` → `int_`.

### Ekin → C++ kütüphanesi

```bash
ekin kütüphane ornekler/kutuphane/geometri.ekin
```

Çıktı: `geometri.hpp` (+ `ekin.hpp`). Herhangi bir C++17 projesinde şöyle kullanılır:

```cpp
#include "geometri.hpp"
ekin::Liste<geometri::Nokta> kare = {{0, 0}, {4, 0}, {4, 3}, {0, 3}};
double a = geometri::alan(kare);          // Ekin'de yazılmış işlev
```

### C++ kütüphanesi → Ekin

```ekin
kullan <vector>                                   # başlık
dış işlev karekök_al(x) -> ondalık = "std::sqrt({0})"   # Türkçe ad + şablon
dış sabit EN_BÜYÜK_TAM -> tam = "INT64_MAX"
cpp:
    // olduğu gibi C++ (en dışta: bildirimler; işlev içinde: komutlar)
    static int sayac_cpp = 0;
```

Şablonda `{0}`, `{1}`… argümanları, `{*}` tüm argümanları gösterir. Yorumlayıcı `dış` işlevleri ve `cpp:` bloklarını çalıştıramaz; bunlar derlenen sürüm içindir.

### Çalışma zamanı kütüphanesi

`calisma_zamani/ekin.hpp` tek başına da kullanılabilir. Türkçe uyumlu metin işlemleri (`ekin::buyut`, `ekin::uzunluk`) ve liste yardımcıları (`ekin::suz`, `ekin::esle`) içerir. PC'de C++11+ ile, Arduino'da standart kütüphane olmadan derlenir.

---

## 13. Kendi modülünüzü yazmak

Bir modül, `moduller/` klasöründeki bir Python dosyasıdır. Ekin şu klasörlerde arar:

1. `.ekin` dosyasının yanındaki `moduller/` klasörü
2. `EKIN_YOL` ortam değişkenindeki klasörler
3. Ekin'in kendi `moduller/` klasörü

Örnek (`ornekler/kendi_modulum/moduller/sicaklik.py`):

```python
from ekin.modul import Islev, Sabit, Modul

MODUL = Modul(
    "sicaklik",
    "Sıcaklık birimi dönüşümleri.",
    basliklar={"pc": ['"sicaklik.hpp"'], "arduino": ['"sicaklik.hpp"']},
    islevler=[
        Islev("fahrenhayta(santigrat'ı)",                 # imza: ekler = argüman rolleri
              py=lambda c: c * 9 / 5 + 32,                # yorumlayıcı
              cpp="sicaklik::fahrenhayta({0})",           # derleyici (PC + Arduino)
              donus="ondalık",
              aciklama="Santigratı Fahrenhayta çevirir.",
              ornek="100'ü fahrenhayta"),
    ],
    sabitler=[Sabit("MUTLAK_SIFIR", -273.15, "sicaklik::MUTLAK_SIFIR", tip="ondalık")],
)
```

Modülün yanındaki `sicaklik.hpp` C++ karşılığıdır. Derleyici bu dosyayı kendiliğinden bulur ve Arduino taslağına kopyalar. Kullanımı: `kullan sıcaklık` → `yaz 100'ü fahrenhayta`.

**`Islev` ayarları:**

| Ayar | Anlamı |
|---|---|
| imza | `"ad(p1'i, p2'ye, p3?, p4...)"`: ek = rol, `?` = isteğe bağlı, `...` = değişken sayıda |
| `py` | Python karşılığı (`None` ise yalnızca derlenen sürümde vardır) |
| `cpp` | C++ şablonu (`{0}`, `{*}`) ya da `lambda args, tipler: "..."` |
| `ino` | Arduino'ya özel şablon; `False` ise Arduino'da yoktur |
| `donus` | `"tam"`, `"metin"`, `"liste[tam]"`, `"$0"` (1. argümanın tipi), `"$0[]"` (1. argüman listesinin öğesi), ya da bir işlev |
| `lambda_param` | `{1: "$0[]"}`: 2. argüman lambda'dır, parametresi listenin öğe tipindedir |
| `daralt` | `{1: "liste[$0]"}`: boş bir listenin tipini kullanımdan bulur (ör. `ekle`) |
| `gerekir` | Ek C++ başlıkları (`"<Servo.h>"`) ya da `"seri"` |
| `takma` | Ad hâli takma adları: `["toplam"]` |

`Modul` ayarları: `hedefler` (`"py"`, `"pc"`, `"arduino"`), `basliklar`, `baglama` (bağlayıcı bayrakları), `bagimliliklar`, `py_bitis` (program bitince çalışacak kanca, ör. pencere döngüsü).

---

## 14. Komut satırı başvurusu

```
ekin çalıştır dosya.ekin [--tur N] [--kare N] [--hızlı] [--sessiz]
ekin derle    dosya.ekin [-o program] [--çalıştır] [--kare N] [--ayrıntılı]
ekin cpp      dosya.ekin [--hedef pc|arduino]
ekin arduino  dosya.ekin [--kart FQBN] [--port PORT] [--yükle] [--portlar]
ekin kütüphane dosya.ekin [-o klasör]
ekin etkileşimli
ekin modüller [ad] [--md]
ekin sürüm
```

| Seçenek | Anlamı |
|---|---|
| `--tur N` | `döngü:` bloğunu N kez çalıştır (benzetim) |
| `--kare N` | `her_karede:` bloğunu N kare sonra durdur (derlenen programda `--çalıştır` ile) |
| `--hızlı` | `bekle` komutlarını atla |
| `--sessiz` | Arduino benzetim iletilerini gizle |

| Ortam değişkeni | Anlamı |
|---|---|
| `EKIN_CXX` | C++ derleyicisi (ör. `clang++`, `g++-13`) |
| `RAYLIB_YOL` | raylib klasörü (içinde `include/` ve `lib/`; Windows'ta varsayılan `C:\raylib`) |
| `EKIN_KARE` | Derlenen grafik programı N kare çizip kapanır |
| `EKIN_GORUNTU` | Grafik programı kapanırken son kareyi bu PNG dosyasına kaydeder (iki sürümde de) |
| `EKIN_YOL` | Ek modül klasörleri |
| `EKIN_ARDUINO_CLI` | `arduino-cli` yolu |
| `EKIN_ARDUINO_KUTUPHANE` | Ek Arduino kütüphane klasörleri |

`etkileşimli` komutuyla Ekin'i satır satır deneyebilirsiniz. `:` ile biten satırdan sonra blok yazın ve boş satırla bitirin. Çıkmak için `çık` yazın.

---

## 15. Kurallar: iki sürüm neden aynı sonucu verir

Ekin'in yorumlayıcısı ile derleyicisi aynı anlam kurallarını uygular. Test paketi her örneğin iki sürümde **birebir aynı çıktı** verdiğini denetler.

| Kural | Açıklama |
|---|---|
| Tek tip | Bir değişken tek tipte değer tutar (`tam` → `ondalık` serbest). |
| Değer semantiği | Liste ve yapılar atamada, işleve verilirken ve `her` döngüsünde kopyalanır. |
| `/` | Her zaman ondalık böler; `//` aşağı yuvarlar; `%` bölenin işaretini alır. |
| Sayı yazımı | Ondalıklar 10 anlamlı basamakla yazılır (`0.1 + 0.2` → `0.3`). |
| Aralık | Uçlar dahil; yön adımın işaretinden; adım 0 hatadır. |
| Kapsam | En dışta atanan ad küreseldir; işlev içinde ilk atanan ad ve döngü değişkeni yereldir. |
| Sınır | Liste dışına erişim hata verir (Arduino'da hız için denetlenmez). |
| Değerlendirme sırası | Yorumlayıcı argümanları soldan sağa değerlendirir; C++ bunu garanti etmez. Aynı çağrının argümanlarında yan etkisi olan iki işlev kullanmayın (ör. `yaz say(), say()`); sonuçları önce değişkenlere atayın. |

**Yalnızca bir sürümde olanlar:**

- Yorumlayıcıda: Arduino benzetimi, `sim_ayarla`.
- Derlenen sürümde: C++ adları, `dış` tanımları, `cpp:` blokları ve `kullan <...>` ile eklenen kütüphaneler.

---

## 16. Platformlar ve yeni hedef eklemek

| Platform | Yorumlayıcı | Derlenen |
|---|---|---|
| Windows | ✔ | ✔ (MinGW/MSYS2, clang, MSVC) |
| macOS | ✔ | ✔ (clang; grafik için Homebrew raylib) |
| Linux | ✔ | ✔ (g++/clang; grafik için raylib) |
| Arduino AVR (Uno, Nano, Mega…) | benzetim | ✔ (`arduino:avr:*`) |
| ESP32 / ESP8266 | benzetim | ✔ (`esp32:esp32:*`, `esp8266:esp8266:*`) |
| PS3 | — | yol haritasında (aşağıya bakın) |

### Yeni bir hedef eklemek (ör. PS3)

Derleyici hedefi bir dizi kurala bağlar. Yeni bir platform için şu adımlar izlenir:

1. **Çalışma zamanı:** `calisma_zamani/ekin.hpp` dosyasına `#if defined(__PPU__)` gibi bir dal ekleyin: tip eşlemeleri (`tam`, `metin`), çıktı (`cikti_yaz`), zaman (`bekle`, `milisaniye`). PS3 için [PSL1GHT](https://github.com/ps3dev/PSL1GHT) araç zinciri (`ppu-g++`) standart C++ kütüphanesi sunduğundan PC dalı büyük ölçüde aynen kullanılabilir.
2. **Derleyici:** `ekin/derleyici.py` içinde hedef adını (`"ps3"`) ve giriş noktasını (`_giris_uret`) tanımlayın.
3. **İnşa:** `ekin/insa.py` dosyasına derleme komutunu ekleyin (`ppu-g++`, `make_self` ile `.self` paketleme).
4. **Modüller:** Destekleyen modüllerin `hedefler` kümesine `"ps3"` ekleyin. Grafik için raylib yerine RSX/`gcm` ya da tiny3D arka ucu yazılabilir. Arka uç, `ekin_grafik.hpp` içindeki işlevlerin (`daire`, `dikdortgen`, `calistir` …) aynı imzalarla yeniden yazılmasıdır.

Bu modüler yapı sayesinde dilin kendisi ve programlar değişmeden yeni platformlara taşınabilir.

---

## 17. Proje yapısı ve testler

```
ekin.py / ekin.bat / ekin.sh    komut satırı girişi
ekin/                           dilin kendisi (Python)
  ekler.py          Türkçe ek çözümleme (ünlü uyumu, ünsüz yumuşaması, iyelik)
  sozcukler.py      sözcük ayırıcı (lexer)
  ayristirici.py    ayrıştırıcı (parser) -> agac.py (sözdizim ağacı)
  yorumlayici.py    yorumlanan sürüm
  derleyici.py      derlenen sürüm: tip çıkarımı + C++ üretimi
  modul.py          modül sistemi
  insa.py           C++ derleyicisi ve Arduino (arduino-cli) sürücüsü
  tuval_tk.py       yorumlayıcının grafik arka ucu
  arac.py           komut satırı aracı
moduller/                       yerleşik modüller (temel, matematik, metin, liste,
                                zaman, arduino, grafik, opengl, dosya, sistem)
calisma_zamani/                 C++ çalışma zamanı (ekin.hpp, ekin_grafik.hpp,
                                ekin_opengl.hpp, ekin_dosya.hpp, ekin_servo.hpp)
ornekler/                       örnek programlar
testler/                        test paketi
KOMUTLAR.md                     195 komutun tam listesi
```

Testleri çalıştırmak için:

```bash
python -m unittest discover testler -v
```

- C++ derleyicisi varsa derlenen programların çıktısı yorumlayıcınınkiyle karşılaştırılır.
- `EKIN_ARDUINO_TEST=1` tanımlıysa Arduino örnekleri Uno için derlenir.
- `EKIN_GRAFIK_TEST=1` tanımlıysa grafik örnekleri gerçek raylib ile derlenir, pencere açıp birkaç kare çizer ve görüntüsü denetlenir.

---

## 18. Sık karşılaşılan hatalar

| İleti | Çözüm |
|---|---|
| `'yak' komutu 'arduino' modülünde` | Dosyanın başına `kullan arduino` yazın. |
| `Bloktan önce ':' bekleniyordu` | `eğer`, `için`, `işlev`… satırının sonuna `:` koyun. |
| `Bloğun içi girintili yazılmalı` | Bloğun satırlarını en az bir boşluk (önerilen 4) içeriden yazın. |
| `'ler' eki tanınmadı` | Kesme işaretinden sonra yalnızca hal ekleri kullanılır (bkz. bölüm 4). |
| `Bu cümle anlaşılamadı` | Eylem (işlev adı) cümlenin başında ya da sonunda olmalıdır: `yaz x` ya da `x'i yaz`. |
| `... tipinde kullanıldı, şimdi ... veriliyor` | Bir değişkene farklı tipte değer vermeyin; yeni bir ad kullanın. |
| `Listenin öğe tipi bulunamadı` | Boş listenin tipini yazın: `x: liste[tam] = []` |
| `C++ derleyicisi bulunamadı` | Bölüm 1'deki derleyiciyi kurun ya da `EKIN_CXX` tanımlayın. |
| `raylib bulunamadı` | raylib paketini `C:\raylib` klasörüne açın ya da `RAYLIB_YOL` tanımlayın (bölüm 1). |
| `LNK2019 ... __imp_...` (Visual Studio) | MinGW için hazırlanmış raylib paketi kullanılmış; `*_win64_msvc16` paketini kurun. |
| `'Servo' kütüphanesi kurulu değil` | `arduino-cli lib install "Servo"` |

---

*Ekin 0.1.0 · [MIT lisansı](LICENSE) ile dağıtılır: ticari işler dahil serbestçe kullanılabilir, değiştirilebilir ve dağıtılabilir.*
