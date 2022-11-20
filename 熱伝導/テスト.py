import os
import sys
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

from 源.駆動 import Ls350, K2182, K6220, K195, GPIB锁
from 源.源 import 日志, 热浴稳定, 温度计转换, 塞贝克系数

初始温度 = 40
終了温度 = 1
平均回数 = 3
降温間隔 = 2  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる
初始电流 = 5 * 10 ** -5  # 开始电流
期望温差 = 0.5  # 加熱による温度差、低温では小さくなる
初始点数 = 200

初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, 高侧表, 低侧表, 结果温度, 结果热导, 温差表, 电压时间表] = [[] for _ in range(9)]
线程锁1 = Lock()
ファイル名 = 'bt錯体3t'
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', '热浴', '热浴逆', 2]  # 通道，校正曲线，逆曲线，输出通道
低 = ['D', '热导左1T']
高 = ['C', '热导右1T']
K2182_1 = K2182(GPIB号=17)
K6220_1 = K6220(GPIB号=13)
K199_1 = K195(GPIB号=26)


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 测定():
    温升文件 = open(f'结果/噪声{ファイル名}低温{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                encoding='utf-8')
    with GPIB锁:
        K6220_1.K6.write('CALC3:FORC:STAT ON')
        K2182_1.K2.write(':sens:volt:auto on')
    热浴稳定(10, 热浴)

    for _ in range(500):
        小循环时间 = time.time()
        温差 = K2182_1.读电压() / 塞贝克系数(10)
        time.sleep(0.2)
        with 线程锁1:
            温差表.append(温差)
            电压时间表.append(小循环时间 - 初始时间)

    # 小循环初始时间 = time.time()

    with GPIB锁:
        K2182_1.K2.write(':sens:volt:rang:100')
        K6220_1.K6.write('CALC3:FORC:PATT 0')

    for _ in range(500):
        小循环时间 = time.time()
        低温侧 = 温度计转换(Ls350_1.读电阻(通道=低[0]), 低[1])
        高温侧 = 温度计转换(Ls350_1.读电阻(通道=高[0]), 高[1])
        with 线程锁1:
            高侧表.append(高温侧)
            低侧表.append(低温侧)
            高低时间表.append(小循环时间 - 初始时间)
    温升文件.write(str([电压时间表, 温差表, 高低时间表, 高侧表, 低侧表]))
    温升文件.flush()
    热浴稳定(1, 热浴)


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="热导测量")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-时间")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴侧曲线 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="温升")
        右图.setLabel(axis='left', text='温度/K')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高温侧曲线 = 右图.plot(高低时间表, 高侧表, pen='b', name='高', symbol='o', symbolBrush='b')
            低温侧曲线 = 右图.plot(高低时间表, 低侧表, pen='r', name='低', symbol='o', symbolBrush='r')

        结果图 = 窗口.addPlot(title="温升2")
        结果图.setLabel(axis='left', text='温度/K')
        结果图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(电压时间表, 温差表, pen='c', name='热导', symbol='o', symbolBrush='b')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(时间表, 温度表)
            高温侧曲线.setData(高低时间表, 高侧表)
            低温侧曲线.setData(高低时间表, 低侧表)
            结果曲线.setData(电压时间表, 温差表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
