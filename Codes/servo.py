from machine import Pin, PWM
import time

pwm_blue = PWM(Pin(15, mode=Pin.OUT))
pwm_red = PWM(Pin(14, mode=Pin.OUT))

# Set the Frequency of the servos
pwm_blue.freq(50)
pwm_red.freq(50)

# The following values of the servos where hard coded
# If you want to set a particular duty_cycle --> use ".duty_u16()"
def close_blue():
    #center position
    pwm_blue.duty_u16(3000)

def open_red():
    #center position
    pwm_red.duty_u16(4000)

def close_red():
    #90 degree angle
    pwm_red.duty_u16(8200)

def open_blue():
    #90 degree angle
    pwm_blue.duty_u16(8200)
