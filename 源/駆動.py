import time
import pyvisa
from multiprocessing import Event

print("仪器驱动文件被调用...__name__=" + __name__)
管理器 = pyvisa.ResourceManager()
占用 = Event()
占用.set()


def 多线程调度器(函数):
    def 闭包(*args, **kwargs):
        占用.wait()
        time.sleep(0.1)
        占用.wait()
        占用.clear()
        返回 = 函数(*args, **kwargs)
        占用.set()
        return 返回

    return 闭包


class Ls370:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    @多线程调度器
    def 读电阻(self):
        return float(self.Ls3.query("RDGR?"))


class Ls350:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    @多线程调度器
    def 读电阻(self, 通道='B'):
        return float(self.Ls3.query(f"SRDG?{通道}"))

    @多线程调度器
    def 读温度(self, 通道='B'):
        return float(self.Ls3.query(f"KRDG?{通道}"))

    @多线程调度器
    def 读加热(self, 通道=2):
        return float(self.Ls3.query(f"HTR?{通道}"))

    @多线程调度器
    def 读加热量程(self, 通道=2):
        return int(self.Ls3.query(f"RANGE?{通道}"))

    @多线程调度器
    def 设加热量程(self, 通道=2, 量程=0):
        self.Ls3.write(f"RANGE{通道},{量程}")

    @多线程调度器
    def 设温度(self, 值, 通道=2):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        self.Ls3.write(f"SETP{通道},{值}")

    @多线程调度器
    def 设PID(self, P, I=60, D=0, 通道=2):
        self.Ls3.write(f"PID,{通道},{P},{I},{D}")

    @多线程调度器
    def 扫引控温(self, 目标温度=250, 扫引速度K每min=0.1, 加热=0):
        # 当前温度 = float(self.Ls3.query(f"KRDG? B"))
        # self.Ls3.write(f'RAMP 1,0,{扫引速度K每min}')
        # self.Ls3.write(f'SETP 1,{当前温度}')
        self.Ls3.write(f'RANGE {加热}')
        self.Ls3.write(f'RAMP 2,1,{扫引速度K每min}')
        self.Ls3.write(f'SETP 2,{目标温度}')


class Ls340:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    @多线程调度器
    def 读电阻(self, 通道='B'):
        return float(self.Ls3.query(f"SRDG?{通道}"))

    @多线程调度器
    def 读温度(self, 通道='B'):
        return float(self.Ls3.query(f"KRDG?{通道}"))

    @多线程调度器
    def 读加热(self, 通道=1):
        return float(self.Ls3.query(f"HTR?{通道}"))

    @多线程调度器
    def 读加热量程(self, 通道=1):
        return int(self.Ls3.query(f"RANGE?{通道}"))

    @多线程调度器
    def 设加热量程(self, 通道=1, 量程=0):
        self.Ls3.write(f"RANGE{通道},{量程}")

    @多线程调度器
    def 设温度(self, 值, 通道=1):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        self.Ls3.write(f"SETP{通道},{值}")

    @多线程调度器
    def 设PID(self, P, I=60, D=0, 通道=1):
        self.Ls3.write(f"PID,{通道},{P},{I},{D}")

    @多线程调度器
    def 扫引控温(self, 目标温度=50, 扫引速度K每min=1, 加热=3):
        当前温度 = float(self.Ls3.query(f"KRDG? B"))
        self.Ls3.write(f'RAMP 1,0,{扫引速度K每min}')
        self.Ls3.write(f'SETP 1,{当前温度}')
        self.Ls3.write(f'RANGE {加热}')
        self.Ls3.write(f'RAMP 1,1,{扫引速度K每min}')
        self.Ls3.write(f'SETP 1,{目标温度}')


class K2182:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    @多线程调度器
    def 读电压(self):
        return float(self.K2.query(":DATA:FRESH?"))

    def 触发切换(self, 开关):
        self.K2.write(f':initiate:continuous {开关}')

    def 触发读电压(self):
        return float(self.K2.query(":read?"))


class K6220:
    def __init__(self, GPIB号):
        self.K6 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    @多线程调度器
    def 设电流(self, 电流):
        self.K6.write(':CURR:RANG:AUTO OFF')
        if 电流:
            self.K6.write(':CURR:RANG %E' % 电流)
        self.K6.write(":CURR %E" % 电流)


class SR850:
    字典 = {
        'X': 1,
        'Y': 2,
        'R': 3,
        'θ': 4,
    }

    def __init__(self, GPIB号):
        self.SR8 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    @多线程调度器
    def 读取(self, 通道):
        return float(self.SR8.query(f"OUTP?{self.字典[通道]}"))
