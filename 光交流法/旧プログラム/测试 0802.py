from scipy.optimize import curve_fit
import os
import sys
import time
from threading import Thread, Lock
import traceback

import numpy as np
import pyqtgraph as pg

from 源.驱动 import Ls340, K2182, K6220
from 源.源 import 日志, 温度计转换

线程锁1 = Lock()
Ls340_1 = Ls340(GPIB号=18)  # 350温控器约定：C=低温计，D=高温计，A,B使用非翻转的10mV激励，CD使用翻转1mV激励
Ls340_2 = Ls340(GPIB号=19)
K2182_1 = K2182(GPIB号=7)
K6220_1 = K6220(GPIB号=12)
Ls350加热环路号 = 2
初始电流 = 5E-3  # 電流/A
X表, Y表, R表 = [], [], []
时间表, 温度表 = [], []


# def 塞贝克系数(塞_温度):  # 温度→V/K　ゼーベック係数
#     return 1E-06 * (1E-06 * 塞_温度 ** 3 - 0.0011 * 塞_温度 ** 2 + 0.398 * 塞_温度 + 1.2598)

def 塞贝克系数(塞_温度):  # 温度→V/K
    a3 = 2.034140227
    a2 = -1.341522423
    a1 = 0.432616895

    return 1E-06 * (1E-06 * a3 * 塞_温度 ** 3 + 1E-03 * a2 * 塞_温度 ** 2 + a1 * 塞_温度)

開始 = time.time()

def 测量():
    初始 = time.time()
    电流 = 初始电流
    Ls340_1.扫引控温(目标温度=160, 扫引速度K每min=0.2, 加热=3)  # 目標温度、変化速度、ヒーターのレンジを驱动.pyに入力
    # Ls340_2.扫引控温(目标温度=200,扫引速度K每min=1, 加热=5)
    K2182_1.触发切换('OFF')
    电压表, 相位表 = [], []
    if not os.path.exists(r'结果'):
        os.makedirs(r'结果')
    结果 = open(f'结果/{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}0.1HzI35mA.txt', mode='a', encoding='utf-8')
    结果.write('时间秒\t温度\tX表\tY表\n')
    if not os.path.exists(r'日志'):
        os.makedirs(r'日志')
    sys.stdout = 日志(f'日志/热导测量日志{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}0.1HzI35mA.log')
    while 1:
        时间1 = time.time()
        # if 时间1 - 開始 >= 36000:
        #     Ls340_1.扫引控温(目标温度=120, 扫引速度K每min=0, 加热=3)
        #     sys.exit()
        K6220_1.设电流(电流)
        time.sleep(0.03)
        热浴 = Ls340_1.读温度()
        # print(time.time() - 时间1)
        for i in range(9):
            try:
                time.sleep(0.5 * (i + 1) - (time.time() - 时间1))
            except:
                traceback.print_exc()
            else:
                电压表.append(K2182_1.触发读电压())
                相位表.append(i + 1)
        try:
            time.sleep(0.5 * 10 - (time.time() - 时间1))
        except:
            traceback.print_exc()
        K6220_1.设电流(0)
        for i in range(9):
            try:
                time.sleep(0.5 * (i + 11) - (time.time() - 时间1))
            except:
                traceback.print_exc()
            else:
                电压表.append(K2182_1.触发读电压())
                相位表.append(i + 11)
        with 线程锁1:
            X表.append(sum(np.sin(2 * np.pi * np.array(相位表) / 20) * np.array(电压表)) / 18)
            Y表.append(-sum(np.cos(2 * np.pi * np.array(相位表) / 20) * np.array(电压表)) / 18)
            R表.append((X表[-1] ** 2 + Y表[-1] ** 2) ** 0.5)
            时间表.append(时间1 - 初始)
            温度表.append(热浴)
        结果.write(f'{time.time() - 初始}\t{热浴}\t{X表[-1]}\t{Y表[-1]}\n')
        结果.flush()
        print(电压表)
        电压表.clear()
        相位表.clear()
        try:
            time.sleep(0.5 * 20 - (time.time() - 时间1))
        except:
            traceback.print_exc()



if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="鉴相热容测量结果")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        # 左图 = 窗口.addPlot(title="同相曲线")
        # 左图.setLabel(axis='left', text='信号/Volt')
        # 左图.setLabel(axis='bottom', text='温度/K', )
        # if 1:  # 窗口内曲线4级
        #     同相X = 左图.plot(温度表, X表, pen='b', name='同相X', symbol='o', symbolBrush='b')

        # 右图 = 窗口.addPlot(title="正交曲线")
        # 右图.setLabel(axis='left', text='信号/Volt')
        # 右图.setLabel(axis='bottom', text='温度/K', )
        # if 1:  # 窗口内曲线4级
        #     正交Y = 右图.plot(温度表, Y表, pen='b', name='正交Y', symbol='o', symbolBrush='b')

        右图2 = 窗口.addPlot(title="R曲线")
        右图2.setLabel(axis='left', text='信号/Volt')
        右图2.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            R = 右图2.plot(温度表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')

        温度图 = 窗口.addPlot(title="温度-时间")
        温度图.setLabel(axis='left', text='温度/K')
        温度图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            温度曲线 = 温度图.plot(时间表, 温度表, pen='b', name='温度', symbol='o', symbolBrush='b')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            # 同相X.setData(温度表, X表)
            # 正交Y.setData(温度表, Y表)
            R.setData(温度表, R表)
            温度曲线.setData(时间表, 温度表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测量).start()
    pg.mkQApp().exec_()
