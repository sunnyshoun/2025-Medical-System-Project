import serial, time

ser = serial.Serial(port='/dev/ttyS0')

while True:
    print(ser.readable())
    if ser.readable():
        print(ser.readline().decode())
    ser.write(b'ok\n')