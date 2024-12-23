from machine import Pin, PWM
from time import sleep

# Set the pulse frequency for motor control
pulse_freq = 1000

# Configure control pins for motor operation
control_pin_A = Pin(19, Pin.OUT)
control_pin_B = Pin(20, Pin.OUT)
pwm_enable = PWM(Pin(18), pulse_freq)

# Define minimum and maximum pulse width values for PWM
duty_min = 15000
duty_max = 65535

# Helper function to compute duty cycle based on input level
def compute_duty(input_level):
    if input_level <= 0 or input_level > 100:
        return 0
    else:
        return int(duty_min + (duty_max - duty_min) * (input_level / 100))

# Function to drive motor in a forward direction
def drive_forward(input_level):
    pwm_enable.duty_u16(compute_duty(input_level))
    control_pin_A.value(1)
    control_pin_B.value(0)

# Function to drive motor in reverse
def drive_reverse(input_level):
    pwm_enable.duty_u16(compute_duty(input_level))
    control_pin_A.value(0)
    control_pin_B.value(1)

# Function to halt motor movement
def halt():
    pwm_enable.duty_u16(0)
    control_pin_A.value(0)
    control_pin_B.value(0)
