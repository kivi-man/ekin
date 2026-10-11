# Ekin Komut Başvurusu

Bu dosya `ekin modüller --md` ile modül tanımlarından otomatik üretilir.

Toplam **194** komut.

Sütunlar: **Komut** (imzadaki ekler argümanın rolünü gösterir), **Döner**, **Açıklama**. Hedef: hangi sürümlerde kullanılabildiği (py = yorumlayıcı).

## arduino — `kullan arduino`

Arduino pinleri, seri port, kesmeler, ton, servo, EEPROM (yorumlayıcıda benzetim).  
Hedef: arduino, py

| Komut | Döner | Açıklama |
|---|---|---|
| `pin_modu(pin'i, kip'e)` | — | Pin kipini ayarlar (GİRİŞ, ÇIKIŞ, GİRİŞ_DİRENÇLİ).<br>örnek: `pin_modu(13, ÇIKIŞ)` |
| `çıkış_yap(pin'i)` | — | Pini çıkış yapar.<br>örnek: `13'ü çıkış_yap` |
| `giriş_yap(pin'i)` | — | Pini giriş yapar. |
| `dirençli_giriş_yap(pin'i)` | — | Pini dahili dirençli (pull-up) giriş yapar. |
| `yak(pin'i)` | — | Pini YÜKSEK yapar.<br>örnek: `13'ü yak  ¦  led'i yak` |
| `söndür(pin'i)` | — | Pini DÜŞÜK yapar.<br>örnek: `13'ü söndür` |
| `tersle(pin'i)` | — | Pinin durumunu tersine çevirir. |
| `dijital_yaz(pin'e, değer'i)` | — | Pine YÜKSEK/DÜŞÜK yazar.<br>örnek: `YÜKSEK'i 13'e dijital_yaz` |
| `dijital_oku(pin'i)` | tam | Pini okur (1 ya da 0). |
| `basılı_mı(pin'in)` | mantık | Dirençli girişe bağlı düğme basılıysa doğru. |
| `analog_oku(pin'i)` | tam | Analog değer okur (0-1023).<br>örnek: `ışık = analog_oku(A0)` |
| `analog_yaz(pin'e, değer'i)` | — | PWM yazar (0-255).<br>örnek: `128'i 9'a analog_yaz` |
| `analog_referans(tip'i)` | — | Analog referans gerilimini seçer. |
| `ton(pin'e, frekans'ı, süre?)` | — | Pinden ses çıkarır.<br>örnek: `ton(8, 440, 200)` |
| `ton_durdur(pin'i)` | — | Sesi durdurur. |
| `darbe_oku(pin'i, durum?, zaman_aşımı?)` | tam | Darbe süresini mikrosaniye olarak ölçer (ör. HC-SR04). |
| `kaydırarak_gönder(veri_pini, saat_pini, sıra, değer)` | — | Bir baytı bit bit gönderir (74HC595). |
| `kaydırarak_al(veri_pini, saat_pini, sıra)` | tam | Bir baytı bit bit okur. |
| `kesme_bağla(pin'e, işlev'i, kip'le?)` | — | Pin değişince işlevi çağırır.<br>örnek: `kesme_bağla(2, düğmeye_basıldı, DÜŞEN)` |
| `kesme_ayır(pin'i)` | — | Pin kesmesini kaldırır. |
| `kesmeleri_kapat()` | — | Tüm kesmeleri kapatır. |
| `kesmeleri_aç()` | — | Kesmeleri açar. |
| `seri_başlat(hız?)` | — | Seri portu başlatır.<br>örnek: `seri_başlat 115200` |
| `seri_var()` | mantık | Okunacak seri veri varsa doğru. |
| `seri_oku()` | tam | Seri porttan bir bayt okur (-1: veri yok). |
| `seri_satır_oku()` | metin | Seri porttan bir satır okur. |
| `seri_bayt_yaz(bayt'ı)` | — | Seri porta ham bayt yazar. |
| `servo_bağla(pin'e)` | — | Pine bir servo motor bağlar.<br>örnek: `9'a servo_bağla` |
| `servo_yaz(pin'e, açı'yı)` | — | Servoyu açıya (0-180) getirir.<br>örnek: `90'ı 9'a servo_yaz` |
| `eeprom_oku(adres'i)` | tam | Kalıcı bellekten bir bayt okur. |
| `eeprom_yaz(değer'i, adres'e)` | — | Kalıcı belleğe bir bayt yazar. |
| `sim_ayarla(pin'e, değer'i)` | — | (Yalnız yorumlayıcı) Benzetimde pinden okunacak değeri belirler; kartta etkisizdir.<br>örnek: `sim_ayarla(A0, 800)` |

