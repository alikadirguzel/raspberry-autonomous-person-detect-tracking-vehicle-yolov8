import numpy as np
import cv2
import pandas as pd
import os
import time
import config # Loglama ayarları ve çözünürlük için

class StateLogger:
    """Kalman filtresini, loglamayı (CSV) ve hedef yörüngesini (trajectory) yönetir."""
    def __init__(self):
        self.kalman = self._init_kalman()
        self.trajectory_points = []
        self.log_buffer = []
        self.last_write_time = time.time()
        self._init_csv_log()
        self.search_start_time = None
        self.last_known_horizontal_direction = "SAG"

    def _init_kalman(self):
        """Kalman filtresini başlatır ve sıfırlar."""
        kalman = cv2.KalmanFilter(4, 2)
        center_x = config.FRAME_WIDTH // 2
        center_y = config.FRAME_HEIGHT // 2
        
        kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
        kalman.statePre = np.array([[center_x], [center_y], [0], [0]], dtype=np.float32)
        kalman.statePost = np.array([[center_x], [center_y], [0], [0]], dtype=np.float32)
        
        return kalman

    def _init_csv_log(self):
        """Log dosyasını hazırlar (varsa siler)."""
        if os.path.exists(config.CSV_FILENAME):
            os.remove(config.CSV_FILENAME)
        log_df = pd.DataFrame(columns=["timestamp", "x", "y", "direction", "source"])
        log_df.to_csv(config.CSV_FILENAME, index=False)
    
    def update_log_buffer(self, x, y, direction, source):
        """Log tamponuna bir satır ekler."""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_buffer.append([timestamp, x, y, direction, source])
        
    def write_logs_to_disk(self):
        """Tampondaki logları diske yazar (belirli aralıklarla veya çıkışta)."""
        current_time_log = time.time()
        
        # Periyodik yazma (main döngüsü içinde)
        if current_time_log - self.last_write_time >= config.LOG_WRITE_INTERVAL_SEC:
            if self.log_buffer:
                temp_df = pd.DataFrame(self.log_buffer, columns=["timestamp", "x", "y", "direction", "source"])
                temp_df.to_csv(config.CSV_FILENAME, mode='a', header=False, index=False)
                self.log_buffer = []
            self.last_write_time = current_time_log
        
        # Çıkışta kalanları yazma (finally bloğu için)
        elif self.log_buffer and current_time_log - self.last_write_time < config.LOG_WRITE_INTERVAL_SEC:
             temp_df = pd.DataFrame(self.log_buffer, columns=["timestamp", "x", "y", "direction", "source"])
             temp_df.to_csv(config.CSV_FILENAME, mode='a', header=False, index=False)
             self.log_buffer = [] # tamponu temizle

    def update_trajectory(self, x, y):
        """Yörünge noktalarını günceller."""
        self.trajectory_points.append((x, y))
        if len(self.trajectory_points) > 100:
            self.trajectory_points.pop(0)

    # Main döngüsünün kullanacağı Kalman metodları
    def kalman_correct(self, measurement):
        return self.kalman.correct(measurement)

    def kalman_predict(self):
        return self.kalman.predict()