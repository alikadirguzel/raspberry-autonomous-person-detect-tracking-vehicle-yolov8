from gpiozero import PWMOutputDevice, DigitalOutputDevice
# from time import sleep # Gerekli değilse kaldırılabilir
import config

# Motor A (Sağ Tekerler)
in1 = DigitalOutputDevice(config.MOTOR_IN1)
in2 = DigitalOutputDevice(config.MOTOR_IN2)
ena = PWMOutputDevice(config.MOTOR_ENA)

# Motor B (Sol Tekerler)
in3 = DigitalOutputDevice(config.MOTOR_IN3)
in4 = DigitalOutputDevice(config.MOTOR_IN4)
enb = PWMOutputDevice(config.MOTOR_ENB)

class MotorController:
    """GPIO Zero kütüphanesi ile motor kontrolünü yönetir."""
    def __init__(self):
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.ena = ena
        self.enb = enb
        self.hiz = 0.7

    def motor_a_ileri(self):
        self.in2.off()
        self.in1.on()
        
    def motor_a_geri(self):
        self.in1.off()
        self.in2.on()

    def motor_b_ileri(self):
        self.in4.off()
        self.in3.on()

    def motor_b_geri(self):
        self.in3.off()
        self.in4.on()

    def dur(self):
        self.in1.off()
        self.in2.off()
        self.in3.off()
        self.in4.off()
        self.ena.value = 0
        self.enb.value = 0

    def motor_a_hiz_ayarla(self, new_speed):
        self.ena.value = max(0.0, min(new_speed, 1.0))

    def motor_b_hiz_ayarla(self, new_speed):
        self.enb.value = max(0.0, min(new_speed, 1.0))