Sabitler: `YÜKSEK`, `DÜŞÜK`, `GİRİŞ`, `ÇIKIŞ`, `GİRİŞ_DİRENÇLİ`, `DAHİLİ_LED`, `YÜKSELEN`, `DÜŞEN`, `DEĞİŞEN`, `LSB_ÖNCE`, `MSB_ÖNCE`, `A0`, `A1`, `A2`, `A3`, `A4`, `A5`, `A6`, `A7`

## dosya — `kullan dosya`

Dosya okuma ve yazma (yalnız PC).  
Hedef: pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `dosya_oku(yol'u)` | metin | Dosyanın tamamını metin olarak okur.<br>örnek: `içerik = dosya_oku "notlar.txt"` |
| `satırları_oku(yol'u)` | liste[metin] | Dosyayı satır listesi olarak okur. |
| `dosyaya_yaz(metin'i, yol'a)` | — | Metni dosyaya yazar (eskisinin üstüne).<br>örnek: `"merhaba"'yı "a.txt"'ye dosyaya_yaz` |
| `dosyaya_ekle(metin'i, yol'a)` | — | Metni dosyanın sonuna ekler. |
| `dosya_var(yol)` | mantık | Dosya varsa doğru. |
| `dosya_sil(yol'u)` | — | Dosyayı siler. |

## grafik — `kullan grafik`

Pencere, 2B tuval çizimi, fare ve klavye (raylib/OpenGL ile derlenir).  
Hedef: pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `pencere_aç(genişlik, yükseklik, başlık?)` | — | Çizim penceresi açar.<br>örnek: `pencere_aç 800, 600, "Oyunum"` |
| `pencere_kapat()` | — | Pencereyi kapatır. |
| `arkaplan(renk'i)` | — | Tuvali bir renkle temizler.<br>örnek: `arkaplan SİYAH` |
| `renk(kırmızı, yeşil, mavi, saydamlık?)` | renk | 0-255 değerlerinden renk.<br>örnek: `turuncu = renk(255, 128, 0)` |
| `rastgele_renk()` | renk | Rastgele parlak bir renk. |
| `renk_seç(renk'i)` | — | Renk verilmeyen çizimlerin rengini seçer. |
| `kalınlık(k)` | — | Çizgi ve çerçeve kalınlığı. |
| `daire(x, y, yarıçap, renk?)` | — | Dolu daire.<br>örnek: `daire 100, 100, 40, KIRMIZI` |
| `daire_çerçeve(x, y, yarıçap, renk?)` | — | İçi boş daire. |
| `elips(x, y, yatay_yarıçap, dikey_yarıçap, renk?)` | — | Dolu elips. |
| `dikdörtgen(x, y, genişlik, yükseklik, renk?)` | — | Dolu dikdörtgen (x, y sol üst köşe).<br>örnek: `dikdörtgen 10, 10, 200, 50, MAVİ` |
| `dikdörtgen_çerçeve(x, y, genişlik, yükseklik, renk?)` | — | İçi boş dikdörtgen. |
| `çizgi(x1, y1, x2, y2, renk?)` | — | Çizgi. |
| `üçgen(x1, y1, x2, y2, x3, y3, renk?)` | — | Dolu üçgen. |
| `nokta(x, y, renk?)` | — | Tek piksel. |
| `yazı(metin'i, x, y, boyut?, renk?)` | — | Tuvale yazı yazar (Türkçe harfler desteklenir).<br>örnek: `yazı "Puan: {puan}", 10, 10, 24, BEYAZ` |
| `yazı_genişliği(metin'in, boyut?)` | tam | Yazının piksel genişliği. |
| `kare_hızı(fps)` | — | Saniyedeki kare sayısı (varsayılan 60). |
| `fare_x()` | tam | Fare x konumu. |
| `fare_y()` | tam | Fare y konumu. |
| `fare_basılı()` | mantık | Sol fare tuşu basılı tutuluyorsa doğru. |
| `fare_tıklandı()` | mantık | Bu karede tıklandıysa doğru. |
| `tuş_basılı(tuş)` | mantık | Tuş basılı tutuluyorsa doğru.<br>örnek: `eğer tuş_basılı(TUŞ_SOL): x -= 5` |
| `tuşa_basıldı(tuş)` | mantık | Tuşa bu karede basıldıysa doğru. |
| `genişlik()` | tam | Pencere genişliği. |
| `yükseklik()` | tam | Pencere yüksekliği. |
| `geçen_süre()` | ondalık | Önceki kareden beri geçen saniye. |
| `kare_sayısı()` | tam | Şimdiye kadar çizilen kare sayısı. |

