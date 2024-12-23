import machine
import time

# Define GPIO pins connected to the stepper motor through L298N driver
step_pin_IN1 = machine.Pin(3, machine.Pin.OUT)   # IN1 connected to GPIO3
step_pin_IN2 = machine.Pin(4, machine.Pin.OUT)   # IN2 connected to GPIO4
step_pin_IN3 = machine.Pin(6, machine.Pin.OUT)   # IN3 connected to GPIO6
step_pin_IN4 = machine.Pin(7, machine.Pin.OUT)   # IN4 connected to GPIO7
enable_pin_A = machine.Pin(2, machine.Pin.OUT)   # ENA for motor driver channel A, connected to GPIO2
enable_pin_B = machine.Pin(5, machine.Pin.OUT)   # ENB for motor driver channel B, connected to GPIO5

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
# Total steps for a full 360-degree rotation (based on motor specifications)
# Adjust for motor specifics (e.g., typical NEMA 17)

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
