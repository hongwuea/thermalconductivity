import time
import pyvisa
from threading import Lock

print("仪器驱动文件被调用...__name__=" + __name__)
管理器 = pyvisa.ResourceManager()
GPIB锁 = Lock()


class Ls370:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')
        print(self.Ls3.query("*IDN?"))

    def 读电阻(self, 通道=0):
        with GPIB锁:
            return float(self.Ls3.query("RDGR?").strip('#'))

    def 读温度(self, 通道=0):
        with GPIB锁:
            return float(self.Ls3.query(f"KRDG?"))

    def 设PID(self, P=20, I=60, D=0, 通道=0):
        with GPIB锁:
            self.Ls3.write(f"PID {P}, {I}, {D}")

    def 读加热(self, 通道=0):
        with GPIB锁:
            return float(self.Ls3.query(f"HTR?"))

    def 读加热量程(self, 通道=0):
        with GPIB锁:
            return int(self.Ls3.query(f"HTRRNG?"))

    def 设加热量程(self, 量程=0, 通道=0):  # range 0-8
        with GPIB锁:
            self.Ls3.write(f"HTRRNG {量程}")

    def 设温度(self, 值, 通道=0):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        with GPIB锁:
            self.Ls3.write(f"SETP {值:.6}")


class Ls350:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电阻(self, 通道='B'):
        with GPIB锁:
            return float(self.Ls3.query(f"SRDG? {通道}"))

    def 读温度(self, 通道='B'):
        with GPIB锁:
            return float(self.Ls3.query(f"KRDG? {通道}"))

    def 读加热(self, 通道=2):
        with GPIB锁:
            return float(self.Ls3.query(f"HTR? {通道}"))

    def 读加热量程(self, 通道=2):
        with GPIB锁:
            return int(self.Ls3.query(f"RANGE? {通道}"))

    def 设加热量程(self, 通道=2, 量程=0):
        with GPIB锁:
            self.Ls3.write(f"RANGE {通道},{量程}")

    def 设温度(self, 值, 通道=2):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        with GPIB锁:
            self.Ls3.write(f"SETP {通道},{值:.6}")

    def 设PID(self, P, I=60, D=0, 通道=2):
        with GPIB锁:
            self.Ls3.write(f"PID, {通道}, {P}, {I}, {D}")

    def 扫引控温(self, 目标温度=250, 扫引速度K每min=0.1, 加热=0):
        with GPIB锁:
            time.sleep(0.1)
            当前温度 = float(self.Ls3.query(f"KRDG? B"))
            time.sleep(0.1)
            self.Ls3.write(f'RAMP 2, 0, 0.1')
            time.sleep(0.1)
            self.Ls3.write(f'SETP 2, {当前温度:.5}')
            time.sleep(0.1)
            self.Ls3.write(f'RANGE 2, {int(加热)}')
            time.sleep(0.1)
            self.Ls3.write(f'RAMP 2, 1, {扫引速度K每min}')
            time.sleep(0.1)
            self.Ls3.write(f'SETP 2, {目标温度}')


class Ls340:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电阻(self, 通道='B'):
        with GPIB锁:
            return float(self.Ls3.query(f"SRDG? {通道}"))

    def 读温度(self, 通道='B'):
        with GPIB锁:
            return float(self.Ls3.query(f"KRDG? {通道}"))

    def 读加热(self, 通道=1):
        with GPIB锁:
            return float(self.Ls3.query(f"HTR? {通道}"))

    def 读加热量程(self, 通道=1):
        with GPIB锁:
            return int(self.Ls3.query(f"RANGE? {通道}"))

    def 设加热量程(self, 通道=1, 量程=0):
        with GPIB锁:
            self.Ls3.write(f"RANGE {量程}")

    def 设温度(self, 值, 通道=1):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        with GPIB锁:
            self.Ls3.write(f"SETP {通道}, {值:.6}")

    def 设PID(self, P, I=60, D=0, 通道=1):
        with GPIB锁:
            self.Ls3.write(f"PID {通道}, {P}, {I}, {D}")

    def 扫引控温(self, 目标温度=50, 扫引速度K每min=1, 加热=3):
        with GPIB锁:
            当前温度 = float(self.Ls3.query(f"KRDG? B"))
            self.Ls3.write(f'RAMP 1, 0, {扫引速度K每min}')
            self.Ls3.write(f'SETP 1, {当前温度}')
            self.Ls3.write(f'RANGE {加热}')
            self.Ls3.write(f'RAMP 1, 1, {扫引速度K每min}')
            self.Ls3.write(f'SETP 1, {目标温度}')


class K2182:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电压(self):
        with GPIB锁:
            return float(self.K2.query(":DATA:FRESH?"))

    def 触发切换(self, 开关):
        with GPIB锁:
            self.K2.write(f':initiate:continuous {开关}')

    def 触发读电压(self):
        with GPIB锁:
            return float(self.K2.query(":read?"))

    def 读通道2后切回(self):
        with GPIB锁:
            self.K2.write(':SENS:CHAN 2')
        time.sleep(0.5)
        with GPIB锁:
            结果 = float(self.K2.query(":DATA:FRESH?"))
            self.K2.write(':SENS:CHAN 1')
        time.sleep(0.5)
        return 结果

    def 读电压t(self):
        with GPIB锁:
            t = time.time()
            return float(self.K2.query(":DATA:FRESH?")), t


class K2400:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读数据(self):
        with GPIB锁:
            return self.K2.query(":READ?")


class K2001:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读数据(self):
        with GPIB锁:
            return float(self.K2.query("FETCh?").split("N")[0])


class K182:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电压(self):
        with GPIB锁:
            return float(self.K2.query("V").split("NDCV")[1])


class K195:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电压(self):
        with GPIB锁:
            return float(self.K2.query("X").split("NDCV")[1])


class K6220:
    def __init__(self, GPIB号):
        self.K6 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 设电流(self, 电流):
        with GPIB锁:
            self.K6.write(':CURR:RANG:AUTO OFF')
            if 电流:
                self.K6.write(':CURR:RANG %E' % 电流)
            self.K6.write(":CURR %E" % 电流)

    def 设电流t(self, 电流):
        with GPIB锁:
            self.K6.write(':CURR:RANG:AUTO OFF')
            if 电流:
                self.K6.write(':CURR:RANG %E' % 电流)
            t = time.time()
            self.K6.write(":CURR %E" % 电流)
            return t

    def 设电流t2(self, 电流):
        with GPIB锁:
            self.K6.write(':CURR:RANG:AUTO OFF')
            if 电流:
                self.K6.write(':CURR:RANG %E' % 电流)
            t = time.time()
            self.K6.write(f'Current {电流}')
            return t


class K220:
    def __init__(self, GPIB号):
        self.K6 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 设电流(self, 电流):
        with GPIB锁:
            self.K6.write("I%EX" % 电流)


class Y7651:
    def __init__(self, GPIB号):
        self.K6 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 设电流(self, 电流):  # 数字を変えるだけ、予めレンジとoutputと機能を選んでね。詳しくは説明書を
        with GPIB锁:
            self.K6.write(f"S{电流}E")


class SR850:
    字典 = {'X': 1, 'Y': 2, 'R': 3, 'θ': 4, }

    def __init__(self, GPIB号):
        self.SR8 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读取(self, 通道):
        with GPIB锁:
            return float(self.SR8.query(f"OUTP?{self.字典[通道]}"))

    def 设频率(self, 频率):
        with GPIB锁:
            self.SR8.write(f"FREQ {频率}")
