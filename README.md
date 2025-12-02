# Autonomous Vehicle - Person Tracking System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red.svg)](https://www.raspberrypi.org/)

An autonomous vehicle project running on Raspberry Pi that performs real-time person detection using YOLOv8 and autonomous tracking using a P-control algorithm.

## 🚀 Features

- **Real-Time Object Detection**: High-accuracy person detection with the YOLOv8 model.
- **Kalman Filter**: Kalman filter implementation for prediction and correction in target tracking.
- **P-Control Algorithm**: Proportional control for precise motor steering.
- **Web Interface**: Real-time video streaming via Flask.
- **Search Mode**: Automatic search algorithm initiates when the target is lost.
- **Data Logging**: Recording tracking data in CSV format.

## 📋 Requirements

### Software
- Python 3.8+
- Raspberry Pi OS (Bullseye or later)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/autonomous-vehicle.git](https://github.com/your-username/autonomous-vehicle.git)
cd autonomous-vehicle
2. Create a Virtual Environment (Recommended)
Bash

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Download the YOLOv8 Model
Place the YOLOv8 model file (yolov8n.pt) in the project directory or update the YOLO_MODEL_PATH variable in config.py.

Bash

# The model can be downloaded automatically on the first run
# or manually:
wget [https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt)
5. Check GPIO Pin Connections
Edit the motor pin settings in src/config.py according to your Raspberry Pi connections:

Python

MOTOR_IN1 = 22  # Motor A - Forward
MOTOR_IN2 = 23  # Motor A - Backward
MOTOR_ENA = 12  # Motor A - PWM
MOTOR_IN3 = 27  # Motor B - Forward
MOTOR_IN4 = 24  # Motor B - Backward
MOTOR_ENB = 13  # Motor B - PWM
🎮 Usage
Starting the Program
Bash

cd src
python3 main.py
Accessing the Web Interface
Once the program is running, you can watch the live video stream from any device on the same network by visiting:

http://<Raspberry_Pi_IP>:5000
Example: http://192.168.1.100:5000

Stopping the Program
You can safely stop the program by pressing Ctrl+C.

⚙️ Configuration
You can adjust system parameters from the src/config.py file:

Python

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
📁 Project Structure
autonomous-vehicle/
├── src/
│   ├── main.py           # Main program loop
│   ├── config.py         # Configuration parameters
│   ├── detector.py       # YOLOv8 detection thread
│   ├── motor_control.py  # Motor control class
│   ├── logger.py         # Kalman filter and logging
│   └── web_server.py     # Flask web server
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── LICENSE               # License information
└── .gitignore            # Git ignore file
🔬 Algorithm Description
P-Control (Proportional Control)
The system adjusts motor speeds based on the target's deviation from the screen center:

error = target_x - center_x
correction = Kp * error
motor_a_speed = BASE_SPEED + correction
motor_b_speed = BASE_SPEED - correction
Kalman Filter
Used to predict the target's position and correct noisy measurements, providing a smooth tracking path.

Search Mode
When the target is lost, the vehicle performs a spot turn based on the last known direction to actively search for the target.

🐛 Troubleshooting
Camera Not Found
Check the camera connection.

Ensure the picamera2 library is installed.

If using a USB camera, update the camera settings in config.py.

Model Cannot Be Loaded
Check your internet connection (for the initial download).

Verify the model file path in config.py.

Motors Not Working
Check the GPIO pin connections.

Ensure the power supply is sufficient.

Ensure the gpiozero library is installed.

📝 License
This project is licensed under the MIT License. See the LICENSE file for details.

👥 Contributing
Contributions are welcome! Please open an issue or submit a pull request first.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📧 Contact
For questions or suggestions, please open an issue.

🙏 Acknowledgements
Ultralytics - YOLOv8

OpenCV - Computer Vision

Flask - Web Framework
