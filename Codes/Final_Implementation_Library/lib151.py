from machine import * 
import machine
import time

#---------------------------------------------------------#
#                     PIN SETUP
#---------------------------------------------------------#

#Oled Pins
oled_i2c = I2C(0, scl=Pin(13), sda=Pin(12))  # Default frequency: 400kHz


#Perilstatic Pump Pins
pulse_freq = 1000 #define the pulse frequency
control_pin_A = Pin(19, Pin.OUT)
control_pin_B = Pin(20, Pin.OUT)
pwm_enable = PWM(Pin(18), pulse_freq)

#Load Cell Pins
data_pin = Pin(16, Pin.IN, pull=Pin.PULL_DOWN)
clock_pin = Pin(17, Pin.OUT)

#Servo Pins
pwm_blue = PWM(Pin(15, mode=Pin.OUT))
pwm_red = PWM(Pin(14, mode=Pin.OUT))

#Stepper Pins
step_pin_IN1 = machine.Pin(3, machine.Pin.OUT)   # IN1 connected to GPIO3
step_pin_IN2 = machine.Pin(4, machine.Pin.OUT)   # IN2 connected to GPIO4
step_pin_IN3 = machine.Pin(6, machine.Pin.OUT)   # IN3 connected to GPIO6
step_pin_IN4 = machine.Pin(7, machine.Pin.OUT)   # IN4 connected to GPIO7
enable_pin_A = machine.Pin(2, machine.Pin.OUT)   # ENA for motor driver channel A, connected to GPIO2
enable_pin_B = machine.Pin(5, machine.Pin.OUT)   # ENB for motor driver channel B, connected to GPIO5

#---------------------------------------------------------#
#                Code for Servos (Pinch Valve)
#---------------------------------------------------------#

pwm_blue.freq(50)
pwm_red.freq(50)

#Need to find the values for the blue servo
pwm_blue.freq(50)
pwm_red.freq(50)

def close_blue():
    #center position
    pwm_blue.duty_u16(3000)

def open_red():
    #center position
    pwm_red.duty_u16(4000)
    #pwm_red.duty_u16(6553)"""

def close_red():
    #90 degree angle
    pwm_red.duty_u16(8200)
    #pwm_red.duty_u16(3276)

def open_blue():
    #90 degree angle
    pwm_blue.duty_u16(8000)

#---------------------------------------------------------#
#                 Code for Perilstatic Pump
#---------------------------------------------------------#

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

#---------------------------------------------------------#
#               Code for I2C Oled Screen
#---------------------------------------------------------#

# Display Configuration Commands
SET_CONTRAST_LVL = const(0x81)
DISPLAY_ALL_PIXELS = const(0xa4)
DISPLAY_NORMAL = const(0xa6)
TURN_DISPLAY = const(0xae)
SET_ADDR_MODE = const(0x20)
SET_COL_RANGE = const(0x21)
SET_PAGE_RANGE = const(0x22)
START_LINE_POS = const(0x40)
SET_REMAP = const(0xa0)
SET_MUX = const(0xa8)
SET_COM_DIRECTION = const(0xc0)
DISPLAY_OFFSET = const(0xd3)
COM_PIN_CONFIG = const(0xda)
SET_CLK_DIV_RATIO = const(0xd5)
SET_PRECHARGE_PERIOD = const(0xd9)
SET_VCOM_DESELECT = const(0xdb)
ENABLE_CHARGE_PUMP = const(0x8d)

# Screen dimensions
OLED_WIDTH = 128
OLED_HEIGHT = 64
I2C_ADDR = 0x3c  #I2C address for SSD1306 found through "oled_i2c.py"

