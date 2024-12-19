```python
from machine import I2C, Pin

# Initialize I2C on channel 0 using pins 12 (SDA) and 13 (SCL) for the OLED display
oled_i2c = I2C(0, scl=Pin(13), sda=Pin(12))

# OLED display configuration commands
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

# OLED screen dimensions
OLED_WIDTH = 128
OLED_HEIGHT = 64

# I2C address for the OLED screen, obtained by running 'oled_address.py'
I2C_ADDR = 0x3C

# Display buffer to store pixel data, each byte represents 8 vertical pixels
display_buffer = bytearray((OLED_HEIGHT // 8) * OLED_WIDTH)

# Send a command to the OLED screen
def send_command(cmd):
    temp_buf = bytearray([0x80, cmd]) 
    oled_i2c.writeto(I2C_ADDR, temp_buf)

# Send data to the OLED screen
def send_data(data):
    temp_buf = bytearray([0x40, data]) 
    oled_i2c.writeto(I2C_ADDR, temp_buf)

# Initialize the OLED display with a sequence of commands
def initialize_oled():
    init_sequence = [
        TURN_DISPLAY | 0x00,  # Turn off display
        SET_ADDR_MODE, 0x00,  # Set to horizontal address mode
        START_LINE_POS | 0x00,
        SET_REMAP | 0x01,  # Set column address remap
        SET_MUX, OLED_HEIGHT - 1,
        SET_COM_DIRECTION | 0x08,  # Set COM[N] to COM0 scan direction
        DISPLAY_OFFSET, 0x00,
        COM_PIN_CONFIG, 0x12,
        SET_CLK_DIV_RATIO, 0x80,
        SET_PRECHARGE_PERIOD, 0xf1,
        SET_VCOM_DESELECT, 0x30,  # Set deselect level
        SET_CONTRAST_LVL, 0xff,  # Set maximum contrast
        DISPLAY_ALL_PIXELS,  # Display RAM content
        DISPLAY_NORMAL,  # Set display to normal mode
        ENABLE_CHARGE_PUMP, 0x14,  # Enable charge pump
        TURN_DISPLAY | 0x01  # Turn on display
    ]
    for cmd in init_sequence:
        send_command(cmd)

# Clear the display buffer by setting all bytes to 0
def clear_buffer():
    for i in range(len(display_buffer)):
        display_buffer[i] = 0x00

# Set a single pixel in the display buffer
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

# Render a character at position (x, y) using a simple 5x8 font
def render_character(x, y, char):
    # Map character symbols to pixel data
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

# Write a string of text to the display buffer
def write_text_to_buffer(text):
    x_position = 0
    for char in text:
        render_character(x_position, 0, char)
        x_position += 6  # Move to the next character position

# Update the OLED display with the contents of the display buffer
def display_on_oled():
    send_command(SET_COL_RANGE)
    send_command(0)
    send_command(OLED_WIDTH - 1)
    send_command(SET_PAGE_RANGE)
    send_command(0)
    send_command((OLED_HEIGHT // 8) - 1)
    for i in range(len(display_buffer)):
        send_data(display_buffer[i])
```
