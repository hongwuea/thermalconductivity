import time
import pyvisa
from threading import Lock

print("仪器驱动文件被调用...__name__=" + __name__)
管理器 = pyvisa.ResourceManager()
GPIB锁 = Lock()


class Ls370:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电阻(self):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query("RDGR?"))


class Ls350:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电阻(self, 通道='B'):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"SRDG?{通道}"))

    def 读温度(self, 通道='B'):
        # time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"KRDG?{通道}"))

    def 读加热(self, 通道=2):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"HTR?{通道}"))

    def 读加热量程(self, 通道=2):
        time.sleep(0.1)
        with GPIB锁:
            return int(self.Ls3.query(f"RANGE?{通道}"))

    def 设加热量程(self, 通道=2, 量程=0):
        time.sleep(0.1)
        with GPIB锁:
            self.Ls3.write(f"RANGE{通道},{量程}")

    def 设温度(self, 值, 通道=2):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        time.sleep(0.1)
        with GPIB锁:
            self.Ls3.write(f"SETP{通道},{值}")

    def 读设温度(self, 通道=2):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"SETP?{通道}"))

    def 设PID(self, P, I=60, D=0, 通道=2):
        time.sleep(0.1)
        with GPIB锁:
            self.Ls3.write(f"PID,{通道},{P},{I},{D}")

    def 扫引控温(self, 目标温度=250, 扫引速度K每min=0.1, 加热=0):
        with GPIB锁:
            time.sleep(0.1)
            当前温度 = float(self.Ls3.query(f"KRDG? B"))
            time.sleep(0.1)
            self.Ls3.write(f'RAMP 2,0,0.1')
            time.sleep(0.1)
            self.Ls3.write(f'SETP 2,{当前温度:.5}')
            time.sleep(0.1)
            self.Ls3.write(f'RANGE 2,{int(加热)}')
            time.sleep(0.1)
            self.Ls3.write(f'RAMP 2,1,{扫引速度K每min}')
            time.sleep(0.1)
            self.Ls3.write(f'SETP 2,{目标温度}')

    def 扫引控温VTI(self, 目标温度=30, 扫引速度K每min=0.1, 加热=0):
        with GPIB锁:
            time.sleep(0.1)
            当前温度 = float(self.Ls3.query(f"KRDG? A"))
            time.sleep(0.1)
            self.Ls3.write(f'RAMP 1,0,0.1')
            time.sleep(0.1)
            self.Ls3.write(f'SETP 1,{当前温度:.5}')
            time.sleep(0.1)
            self.Ls3.write(f'RANGE 1,{int(加热)}')
            time.sleep(0.1)
            self.Ls3.write(f'RAMP 1,1,{扫引速度K每min}')
            time.sleep(0.1)
            self.Ls3.write(f'SETP 1,{目标温度}')


class Ls340:
    def __init__(self, GPIB号):
        self.Ls3 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读电阻(self, 通道='B'):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"SRDG?{通道}"))

    def 读温度(self, 通道='B'):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"KRDG?{通道}"))

    def 读加热(self, 通道=1):
        time.sleep(0.1)
        with GPIB锁:
            return float(self.Ls3.query(f"HTR?{通道}"))

    def 读加热量程(self, 通道=1):
        time.sleep(0.1)
        with GPIB锁:
            return int(self.Ls3.query(f"RANGE?{通道}"))

    def 设加热量程(self, 通道=1, 量程=0):
        time.sleep(0.1)
        with GPIB锁:
            self.Ls3.write(f"RANGE{通道},{量程}")

    def 设温度(self, 值, 通道=1):  # 这里注意用4.1E1这种科学计数法会让340不识别，默认的17位浮点数即可
        time.sleep(0.1)
        with GPIB锁:
            self.Ls3.write(f"SETP{通道},{值}")

    def 设PID(self, P, I=60, D=0, 通道=1):
        time.sleep(0.1)
        with GPIB锁:
            self.Ls3.write(f"PID,{通道},{P},{I},{D}")

    def 扫引控温(self, 目标温度=50, 扫引速度K每min=1, 加热=3):
        time.sleep(0.1)
        with GPIB锁:
            当前温度 = float(self.Ls3.query(f"KRDG? B"))
            self.Ls3.write(f'RAMP 1,0,{扫引速度K每min}')
            self.Ls3.write(f'SETP 1,{当前温度}')
            self.Ls3.write(f'RANGE {加热}')
            self.Ls3.write(f'RAMP 1,1,{扫引速度K每min}')
            self.Ls3.write(f'SETP 1,{目标温度}')


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
        return 结果

    def 触发读电压2(self):
        with GPIB锁:
            return float(self.K2.query(":fetch?"))

    def REL変更(self):
        # with GPIB锁:
        #     self.K2.write(':sens:volt:ref:stat OFF')
        # time.sleep(0.1)
        with GPIB锁:
            self.K2.write(':sens:volt:ref:acq')
        # time.sleep(0.1)
        with GPIB锁:
            self.K2.write(':sens:volt:ref:stat ON')

    def RELOFF(self):
        with GPIB锁:
            self.K2.write(':sens:volt:ref:stat OFF')

    def 读REL状態(self):
        with GPIB锁:
            return float(self.K2.query(':sens:volt:ref:stat?'))

    def 读REL(self):
        with GPIB锁:
            return float(self.K2.query(":sens:volt:ref?"))

    def ゲイン変更(self, ゲイン):
        with GPIB锁:
            self.K2.write(f':OUTPut:GAIN {ゲイン}')
            print('ゲイン変更')
            print(self.K2.query(":OUTPut:GAIN?"))

    def 设ゲイン(self, ゲイン):
        with GPIB锁:
            self.K2.write(f':OUTPut:GAIN {ゲイン}')

    def 读ゲイン(self):
        with GPIB锁:
            return float(self.K2.query(":OUTPut:GAIN?"))

    def 设レンジ(self, レンジ):
        with GPIB锁:
            self.K2.write(f':sens:volt:RANGe {レンジ}')

    def 读レンジ(self):
        with GPIB锁:
            return float(self.K2.query(":sens:volt:RANGe?"))

    def 设頻度(self, PLC):
        with GPIB锁:
            self.K2.write(f':sens:volt:nplc {PLC}')

    def 读頻度(self):
        with GPIB锁:
            return float(self.K2.query(":sens:volt:nplc?"))

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