Sabitler: `SİYAH`, `BEYAZ`, `KIRMIZI`, `YEŞİL`, `MAVİ`, `SARI`, `TURUNCU`, `MOR`, `PEMBE`, `KAHVERENGİ`, `GRİ`, `AÇIK_GRİ`, `KOYU_GRİ`, `LACİVERT`, `TURKUAZ`, `ALTIN`, `GÖK_MAVİSİ`, `KOYU_YEŞİL`, `BORDO`, `SAYDAM`, `TUŞ_SOL`, `TUŞ_SAĞ`, `TUŞ_YUKARI`, `TUŞ_AŞAĞI`, `TUŞ_BOŞLUK`, `TUŞ_ENTER`, `TUŞ_ESC`, `TUŞ_SİL`, `TUŞ_TAB`, `TUŞ_SHIFT`, `TUŞ_CTRL`, `TUŞ_A`, `TUŞ_B`, `TUŞ_C`, `TUŞ_D`, `TUŞ_E`, `TUŞ_F`, `TUŞ_G`, `TUŞ_H`, `TUŞ_I`, `TUŞ_J`, `TUŞ_K`, `TUŞ_L`, `TUŞ_M`, `TUŞ_N`, `TUŞ_O`, `TUŞ_P`, `TUŞ_Q`, `TUŞ_R`, `TUŞ_S`, `TUŞ_T`, `TUŞ_U`, `TUŞ_V`, `TUŞ_W`, `TUŞ_X`, `TUŞ_Y`, `TUŞ_Z`, `TUŞ_0`, `TUŞ_1`, `TUŞ_2`, `TUŞ_3`, `TUŞ_4`, `TUŞ_5`, `TUŞ_6`, `TUŞ_7`, `TUŞ_8`, `TUŞ_9`

## liste (otomatik yüklenir)

Liste işlemleri.  
Hedef: arduino, pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `ekle(öğe'yi, liste'ye)` | — | Listenin sonuna öğe ekler.<br>örnek: `5'i sayılar'a ekle` |
| `çıkar(öğe'yi, liste'den)` | mantık | Öğenin ilk geçtiği yeri listeden çıkarır.<br>örnek: `5'i sayılar'dan çıkar` |
| `sil(liste'den, sıra'yı)` | (listenin öğesi) | Verilen sıradaki öğeyi siler ve döndürür.<br>örnek: `sayılar'dan 0'ı sil` |
| `araya_ekle(liste'ye, sıra, öğe'yi)` | — | Öğeyi verilen sıraya yerleştirir. |
| `içinde(öğe'yi, liste'de)` | mantık | Öğe listede varsa doğru.<br>örnek: `eğer içinde(3, sayılar): ...` |
| `sırala(liste'yi)` | (1. argümanın tipi) | Küçükten büyüğe sıralanmış yeni liste. |
| `ters_sırala(liste'yi)` | (1. argümanın tipi) | Büyükten küçüğe sıralanmış yeni liste. |
| `karıştır(liste'yi)` | (1. argümanın tipi) | Karıştırılmış yeni liste. |
| `topla(liste'yi)` | (listenin öğesi) | Liste öğelerinin toplamı.<br>örnek: `sayılar'ı topla` |
| `çarp(liste'yi)` | (listenin öğesi) | Liste öğelerinin çarpımı. |
| `ortalama(liste'nin)` | ondalık | Ortalama.<br>örnek: `notlar'ın ortalaması` |
| `temizle(liste'yi)` | — | Listeyi boşaltır. |
| `dilim(liste'den, baş, son)` | (1. argümanın tipi) | baş ile son (ikisi dahil) arasındaki öğeler. |
| `süz(liste'yi, koşul'la)` | (1. argümanın tipi) | Koşulu sağlayan öğelerden yeni liste.<br>örnek: `çiftler = süz(sayılar, x -> x % 2 == 0)` |
| `eşle(liste'yi, işlev'le)` | (argümana göre) | Her öğeye işlevi uygular.<br>örnek: `kareler = eşle(sayılar, x -> x * x)` |
| `hepsi(liste'nin, koşul'la)` | mantık | Tüm öğeler koşulu sağlıyorsa doğru. |
| `biri(liste'nin, koşul'la)` | mantık | En az bir öğe koşulu sağlıyorsa doğru. |
| `ilk(liste'nin)` | (listenin öğesi) | İlk öğe. |
| `son(liste'nin)` | (listenin öğesi) | Son öğe. |
| `doldur(adet, değer'le)` | (argümana göre) | Aynı değerden n tane içeren liste.<br>örnek: `doldur(5, 0)  ->  [0, 0, 0, 0, 0]` |
| `kopya(x'in)` | (1. argümanın tipi) | Listenin kopyası. |

