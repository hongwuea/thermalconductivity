import os
import sys
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

from 源.駆動 import Ls350, SR850
from 源.源 import 温度计转换, 热浴稳定

初始温度 = 1.8
終了温度 = 10
降温間隔 = -1  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる
平均点数 = 200
激励电压 = 1e-3
文件名 = '容量磁场测定'
初始时间 = time.time()
数据表 = [温度表, 热浴时间表, 电容表, 电容温度表, X表, Y表, XY时间表] = [[] for _ in range(7)]
线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)  # 350温控器约定：C=低温计，D=高温计，A,B使用非翻转的10mV激励，CD使用翻转1mV激励
SR850_1 = SR850(GPIB号=8)
热浴温度計 = ['B', '热浴', '热浴逆', 2]


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴温度計[0]), 热浴温度計[1])
        time.sleep(3)
        with 线程锁1:
            温度表.append(热浴温度)
            热浴时间表.append(time.time() - 初始时间)


def 测定():
    设定温度 = 初始温度
    if not os.path.exists(r'容量校准结果'):
        os.makedirs(r'容量校准结果')
    结果文件 = open(f'容量校准结果/{文件名}{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
    结果文件.write('时间秒\t热浴温度\t电容值F\n')
    print("\n创建文件成功\n")
    Ls350_1.设加热量程(量程=1)
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        print('---------------------少女祈禱中。。。--------------------')
        热浴稳定(设定温度, 热浴温度計)

        for i in range(平均点数):
            小循环时间 = time.time()
            X = SR850_1.读取('X')
            time.sleep(0.2)
            Y = SR850_1.读取('Y')
            time.sleep(0.2)
            with 线程锁1:
                X表.append(X)
                Y表.append(Y)
                XY时间表.append(小循环时间 - 初始时间)
        # 温度 = np.mean(温度表[-15::])

        电容值 = 1 / (2 * np.pi * 1000 * 激励电压 * (1 / complex(float(np.mean(X表)), float(np.mean(Y表)))).imag)
        X表.clear()
        Y表.clear()
        结果文件.write(f'{time.time() - 初始时间}\t{设定温度}\t{电容值}\n')
        结果文件.flush()
        电容温度表.append(np.mean(温度表[-15::]))
        电容表.append(电容值)

        设定温度 = 设定温度 - 降温間隔 * min(1, 设定温度 / 40)
    热浴稳定(1, 热浴温度計)


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="容量校正")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-时间")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴 = 左图.plot(热浴时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="容量値")
        右图.setLabel(axis='left', text='容量/F')
        右图.setLabel(axis='bottom', text='温度/K', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            电容 = 右图.plot(电容温度表, 电容表, pen='g', name='热浴', symbol='o', symbolBrush='b')


    def 定时更新f():
        with 线程锁1:
            热浴.setData(热浴时间表, 温度表)
            电容.setData(电容温度表, 电容表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
