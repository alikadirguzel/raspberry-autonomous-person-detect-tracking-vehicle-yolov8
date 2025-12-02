# Otonom Araç - Kişi Takip Sistemi

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4B-red.svg)](https://www.raspberrypi.org/)

Raspberry Pi üzerinde çalışan, YOLOv8 ile gerçek zamanlı kişi tespiti ve P-kontrol algoritması ile otonom takip yapan araç projesi.

## 🚀 Özellikler

- **Gerçek Zamanlı Nesne Tespiti**: YOLOv8 modeli ile yüksek doğrulukta kişi tespiti
- **Kalman Filtresi**: Hedef takibinde tahmin ve düzeltme için Kalman filtresi
- **P-Kontrol Algoritması**: Hassas motor kontrolü için oransal kontrol
- **Web Arayüzü**: Flask ile gerçek zamanlı video yayını
- **Arama Modu**: Hedef kaybolduğunda otomatik arama algoritması
- **Veri Loglama**: CSV formatında takip verilerinin kaydedilmesi

## 📋 Gereksinimler


### Yazılım
- Python 3.8+
- Raspberry Pi OS (Bullseye veya üzeri)

## 🔧 Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/alikadirguzel/otonom-arac.git
cd otonom-arac
```

### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. YOLOv8 Modelini İndirin

YOLOv8 model dosyasını (`yolov8n.pt`) proje dizinine yerleştirin veya `config.py` dosyasındaki `YOLO_MODEL_PATH` değişkenini güncelleyin.

```bash
# Model otomatik olarak ilk çalıştırmada indirilebilir
# veya manuel olarak:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### 5. GPIO Pin Bağlantılarını Kontrol Edin

`src/config.py` dosyasında motor pin ayarlarını Raspberry Pi bağlantılarınıza göre düzenleyin:

```python
MOTOR_IN1 = 22  # Motor A - İleri
MOTOR_IN2 = 23  # Motor A - Geri
MOTOR_ENA = 12  # Motor A - PWM
MOTOR_IN3 = 27  # Motor B - İleri
MOTOR_IN4 = 24  # Motor B - Geri
MOTOR_ENB = 13  # Motor B - PWM
```

## 🎮 Kullanım

### Programı Başlatma

```bash
cd src
python3 main.py
```

### Web Arayüzüne Erişim

Program çalıştıktan sonra, aynı ağdaki herhangi bir cihazdan şu adrese giderek canlı video yayınını izleyebilirsiniz:

```
http://<Raspberry_Pi_IP>:5000
```

Örnek: `http://192.168.1.100:5000`

### Programı Durdurma

`Ctrl+C` tuşlarına basarak programı güvenli bir şekilde durdurabilirsiniz.

## ⚙️ Yapılandırma

`src/config.py` dosyasından sistem parametrelerini ayarlayabilirsiniz:

```python
# Kontrol Parametreleri
BASE_SPEED = 1.0              # Temel hız (0.0 - 1.0)
Kp = 0.100                    # P-Kontrol kazancı
DEADZONE = 20                 # Merkez toleransı (piksel)
SCAN_SPEED = 0.9              # Arama modu hızı
TOTAL_SEARCH_TIMEOUT = 30.0   # Arama zaman aşımı (saniye)

# Sistem Ayarları
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DEVICE = 'cuda'  # veya 'cpu'
```

## 📁 Proje Yapısı

```
otonom-arac/
├── src/
│   ├── main.py           # Ana program döngüsü
│   ├── config.py         # Yapılandırma parametreleri
│   ├── detector.py       # YOLOv8 tespit thread'i
│   ├── motor_control.py  # Motor kontrol sınıfı
│   ├── logger.py         # Kalman filtresi ve loglama
│   └── web_server.py     # Flask web sunucusu
├── requirements.txt      # Python bağımlılıkları
├── README.md            # Bu dosya
├── LICENSE              # Lisans bilgisi
└── .gitignore          # Git ignore dosyası
```

## 🔬 Algoritma Açıklaması

### P-Kontrol (Proportional Control)

Sistem, hedefin ekran merkezinden sapmasına göre motor hızlarını ayarlar:

```
hata = hedef_x - merkez_x
düzeltme = Kp × hata
motor_a_hız = BASE_SPEED + düzeltme
motor_b_hız = BASE_SPEED - düzeltme
```

### Kalman Filtresi

Hedefin pozisyonunu tahmin etmek ve gürültülü ölçümleri düzeltmek için kullanılır.

### Arama Modu

Hedef kaybolduğunda, son bilinen yöne göre yerinde dönüş yaparak hedefi arar.

## 🐛 Sorun Giderme

### Kamera Bulunamıyor
- Kamera bağlantısını kontrol edin
- `picamera2` kütüphanesinin yüklü olduğundan emin olun
- USB kamera kullanıyorsanız, `config.py`'de kamera ayarlarını güncelleyin

### Model Yüklenemiyor
- İnternet bağlantınızı kontrol edin (ilk indirme için)
- Model dosyasının yolunu `config.py`'de kontrol edin

### Motorlar Çalışmıyor
- GPIO pin bağlantılarını kontrol edin
- Güç kaynağının yeterli olduğundan emin olun
- `gpiozero` kütüphanesinin yüklü olduğundan emin olun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen önce bir issue açın veya pull request gönderin.

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

## 🙏 Teşekkürler

- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLOv8
- [OpenCV](https://opencv.org/) - Görüntü işleme
- [Flask](https://flask.palletsprojects.com/) - Web framework