## matematik (otomatik yüklenir)

Sayısal işlevler ve sabitler.  
Hedef: arduino, pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `karekök(x'in)` | ondalık | Karekök.<br>örnek: `karekök(16)  ¦  16'nın karekökü` |
| `mutlak(x'in)` | (argümana göre) | Mutlak değer. |
| `üs(taban, üs)` | (argümana göre) | Üs alma (a ** b ile aynı). |
| `yuvarla(x'i, basamak?)` | (argümana göre) | En yakın tam sayıya (ya da basamağa) yuvarlar. |
| `taban(x'in)` | tam | Aşağı yuvarlar. |
| `tavan(x'in)` | tam | Yukarı yuvarlar. |
| `sin(x)` | ondalık | Sinüs (radyan). |
| `cos(x)` | ondalık | Kosinüs (radyan). |
| `tan(x)` | ondalık | Tanjant (radyan). |
| `asin(x)` | ondalık | Ters sinüs. |
| `acos(x)` | ondalık | Ters kosinüs. |
| `atan(x)` | ondalık | Ters tanjant. |
| `atan2(y, x)` | ondalık | İki bağımsız değişkenli ters tanjant. |
| `log(x)` | ondalık | Doğal logaritma. |
| `log10(x)` | ondalık | 10 tabanında logaritma. |
| `üstel(x)` | ondalık | e üzeri x. |
| `derece(radyan)` | ondalık | Radyanı dereceye çevirir. |
| `radyan(derece)` | ondalık | Dereceyi radyana çevirir. |
| `hipotenüs(a, b)` | ondalık | Dik üçgenin hipotenüsü. |
| `en_büyük(değerler...)` | (argümana göre) | En büyük değer (sayılar ya da bir liste).<br>örnek: `en_büyük(3, 9, 4)  ¦  sayılar'ın en_büyüğü` |
| `en_küçük(değerler...)` | (argümana göre) | En küçük değer. |
| `sınırla(x'i, alt, üst)` | (argümana göre) | x'i alt ile üst arasında tutar. |
| `ölçekle(x'i, eski_alt, eski_üst, yeni_alt, yeni_üst)` | (argümana göre) | Bir aralıktaki değeri başka aralığa taşır (Arduino map).<br>örnek: `ölçekle(analog_oku(A0), 0, 1023, 0, 255)` |
| `rastgele(alt, üst)` | tam | alt ile üst arasında (ikisi dahil) rastgele tam sayı. |
| `rastgele_ondalık()` | ondalık | 0 ile 1 arasında rastgele ondalık sayı. |
| `rastgele_tohum(tohum)` | — | Rastgele sayı üretecini başlatır. |
| `işaret(x'in)` | tam | -1, 0 ya da 1. |
| `çift_mi(x)` | mantık | Sayı çiftse doğru. |
| `tek_mi(x)` | mantık | Sayı tekse doğru. |
| `asal_mı(x)` | mantık | Sayı asalsa doğru. |
| `faktöriyel(n'in)` | tam | n! |
| `ebob(a, b)` | tam | En büyük ortak bölen. |
| `ekok(a, b)` | tam | En küçük ortak kat. |

Sabitler: `PI`, `TAU`, `E`, `SONSUZ`

## metin (otomatik yüklenir)

