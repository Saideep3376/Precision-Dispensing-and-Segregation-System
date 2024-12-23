from machine import Pin, SoftI2C

i2c = SoftI2C(scl = Pin(13), sda = Pin(12))

print('I2C Scanner: ')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c devices found!")
else:
  print("i2c devices found: ", len(devices))
  for device in devices: 
    print('I2C hexdecimal address: ', hex(device))
