from lib151 import *
import time

initialize_oled()
clear_buffer()

total_weight = 0

# Initialize load cell and clear any offset
initial_offset_red = tare()
weights = []

# Initial Calibration Phase
for _ in range(10):
    raw_wt = read() * 0.001
    weights.append(raw_wt)
    time.sleep(0.01)  # Consistent delay for stability

weight = ((sum(weights) / len(weights)) - initial_offset_red) * (-0.500)
print(f"Calibration done! Average Offset Weight: {weight:.1f} grams")

# Begin main weight measurement cycle
for _ in range(5):
    # Red Cycle
    print("STARTING RED CYCLE")
    open_red()

    # Measure until the weight of the red solution reaches 5 grams
    while weight < 4.8:  # Target 5 grams for Red Cycle
        drive_forward(70)
        weights = []

        for _ in range(5):  # Measure weight 5 times
            raw_wt = read() * 0.001
            weights.append(raw_wt)
            time.sleep(0.001)  # Consistent delay for stability

        weight = ((sum(weights) / len(weights)) - initial_offset_red) * (-0.500)
        #print(f"Red Solution Weight: {weight:.1f} g")
        write_text_to_buffer("TEAM IC2                                   WEIGHT: {:.1f} g".format(weight))
        display_on_oled()

    drive_reverse(100)
    time.sleep(15)
    close_red()
    halt()

    total_weight += weight  # Initialize total weight with red cycle weight
    print(f"Total Weight after Red Cycle: {total_weight:.1f} g")
    write_text_to_buffer("TEAM IC2                                   TOTAL WEIGHT: {:.1f} g".format(total_weight))
    display_on_oled()
    clear_buffer()

    rotation_speed_delay_ms = 3
    total_steps_360 = 200

    # Rotate to blue solution

    for _ in range(9):
        rotate_counterclockwise(total_steps_360, rotation_speed_delay_ms)

    # Blue Cycle
    print("Starting Blue Cycle")
    open_blue()

    weights = []  # Reset weights for the new cycle
    initial_offset_blue = tare()  # Re-tare for the blue cycle

    for _ in range(10):  # measure weight 10 times
        raw_wt = read() * 0.001
        weights.append(raw_wt)
        time.sleep(0.001)  # small delay between measurements

    weight_blue = ((sum(weights) / len(weights)) - initial_offset_blue) * (-0.500)  # calculate average
    print(f"Average Weight: {weight:.1f} grams", end="    \r")

    # Measure until the weight of the blue solution reaches 10 grams
    while weight_blue < 9.6:  # Target 10 grams for Blue Cycle
        drive_forward(70)
        weights = []

        for _ in range(10):
            raw_wt = read() * 0.001
            weights.append(raw_wt)
            time.sleep(0.001)

        weight_blue = ((sum(weights) / len(weights)) - initial_offset_blue) * (-0.500)
        print(f"Blue Solution Weight: {weight_blue:.1f} g")
        write_text_to_buffer("TEAM IC2                                   WEIGHT: {:.1f} g".format(weight_blue))
        display_on_oled()

    drive_reverse(100)
    time.sleep(15)
    close_blue()
    halt()

    # Rotate back after blue cycle
    for _ in range(9):
        rotate_clockwise(total_steps_360, rotation_speed_delay_ms)


    # Update and print final total weight after both cycles
    total_weight += weight_blue
    print(f"Total Weight after Blue Cycle: {total_weight:.1f} mg")
    write_text_to_buffer("TEAM IC2                                   TOTAL WEIGHT: {:.1f} g".format(total_weight))
    display_on_oled()
    clear_buffer()

    # Final Red Cup Measurement
    weights = []
    initial_offset_red = tare()  # Re-tare for the final measurement

    for _ in range(10):
        raw_wt = read() * 0.001
        weights.append(raw_wt)
        time.sleep(0.01)

    weight = ((sum(weights) / len(weights)) - initial_offset_red) * (-0.500)
    print(f"Final Red Cup Average Weight: {weight:.1f} grams")