Metin işlemleri (Türkçe büyük/küçük harf kurallarıyla).  
Hedef: arduino, pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `büyüt(metin'i)` | metin | Büyük harfe çevirir (i -> İ).<br>örnek: `"istanbul"'u büyüt  ->  "İSTANBUL"` |
| `küçült(metin'i)` | metin | Küçük harfe çevirir (I -> ı). |
| `kırp(metin'i)` | metin | Baştaki ve sondaki boşlukları siler. |
| `parçala(metin'i, ayraç'la?)` | liste[metin] | Metni ayraca göre parçalar (ayraç yoksa boşluklara göre).<br>örnek: `"a,b,c"'yi ","'le parçala  ->  ["a", "b", "c"]` |
| `birleştir(liste'yi, ayraç'la?)` | metin | Liste öğelerini aralarına ayraç koyarak birleştirir. |
| `içerir(kaynak, aranan'ı)` | mantık | Kaynak (metin ya da liste) arananı içeriyorsa doğru. |
| `bul(aranan'ı, kaynak'ta)` | tam | Arananın ilk konumu (yoksa -1). Metin ve listede çalışır.<br>örnek: `"dünya"'yı mesaj'da bul` |
| `değiştir(kaynak'ta, eski'yi, yeni'yle)` | metin | Metindeki tüm 'eski' parçaları 'yeni' yapar. |
| `başlar(metin, önek'le)` | mantık | Metin önekle başlıyorsa doğru. |
| `biter(metin, sonek'le)` | mantık | Metin sonekle bitiyorsa doğru. |
| `ters(x'i)` | (1. argümanın tipi) | Metni ya da listeyi ters çevirir. |
| `harf(metin'in, sıra)` | metin | Verilen sıradaki harf (0'dan başlar). |
| `alt_metin(metin'in, baş, uzunluk?)` | metin | Metnin bir parçası. |
| `sayı_mı(metin)` | mantık | Metin bir sayıysa doğru. |
| `karakter_kodu(harf'in)` | tam | İlk harfin Unicode kodu. |
| `koddan_karakter(kod)` | metin | Unicode kodundan harf. |
| `çoğalt(metin'i, kez)` | metin | Metni n kez yan yana yazar. |
| `harfler(metin'in)` | liste[metin] | Metnin harflerinden oluşan liste. |
| `satırlar(metin'in)` | liste[metin] | Metni satırlara böler. |
| `say(küme'de, öğe'yi)` | tam | Öğenin (metin ya da liste içinde) kaç kez geçtiği.<br>örnek: `sayılar'da 3'ü say` |

## opengl — `kullan opengl`

3B sahne, kamera, şekiller ve OpenGL tarzı köşe çizimi (rlgl/OpenGL ile derlenir).  
Hedef: pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `kamera(x, y, z, hedef_x?, hedef_y?, hedef_z?)` | — | Kameranın yerini ve baktığı noktayı ayarlar.<br>örnek: `kamera 6, 5, 8, 0, 0, 0` |
| `görüş_açısı(derece)` | — | Dikey görüş açısı (varsayılan 45). |
| `sahne_başla()` | — | 3B çizime başlar. |
| `sahne_bitir()` | — | 3B çizimi bitirir. |
| `küp(x, y, z, boyut, renk?)` | — | Küp (x, y, z merkez).<br>örnek: `küp 0, 1, 0, 2, KIRMIZI` |
| `kutu(x, y, z, genişlik, yükseklik, derinlik, renk?)` | — | Dikdörtgenler prizması. |
| `küp_çerçeve(x, y, z, boyut, renk?)` | — | Küpün tel çerçevesi. |
| `küre(x, y, z, yarıçap, renk?)` | — | Küre. |
| `silindir(x, y, z, yarıçap, yükseklik, renk?)` | — | Dik silindir (taban merkezi x, y, z). |
| `düzlem(x, y, z, genişlik, derinlik, renk?)` | — | Yatay düzlem (zemin). |
| `ızgara(adet, aralık)` | — | Zemin ızgarası. |
| `çizgi3(x1, y1, z1, x2, y2, z2, renk?)` | — | 3B çizgi. |
| `gl_kaydet()` | — | Dönüşüm matrisini saklar (glPushMatrix). |
| `gl_geri()` | — | Saklanan matrise döner (glPopMatrix). |
| `gl_taşı(x, y, z)` | — | Öteleme (glTranslatef). |
| `gl_döndür(açı, x, y, z)` | — | Eksen etrafında derece cinsinden döndürme (glRotatef).<br>örnek: `gl_döndür açı, 0, 1, 0` |
| `gl_ölçekle(x, y, z)` | — | Ölçekleme (glScalef). |
| `gl_başla(kip)` | — | Köşe çizimine başlar (glBegin).<br>örnek: `gl_başla GL_ÜÇGENLER` |
| `gl_renk(renk'i)` | — | Sonraki köşelerin rengi (glColor). |
| `gl_köşe(x, y, z?)` | — | Bir köşe ekler (glVertex3f). |
| `gl_bitir()` | — | Köşe çizimini bitirir (glEnd). |

Sabitler: `GL_ÇİZGİLER`, `GL_ÜÇGENLER`, `GL_DÖRTGENLER`

## sistem — `kullan sistem`

Komut çalıştırma, ortam değişkenleri, program argümanları (yalnız PC).  
Hedef: pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `komut(komut'u)` | tam | İşletim sistemi komutunu çalıştırır, çıkış kodunu verir. |
| `ortam_değişkeni(ad)` | metin | Ortam değişkeninin değeri. |
| `argümanlar()` | liste[metin] | Programa verilen komut satırı argümanları. |
| `platform()` | metin | "windows", "linux" ya da "macos". |

## temel (otomatik yüklenir)

Yazma, okuma ve tip dönüşümleri.  
Hedef: arduino, pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `yaz(değer'i...)` | — | Değerleri aralarına boşluk koyarak yazar, satır atlar.<br>örnek: `yaz "Merhaba", ad   ¦   "Merhaba"'yı yaz` |
| `yaz_satırsız(değer'i...)` | — | Satır atlamadan yazar. |
| `sor(soru?)` | metin | Kullanıcıdan bir satır okur.<br>örnek: `ad = sor "Adın ne? "` |
| `sayı_sor(soru?)` | ondalık | Kullanıcıdan bir sayı okur. |
| `tam_sor(soru?)` | tam | Kullanıcıdan bir tam sayı okur. |
| `uzunluk(x'in)` | tam | Metnin harf sayısı ya da listenin öğe sayısı.<br>örnek: `liste'nin uzunluğu   ¦   uzunluk(ad)` |
| `tam(x)` | tam | Tam sayıya çevirir.<br>örnek: `tam("42")` |
| `ondalık(x)` | ondalık | Ondalık sayıya çevirir. |
| `metin(x)` | metin | Metne çevirir. |
| `mantık(x)` | mantık | Doğru/yanlış değerine çevirir. |
| `tür(x'in)` | metin | Değerin tipini metin olarak verir. |
| `aralık(baş'tan, son'a, adım?)` | liste[tam] | Baştan sona (ikisi dahil) sayılar listesi; geri saymak için negatif adım.<br>örnek: `aralık(1, 5) -> [1, 2, 3, 4, 5]   aralık(5, 1, -2) -> [5, 3, 1]` |
| `iddia(koşul, ileti?)` | — | Koşul yanlışsa programı hata ile durdurur. |
| `çık(kod?)` | — | Programı bitirir. |
| `boş_mu(x)` | mantık | Metin ya da liste boşsa doğru. |

## zaman (otomatik yüklenir)

Bekleme, süre ölçme, saat ve tarih.  
Hedef: arduino, pc, py

| Komut | Döner | Açıklama |
|---|---|---|
| `bekle(süre'yi)` | — | Milisaniye cinsinden bekler.<br>örnek: `500 bekle  ¦  bekle 1000` |
| `saniye_bekle(süre'yi)` | — | Saniye cinsinden bekler. |
| `mikro_bekle(süre'yi)` | — | Mikrosaniye cinsinden bekler. |
| `milisaniye()` | tam | Program başladığından beri geçen milisaniye. |
| `mikrosaniye()` | tam | Program başladığından beri geçen mikrosaniye. |
| `zaman_damgası()` | tam | 1970'ten beri geçen saniye (yalnız PC). *(Arduino'da yok)* |
| `saat()` | tam | Şu anki saat (0-23). *(Arduino'da yok)* |
| `dakika()` | tam | Şu anki dakika. *(Arduino'da yok)* |
| `saniye()` | tam | Şu anki saniye. *(Arduino'da yok)* |
| `gün()` | tam | Ayın günü. *(Arduino'da yok)* |
| `ay()` | tam | Ay (1-12). *(Arduino'da yok)* |
| `yıl()` | tam | Yıl. *(Arduino'da yok)* |
| `tarih()` | metin | Bugünün tarihi: GG.AA.YYYY *(Arduino'da yok)* |
| `saat_metni()` | metin | Şu anki saat: SS:DD:ss *(Arduino'da yok)* |
