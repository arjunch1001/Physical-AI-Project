import lgpio
from time import sleep

SERVO_PIN = 18
SERVO_MIN = 1000
SERVO_MID = 1500
SERVO_MAX = 2000

class PhysicalController:
    def __init__(self):
        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self.h, SERVO_PIN)
        print("PhysicalController initialized")

    def _set_servo(self, pulsewidth):
        lgpio.tx_servo(self.h, SERVO_PIN, pulsewidth)
        sleep(0.3)

    def alert(self):
        self._set_servo(SERVO_MAX)
        sleep(0.5)
        self._set_servo(SERVO_MIN)

    def track(self):
        self._set_servo(SERVO_MID)

    def idle(self):
        lgpio.tx_servo(self.h, SERVO_PIN, 0)

    def cleanup(self):
        lgpio.tx_servo(self.h, SERVO_PIN, 0)
        lgpio.gpiochip_close(self.h)