# Display buffer (1 byte for each 8 vertical pixels)
display_buffer = bytearray((OLED_HEIGHT // 8) * OLED_WIDTH)

# Sends command to the OLED screen
def send_command(cmd):
    temp_buf = bytearray([0x80, cmd]) 
    oled_i2c.writeto(I2C_ADDR, temp_buf)

# Sends data to OLED
def send_data(data):
    temp_buf = bytearray([0x40, data]) 
    oled_i2c.writeto(I2C_ADDR, temp_buf)

# Initialize OLED settings
def initialize_oled():
    init_sequence = [
        TURN_DISPLAY | 0x00,  # Turn off display
        SET_ADDR_MODE, 0x00,  # Horizontal address mode
        START_LINE_POS | 0x00,
        SET_REMAP | 0x01,  # Column address remap
        SET_MUX, OLED_HEIGHT - 1,
        SET_COM_DIRECTION | 0x08,  # COM[N] to COM0 scan
        DISPLAY_OFFSET, 0x00,
        COM_PIN_CONFIG, 0x12,
        SET_CLK_DIV_RATIO, 0x80,
        SET_PRECHARGE_PERIOD, 0xf1,
        SET_VCOM_DESELECT, 0x30,  # Deselect level
        SET_CONTRAST_LVL, 0xff,  # Max contrast
        DISPLAY_ALL_PIXELS,  # Display RAM content
        DISPLAY_NORMAL,  # Normal display mode
        ENABLE_CHARGE_PUMP, 0x14,  # Enable charge pump
        TURN_DISPLAY | 0x01  # Turn on display
    ]
    for cmd in init_sequence:
        send_command(cmd)

# Clears the display buffer
def clear_buffer():
    for i in range(len(display_buffer)):
        display_buffer[i] = 0x00

# Sets a single pixel in the buffer
def set_pixel_in_buffer(x, y, color):
    if y >= OLED_HEIGHT or x < 0 or y < 0:
        return
    if x >= OLED_WIDTH:
        y += 8
    row = y // 8
    bit_pos = y % 8
    buffer_index = row * OLED_WIDTH + x
    if color:
        display_buffer[buffer_index] |= (1 << bit_pos)
    else:
        display_buffer[buffer_index] &= ~(1 << bit_pos)

# Draws character (simple 5x8 font)
def render_character(x, y, char):
    font_map = {
    'A': [0x7C, 0x12, 0x12, 0x12, 0x7C],
    'B': [0x7E, 0x4A, 0x4A, 0x4A, 0x34],
    'C': [0x3C, 0x42, 0x42, 0x42, 0x24],
    'D': [0x7E, 0x42, 0x42, 0x42, 0x3C],
    'E': [0x7E, 0x4A, 0x4A, 0x42, 0x42],
    'F': [0x7E, 0x0A, 0x0A, 0x0A, 0x02],
    'G': [0x3C, 0x42, 0x4A, 0x4A, 0x38],
    'H': [0x7E, 0x08, 0x08, 0x08, 0x7E],
    'I': [0x00, 0x42, 0x7E, 0x42, 0x00],
    'J': [0x20, 0x40, 0x40, 0x3E, 0x00],
    'K': [0x7E, 0x08, 0x14, 0x22, 0x40],
    'L': [0x7E, 0x40, 0x40, 0x40, 0x00],
    'M': [0x7E, 0x02, 0x0C, 0x02, 0x7E],
    'N': [0x7E, 0x04, 0x08, 0x10, 0x7E],
    'O': [0x3C, 0x42, 0x42, 0x42, 0x3C],
    'P': [0x7E, 0x0A, 0x0A, 0x0A, 0x04],
    'Q': [0x3C, 0x42, 0x52, 0x22, 0x5C],
    'R': [0x7E, 0x0A, 0x1A, 0x2A, 0x44],
    'S': [0x24, 0x4A, 0x4A, 0x4A, 0x30],
    'T': [0x02, 0x02, 0x7E, 0x02, 0x02],
    'U': [0x3E, 0x40, 0x40, 0x40, 0x3E],
    'V': [0x1E, 0x20, 0x40, 0x20, 0x1E],
    'W': [0x7E, 0x20, 0x10, 0x20, 0x7E],
    'X': [0x42, 0x24, 0x18, 0x24, 0x42],
    'Y': [0x06, 0x08, 0x70, 0x08, 0x06],
    'Z': [0x42, 0x62, 0x52, 0x4A, 0x46],

    '0': [0x3C, 0x42, 0x42, 0x42, 0x3C],
    '1': [0x00, 0x44, 0x7E, 0x40, 0x00],
    '2': [0x64, 0x52, 0x52, 0x52, 0x4C],
    '3': [0x24, 0x42, 0x4A, 0x4A, 0x34],
    '4': [0x18, 0x14, 0x12, 0x7E, 0x10],
    '5': [0x2E, 0x4A, 0x4A, 0x4A, 0x32],
    '6': [0x3C, 0x4A, 0x4A, 0x4A, 0x30],
    '7': [0x02, 0x02, 0x72, 0x0A, 0x06],
    '8': [0x34, 0x4A, 0x4A, 0x4A, 0x34],
    '9': [0x0C, 0x52, 0x52, 0x52, 0x3C],

    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    '.': [0x00, 0x60, 0x60, 0x00, 0x00],
    '!': [0x00, 0x7A, 0x00, 0x00, 0x00],
    '?': [0x04, 0x02, 0x52, 0x0A, 0x04],
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],
    '_': [0x40, 0x40, 0x40, 0x40, 0x40],

    'g': [0x4C, 0x52, 0x52, 0x52, 0x3E],
    'm': [0x7C, 0x04, 0x18, 0x04, 0x78],

    ':': [0x00, 0x00, 0x12, 0x12, 0x00]
    }

    if char in font_map:
        pixels = font_map[char]
        for i in range(5):
            byte_data = pixels[i]
            for j in range(8):
                set_pixel_in_buffer(x + i, y + j, (byte_data >> j) & 1)

# Writes text to the display buffer
def write_text_to_buffer(text):
    x_position = 0
    for char in text:
        render_character(x_position, 0, char)
        x_position += 6  # Move to next character position

# Updates the OLED with buffer content
def display_on_oled():
    send_command(SET_COL_RANGE)
    send_command(0)
    send_command(OLED_WIDTH - 1)
    send_command(SET_PAGE_RANGE)
    send_command(0)
    send_command((OLED_HEIGHT // 8) - 1)
    for i in range(len(display_buffer)):
        send_data(display_buffer[i])

#---------------------------------------------------------#
#          Code for Load Cell + HX711 board
#---------------------------------------------------------#

# Initialize variables
GAIN = 1  # Default gain setting
OFFSET = 0
SCALE = 1
TIME_CONSTANT = 0.25
FILTERED = 0

# Function to read raw data from HX711
def read():
    data_pin.irq(trigger=Pin.IRQ_FALLING, handler=None)
    # Wait until HX711 is ready
    for _ in range(500):
        if data_pin.value() == 0:
            break
        time.sleep_ms(1)
    else:
        raise OSError("Sensor does not respond")

    result = 0
    # Shift in data and gain & channel info
    for _ in range(24 + GAIN):
        state = disable_irq()
        clock_pin.value(True)
        clock_pin.value(False)
        enable_irq(state)
        result = (result << 1) | data_pin.value()

    # Shift back the extra bits
    result >>= GAIN

    # Check sign
    if result > 0x7FFFFF:
        result -= 0x1000000

    return result

# Function to tare the scale
def tare(times=100):
    weights = []

    for _ in range(times):  # measure weight 100 times
        raw_wt = read() * 0.001
        weight = raw_wt
        weights.append(weight)
        time.sleep(0.01)  # small delay between measurements

    avg_weight = sum(weights) / len(weights)  # calculate average
    return avg_weight

#---------------------------------------------------------#
#            Code for Stepper Motor
#---------------------------------------------------------#
# Using Nema 17 with the L2898N Driver

# Enable motor driver channels A and B
enable_pin_A.value(1)
enable_pin_B.value(1)

# Full-step sequence for a bipolar stepper motor, each array defines pin activation for one step
full_step_sequence = [
    [1, 0, 1, 0],  # Step 1
    [0, 1, 1, 0],  # Step 2
    [0, 1, 0, 1],  # Step 3
    [1, 0, 0, 1],  # Step 4
]

# Function to set the motor to a specific step in the sequence
def apply_motor_step(step_pin1, step_pin2, step_pin3, step_pin4):
    step_pin_IN1.value(step_pin1)
    step_pin_IN2.value(step_pin2)
    step_pin_IN3.value(step_pin3)
    step_pin_IN4.value(step_pin4)

# Rotate motor 360 degrees in clockwise direction
def rotate_clockwise(total_steps, delay_between_steps_ms):
    for current_step in range(total_steps):
        # Determine the correct step in the sequence
        sequence_step = current_step % len(full_step_sequence)
        
        # Set motor pins according to the current step in the sequence
        apply_motor_step(*full_step_sequence[sequence_step])
        
        # Delay between steps to control motor speed
        time.sleep_ms(delay_between_steps_ms)

# Rotate motor 360 degrees in counterclockwise direction
def rotate_counterclockwise(total_steps, delay_between_steps_ms):
    for current_step in range(total_steps):
        # Determine the correct step in the reversed sequence
        sequence_step = current_step % len(full_step_sequence)
        
        # Set motor pins for reverse motion
        apply_motor_step(*full_step_sequence[::-1][sequence_step])
        
        # Delay between steps to control motor speed
        time.sleep_ms(delay_between_steps_ms)
