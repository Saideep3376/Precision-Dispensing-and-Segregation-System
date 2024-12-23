from machine import Pin, disable_irq, enable_irq
import time

# Define pins
data_pin = Pin(16, Pin.IN, pull=Pin.PULL_DOWN)
clock_pin = Pin(17, Pin.OUT)

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

'''
# Simple Technique to tare the loadcell efficently and accurately

# Initial setup
sf = 1  # scaling factor to convert raw readings to grams
c = 0   # offset to tare

weights = []  # list to store weights

# Calibration(tare)
print("Don't put any weights")
for _ in range(100):  # measure weight 100 times
    raw_wt = read() * 0.001
    weight = raw_wt
    weights.append(weight)
    time.sleep_ms(50)  # small delay between measurements

avg_weight = sum(weights) / len(weights)  # calculate average
c = avg_weight

# Main loop to read weight and adjust based on tare weight
while True:
    weights = []  # list to store weights

    for _ in range(10):  # measure weight 10 times
        raw_wt = read() * 0.001
        weight = raw_wt 
        weights.append(weight)
        time.sleep_ms(50)  # small delay between measurements

    avg_weight = ((sum(weights) / len(weights)) - c) * (-0.500)  # calculate average
    print(f"Average Weight: {avg_weight:.1f} grams", end="    \r")
'''
