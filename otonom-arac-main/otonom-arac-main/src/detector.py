import threading
import queue
import torch
from ultralytics import YOLO
import numpy as np
# import time # Gerekli değilse kaldırılabilir
import config

# Kuyruklar (Thread'ler arası iletişim için)
frame_queue = queue.Queue(maxsize=1)
result_queue = queue.Queue(maxsize=1)

class DetectionThread(threading.Thread):
    def __init__(self, model_pt_path, device, frame_q, result_q):
        super().__init__()
        
        self.model_pt_path = model_pt_path
        self.device = device
        self.frame_q = frame_q
        self.result_q = result_q
        self.model = None 
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        print("[INFO] Tespit Thread'i: YOLOv8 Modeli yükleniyor...")
        try:
            self.model = YOLO(self.model_pt_path).to(self.device)
            self.model(np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8), verbose=False)
            print("[INFO] Tespit Thread'i: Model yüklendi. Döngü başlıyor.")
        except Exception as e:
            print(f"[HATA] Tespit Thread'i modeli yükleyemedi: {e}")
            self.running = False 
            return 
            
        while self.running:
            try:
                # img_rgb, small_frame (small_frame kullanılmıyor ama uyumluluk için alınabilir)
                img_rgb, _ = self.frame_q.get(timeout=1)
            except queue.Empty:
                continue 

            results_list = self.model(img_rgb, imgsz=320, verbose=False)
            result = results_list[0]
            
            preds_v8_format = []
            for box in result.boxes:
                class_id = int(box.cls[0].cpu().numpy())
                if class_id == 0: # Sadece 'person' sınıfı
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    if conf > 0.25:
                        preds_v8_format.append([x1, y1, x2, y2, conf, class_id])
            
            # En büyük alanı (hedefi) bul
            target = None
            max_area = 0

            for row in preds_v8_format: 
                x1, y1, x2, y2 = map(int, row[:4])
                area = (x2 - x1) * (y2 - y1)
                
                if area > max_area:
                    max_area = area
                    target = row 

            try:
                self.result_q.put_nowait(target)
            except queue.Full:
                pass