class K199:
    def __init__(self, GPIB号):
        self.K2 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读電流(self):
        with GPIB锁:
            return float(self.K2.query("").split("NDCI")[1])


class K6220:
    def __init__(self, GPIB号):
        self.K6 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 设电流(self, 电流):
        with GPIB锁:
            self.K6.write(':CURR:RANG:AUTO OFF')
            if 电流:
                self.K6.write(':CURR:RANG %E' % 电流)
            self.K6.write(":CURR %E" % 电流)

    def 设電流(self, 電流):
        with GPIB锁:
            self.K6.write(f':Current {電流}')

    def 读電流(self):
        with GPIB锁:
            return float(self.K6.query(":Current?"))

    def 读レンジ(self):
        with GPIB锁:
            return float(self.K6.query("CURRent:RANGe?"))

    def 设レンジ(self, レンジ):
        with GPIB锁:
            self.K6.write(f'CURRent:RANGe {レンジ}')


class K6221:
    def __init__(self, GPIB号):
        self.K6 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 设電流(self, 電流):
        with GPIB锁:
            self.K6.write(f':Current {電流}')

    def 读電流(self):
        with GPIB锁:
            return float(self.K6.query(":Current?"))

    def 读レンジ(self):
        with GPIB锁:
            return float(self.K6.query("CURRent:RANGe?"))

    def 设レンジ(self, レンジ):
        with GPIB锁:
            self.K6.write(f'CURRent:RANGe {レンジ}')

    def 读出力(self):
        with GPIB锁:
            return float(self.K6.query("OUTPut:STATe?"))

    def 设出力(self, 出力):
        with GPIB锁:
            self.K6.write(f'OUTPut:STATe {出力}')


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
    字典 = {
        'X': 1,
        'Y': 2,
        'R': 3,
        'θ': 4,
    }

    def __init__(self, GPIB号) -> object:
        self.SR8 = 管理器.open_resource(f'GPIB0::{GPIB号}::INSTR')

    def 读取(self, 通道):
        with GPIB锁:
            return float(self.SR8.query(f"OUTP?{self.字典[通道]}"))

    def 设频率(self, 频率):
        with GPIB锁:
            self.SR8.write(f"FREQ {频率}")

    # def 读频率(self):
    #     with GPIB锁:
    #         return float(self.SR8.query(f"FREQ?"))

    def 读频率(self):
        with GPIB锁:
            return float(self.SR8.query('FREQ?\n'))

    def リザーブ変更(self, リザーブ):  # 0だとminになる
        with GPIB锁:
            self.SR8.write(f"RSRV {リザーブ}")
            print('リザーブ変更')
            print(float(self.SR8.query('RSRV?\n')))

    def レンジ変更(self, レンジ):
        with GPIB锁:
            self.SR8.write(f"SENS {レンジ}")
            print('レンジ変更')
            print(float(self.SR8.query('SENS?\n')))

    def 自動調整(self):
        STB3 = float(self.SR8.query('*STB?3\n'))
        STB6 = float(self.SR8.query('*STB?6\n'))

        if STB3 and STB6 == 1:
            LIAS0 = float(self.SR8.query('LIAS?0\n'))
            LIAS2 = float(self.SR8.query('LIAS?2\n'))

            if LIAS0 == 1 and LIAS2 == 0:
                RSRV = float(self.SR8.query('RSRV?\n'))
                RSRV = RSRV + 1
                self.SR8.write(f'RSRV {RSRV}')

                if RSRV >= 3:
                    SENS = float(self.SR8.query('SENS?\n'))
                    SENS = SENS + 1
                    self.SR8.write(f'SENS {SENS}')
                    self.SR8.write('RSRV 0')
                time.sleep(25)

            if LIAS2 == 1:
                SENS = float(self.SR8.query('SENS?\n'))
                SENS = SENS + 1
                self.SR8.write(f'SENS {SENS}')
                self.SR8.write('RSRV 0')
                time.sleep(25)

        self.SR8.write('*CLS')
        time.sleep(3)


if __name__ == '__main__':
    print(管理器.list_resources())
    計測器 = 管理器.open_resource(f'GPIB0::13::INSTR')
    print(計測器.query("*IDN?"))
