# KONTROL PARAMETRELERİ
BASE_SPEED = 1.0            # Aracın merkezde düz giderkenki temel hızı (0.0 - 1.0)
Kp = 0.100 	                # P-Kontrol Kazancı: Dönüş hassasiyeti (Çok kritik, ayarla!)
DEADZONE = 20 	            # Merkezdeki piksel toleransı (piksel)
SCAN_SPEED = 0.9            # Arama modundaki yerinde dönüş hızı (0.0 - 1.0)
TOTAL_SEARCH_TIMEOUT = 30.0 # Hedef kayıp sayacı (saniye)


# SİSTEM AYARLARI
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
YOLO_MODEL_PATH = "/home/pi/Desktop/otonom_arac/yolov8n.pt"
DEVICE = 'cuda' # 'cuda' veya 'cpu'


# MOTOR PIN AYARLARI (GPIO Zero için)
MOTOR_IN1 = 22
MOTOR_IN2 = 23
MOTOR_ENA = 12
MOTOR_IN3 = 27
MOTOR_IN4 = 24
MOTOR_ENB = 13


# LOGLAMA AYARLARI 
CSV_FILENAME = "takip_log.csv"
LOG_WRITE_INTERVAL_SEC = 1.0