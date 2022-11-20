import serial
import time

print("Open Port")
串口 = serial.Serial("COM4", 9600, timeout=1)

i = 0

# ser.write('*IDN?\n'.encode())
# print(ser.read(size=100))
串口.write('G'.encode())
print(串口.read(size=100))
# for _ in range(10):
#     print(ser.read(size=100))
# ser.write('SYSTem:LED:BRIGhtness:INCrease 1000\n'.encode())
# print()
串口.close()
