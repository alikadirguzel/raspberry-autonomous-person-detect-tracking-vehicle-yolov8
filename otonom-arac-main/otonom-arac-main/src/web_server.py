from flask import Flask, Response, render_template_string
import time
import cv2
import threading

# --- FLASK UYGULAMASI VE GLOBAL KARE TAMPONU ---
app = Flask(__name__)
GLOBAL_FRAME = None 

# Basit bir HTML şablonu
INDEX_HTML = """
<html>
<head>
    <meta charset="utf-8"/>
    <title>Otonom Araç Yayını</title>
    <style>
        body { margin: 0; background: #111; }
        img.video-feed {
            max-width: 100vw; max-height: 100vh;
            width: auto; height: auto;
            display: block; margin: 0 auto;
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <img src="/video_feed" class="video-feed"/>
</body>
</html>
"""

def set_global_frame(frame):
    """main.py'nin kareyi ayarlaması için bir helper fonksiyon."""
    global GLOBAL_FRAME
    GLOBAL_FRAME = frame

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

def mjpeg_generator():
    """MJPEG akışını sağlayan jeneratör."""
    global GLOBAL_FRAME
    while True:
        if GLOBAL_FRAME is None:
            time.sleep(0.05) 
            continue

        try:
            frame_copy = GLOBAL_FRAME.copy()
        except AttributeError:
            time.sleep(0.05)
            continue
        
        ok, buf = cv2.imencode(".jpg", frame_copy, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ok:
            print("[HATA] Frame JPEG'e dönüştürülemedi.")
            continue
        
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")
        
        time.sleep(0.03) 

@app.route("/video_feed")
def video_feed():
    return Response(mjpeg_generator(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

def start_flask_server():
    """Flask sunucusunu ayrı bir thread'de başlatır."""
    print("[INFO] Flask sunucusu 0.0.0.0:5000 adresinde başlatılıyor...")
    print("[INFO] Yayını görmek için http://<Raspberry_Pi_IP>:5000 adresine gidin.")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)

def start_server_thread():
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    return flask_thread