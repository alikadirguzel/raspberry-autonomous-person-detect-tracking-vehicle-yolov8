#!/usr/bin/env python3
import torch
import cv2
import time
import threading
import sys
import numpy as np
import queue 

import config
from motor_control import MotorController 
from detector import DetectionThread, frame_queue, result_queue 
from logger import StateLogger 
import web_server 

# Picamera2'yi import et
try:
    from picamera2 import Picamera2
except ImportError:
    print("[HATA] Picamera2 yüklenemedi. Kamerayı devre dışı bırakıyorum.")
    Picamera2 = None

# ==================================================================
# --- SİSTEM BAŞLATMA ---
# ==================================================================

# 1. Donanım ve Sistem Durumu Hazırlığı
device = config.DEVICE if torch.cuda.is_available() else 'cpu'
print(f"[INFO] CUDA kullanılabilir mi?: {torch.cuda.is_available()}")

motor = MotorController() # Motor kontrolcüsünü başlat

state_logger = StateLogger() # Kalman, Log ve Trajectory yöneticisini başlat

# 2. Kamera Başlatma
picam2 = None
if Picamera2:
    try:
        picam2 = Picamera2()
        camera_config = picam2.create_video_configuration(
            main={"size": (config.FRAME_WIDTH, config.FRAME_HEIGHT), "format": "BGR888"},
        )
        picam2.configure(camera_config)
        picam2.start()
        time.sleep(1)
        print(f"[INFO] Picamera2 başlatıldı. Çözünürlük: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
    except Exception as e:
        print(f"[HATA] Picamera2 başlatılamadı: {e}. Programı sonlandırıyorum.")
        sys.exit(1)


# 3. Threadleri Başlatma
print(f"[INFO] YOLOv8 modeli başlatılıyor: {config.YOLO_MODEL_PATH}")
detection_thread = DetectionThread(
    config.YOLO_MODEL_PATH, device, 
    frame_queue, result_queue
)
detection_thread.daemon = True 
detection_thread.start()

web_server_thread = web_server.start_server_thread() # Flask sunucusunu başlat

# ==================================================================
# --- ANA KONTROL DÖNGÜSÜ ---
# ==================================================================

print("[INFO] Ana kontrol döngüsü P-Kontrol ile başlıyor...")
last_known_target = None 
frame_count = 0
fps = 0
start_fps_time = time.time()

try:
    while True:
        # --- 1. Görüntü Yakala (HIZLI) ---
        if picam2 is None:
            time.sleep(1)
            continue

        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
        if frame is None:
            print("[HATA] Kameradan görüntü alınamadı.")
            break
            
        small_frame = cv2.flip(frame, 1) # BGR
        img_rgb_for_yolo = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB) # RGB

        # --- 2. Frame'i Tespit Thread'ine Gönder (HIZLI) ---
        try:
            frame_queue.put_nowait((img_rgb_for_yolo, small_frame)) 
        except queue.Full:
            pass 

        # --- 3. Sonucu Tespit Thread'inden Al (HIZLI) ---
        try:
            last_known_target = result_queue.get_nowait()
        except queue.Empty:
            pass 

        direction = "BEKLEME" 

        # --- 4. MOTOR KONTROL VE LOJİK (HIZLI) ---
        center_x = config.FRAME_WIDTH // 2

        if last_known_target is not None:
            # ==================================================================
            # --- HEDEF GÖRÜNÜR DURUMDA (P-KONTROL TAKİP) ---
            # ==================================================================
            state_logger.search_start_time = None 
            
            x1, y1, x2, y2 = map(int, last_known_target[:4])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            width = x2 - x1
            
            # Kalman ve Tahmin
            measurement = np.array([[np.float32(cx)], [np.float32(cy)]])
            state_logger.kalman_correct(measurement) 
            prediction = state_logger.kalman_predict() 
            pred_x = int(prediction[0][0])
            pred_y = int(prediction[1][0])

            dx = pred_x - center_x # Merkezden yatay sapma (HATA)

            # Yakınlık Hesaplama
            proximity = "UZAK"
            if width > 200: proximity = "YAKIN"
            elif width > 100: proximity = "ORTA"
            
            # Son bilinen yatay yönü güncelle
            if dx > config.DEADZONE: state_logger.last_known_horizontal_direction = "SAG"
            elif dx < -config.DEADZONE: state_logger.last_known_horizontal_direction = "SOL"

            # ------------------------------------------------
            # P-KONTROL HIZ HESAPLAMASI
            # ------------------------------------------------
            if proximity == "YAKIN":
                motor.dur()
                direction = "YAKIN"
            
            elif abs(dx) <= config.DEADZONE:
                # Merkezde
                motor.motor_a_hiz_ayarla(config.BASE_SPEED)
                motor.motor_b_hiz_ayarla(config.BASE_SPEED)
                motor.motor_a_ileri()
                motor.motor_b_ileri()
                direction = "MERKEZ"
                
            else:
                # Merkezde değil
                turn_adjustment = config.Kp * dx
                turn_adjustment = max(-config.BASE_SPEED, min(config.BASE_SPEED, turn_adjustment))
                
                motor_a_speed = config.BASE_SPEED + turn_adjustment
                motor_b_speed = config.BASE_SPEED - turn_adjustment
                
                motor_a_speed = max(0.0, min(1.0, motor_a_speed))
                motor_b_speed = max(0.0, min(1.0, motor_b_speed))

                motor.motor_a_hiz_ayarla(motor_a_speed)
                motor.motor_b_hiz_ayarla(motor_b_speed)
                motor.motor_a_ileri() 
                motor.motor_b_ileri()

                direction = "SAG" if dx > 0 else "SOL"
                
            print(f"[YÖN]: {direction} | {proximity} | Hız A: {motor.ena.value:.2f}, Hız B: {motor.enb.value:.2f}")

            # Çizim
            cv2.rectangle(small_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(small_frame, (pred_x, pred_y), 5, (0, 0, 255), -1)
            cv2.putText(small_frame, f"{direction} | {proximity}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                            
            state_logger.update_trajectory(pred_x, pred_y) 
            state_logger.update_log_buffer(pred_x, pred_y, direction, "YOLOv8+Kalman") 

        else:
            # ==================================================================
            # --- HEDEF YOK (SPIN TURN ARAMA MODU) ---
            # ==================================================================
            current_time = time.time()
            msg = "ARANIYOR"

            if state_logger.search_start_time is None:
                print("[BİLGİ] Arama modu başlatıldı.")
                state_logger.search_start_time = current_time
                motor.dur() # Başlangıçta dur

            total_elapsed = current_time - state_logger.search_start_time
            
            if total_elapsed > config.TOTAL_SEARCH_TIMEOUT:
                # Zaman aşımı
                print(f"[UYARI] Hedef {config.TOTAL_SEARCH_TIMEOUT:.0f} saniyedir kayıp. Arama modu sıfırlanıyor.")
                state_logger.search_start_time = None
                motor.dur()
                msg = "ARAMA SIFIRLANDI"
            
            else:
                # Yerinde Dönüş
                turn_speed = config.SCAN_SPEED 
                
                # Arama lojiği
                if state_logger.last_known_horizontal_direction == "SOL":
                    motor.motor_a_hiz_ayarla(turn_speed - 0.4) 
                    motor.motor_b_hiz_ayarla(turn_speed)
                    motor.motor_b_ileri() 
                    motor.motor_a_geri() 
                    msg = f"ARANIYOR (SAG Taraniyor {config.TOTAL_SEARCH_TIMEOUT - total_elapsed:.1f}s)"
                    direction = "ARAMA_SAG"
                else: # SAG
                    motor.motor_a_hiz_ayarla(turn_speed) 
                    motor.motor_b_hiz_ayarla(turn_speed - 0.4)
                    motor.motor_a_ileri() 
                    motor.motor_b_geri() 
                    msg = f"ARANIYOR (SOL Taraniyor {config.TOTAL_SEARCH_TIMEOUT - total_elapsed:.1f}s)"
                    direction = "ARAMA_SOL"

            # Kalman tahmini 
            prediction = state_logger.kalman_predict() 
            pred_x = int(prediction[0][0])
            pred_y = int(prediction[1][0])
            state_logger.update_trajectory(pred_x, pred_y) 
            
            cv2.circle(small_frame, (pred_x, pred_y), 5, (255, 0, 0), -1)
            cv2.putText(small_frame, msg, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            state_logger.update_log_buffer(pred_x, pred_y, direction, "Kalman Search")


        # --- 5. Döngü Sonu İşlemleri (HER ZAMAN ÇALIŞIR) ---
        state_logger.write_logs_to_disk() 

        # Yörünge çizimi
        for i in range(1, len(state_logger.trajectory_points)):
            cv2.line(small_frame, state_logger.trajectory_points[i - 1], state_logger.trajectory_points[i], (0, 0, 255), 2)

        # FPS Hesaplama
        frame_count += 1
        if frame_count % 10 == 0 and frame_count > 0:
            curr_time = time.time()
            elapsed = curr_time - start_fps_time
            if elapsed > 0:
                fps = 10 / elapsed
            start_fps_time = curr_time

        cv2.putText(small_frame, f"FPS: {int(fps)}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # KAREYİ GLOBAL YAYIN TAMPONUNA GÖNDER
        web_server.set_global_frame(small_frame)


finally:
    # --- GÜVENLİ ÇIKIŞ BLOĞU ---
    print("\n[INFO] Program sonlandırılıyor (Ctrl+C algılandı)...")
    
    # Thread'i durdur
    if 'detection_thread' in locals() and detection_thread.is_alive():
        print("[INFO] Tespit thread'i durduruluyor...")
        detection_thread.stop()
        detection_thread.join() 
        print("[INFO] Tespit thread'i durduruldu.")

    # Kalan logları diske yaz
    print("[INFO] Kalan loglar diske yazılıyor...")
    state_logger.write_logs_to_disk() 

    print("[INFO] Donanımlar kapatılıyor...")
    if picam2:
        picam2.stop()
    cv2.destroyAllWindows()
    motor.dur() # Motorları mutlaka durdur
    
    print("[INFO] Temizlik tamamlandı. Çıkış yapıldı.")