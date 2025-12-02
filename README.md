# Autonomous Vehicle - Person Tracking System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red.svg)](https://www.raspberrypi.org/)

An autonomous vehicle project running on Raspberry Pi that performs real-time person detection using YOLOv8 and autonomous tracking with a P-control algorithm.

## 🚀 Features

- **Real-Time Object Detection**: High-accuracy person detection using YOLOv8 model
- **Kalman Filter**: Kalman filter for prediction and correction in target tracking
- **P-Control Algorithm**: Proportional control for precise motor control
- **Web Interface**: Real-time video streaming with Flask
- **Search Mode**: Automatic search algorithm when target is lost
- **Data Logging**: Tracking data saved in CSV format

## 📋 Requirements

### Hardware
- Raspberry Pi 4B (recommended)
- Raspberry Pi Camera Module or USB camera
- L298N Motor Driver
- 2x DC Motors
- Power supply (7-12V)

### Software
- Python 3.8+
- Raspberry Pi OS (Bullseye or later)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/alikadirguzel/otonom-arac.git
cd otonom-arac
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download YOLOv8 Model

Place the YOLOv8 model file (`yolov8n.pt`) in the project directory or update the `YOLO_MODEL_PATH` variable in `config.py`.

```bash
# Model can be automatically downloaded on first run
# or manually:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### 5. Check GPIO Pin Connections

Adjust the motor pin settings in `src/config.py` according to your Raspberry Pi connections:

```python
MOTOR_IN1 = 22  # Motor A - Forward
MOTOR_IN2 = 23  # Motor A - Backward
MOTOR_ENA = 12  # Motor A - PWM
MOTOR_IN3 = 27  # Motor B - Forward
MOTOR_IN4 = 24  # Motor B - Backward
MOTOR_ENB = 13  # Motor B - PWM
```

## 🎮 Usage

### Starting the Program

```bash
cd src
python3 main.py
```

### Accessing the Web Interface

After the program starts, you can view the live video stream from any device on the same network by visiting:

```
http://<Raspberry_Pi_IP>:5000
```

Example: `http://192.168.1.100:5000`

### Stopping the Program

Press `Ctrl+C` to safely stop the program.

## ⚙️ Configuration

You can adjust system parameters from the `src/config.py` file:

```python
# Control Parameters
BASE_SPEED = 1.0              # Base speed (0.0 - 1.0)
Kp = 0.100                    # P-Control gain
DEADZONE = 20                 # Center tolerance (pixels)
SCAN_SPEED = 0.9              # Search mode speed
TOTAL_SEARCH_TIMEOUT = 30.0   # Search timeout (seconds)

# System Settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DEVICE = 'cuda'  # or 'cpu'
```

## 📁 Project Structure

```
otonom-arac/
├── src/
│   ├── main.py           # Main program loop
│   ├── config.py         # Configuration parameters
│   ├── detector.py       # YOLOv8 detection thread
│   ├── motor_control.py  # Motor control class
│   ├── logger.py         # Kalman filter and logging
│   └── web_server.py     # Flask web server
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── LICENSE              # License information
└── .gitignore          # Git ignore file
```

## 🔬 Algorithm Explanation

### P-Control (Proportional Control)

The system adjusts motor speeds based on the target's deviation from the screen center:

```
error = target_x - center_x
adjustment = Kp × error
motor_a_speed = BASE_SPEED + adjustment
motor_b_speed = BASE_SPEED - adjustment
```

### Kalman Filter

Used to predict target position and correct noisy measurements.

### Search Mode

When the target is lost, the vehicle performs in-place rotation based on the last known direction to search for the target.

## 🐛 Troubleshooting

### Camera Not Found
- Check camera connection
- Ensure `picamera2` library is installed
- If using USB camera, update camera settings in `config.py`

### Model Cannot Be Loaded
- Check your internet connection (for initial download)
- Verify the model file path in `config.py`

### Motors Not Working
- Check GPIO pin connections
- Ensure power supply is adequate
- Verify `gpiozero` library is installed

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👥 Contributing

We welcome your contributions! Please open an issue first or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact
ali_kadir_guzel@hotmail.com
You can open an issue for questions or suggestions.

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLOv8
- [OpenCV](https://opencv.org/) - Image processing
- [Flask](https://flask.palletsprojects.com/) - Web framework
