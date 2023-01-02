import time
from threading import Thread, Lock
import pyqtgraph as pg
import os
import numpy as np

from 源.駆動 import Ls350, K6220, SR850, GPIB锁
from 源.源 import 温度计转换

励起电压 = 1e-3
初始时间 = time.time()
数据表 = [时间表, 温度表, XY时间表, X表, Y表] = [[] for _ in range(5)]
数据表2 = [C1表, 温度1表, C2表, 温度2表] = [[] for _ in range(4)]
线程锁1 = Lock()
ファイル名 = '容量測定自然降温'
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', '热浴', '热浴逆', 2]  # 通道，校正曲线，逆曲线，输出通道
# 低 = ['D', '热导左1T']
# 高 = ['C', '热导右1T']
# K2182_1 = K2182(GPIB号=17)
K6220_1 = K6220(GPIB号=13)
# K199_1 = K195(GPIB号=26)
SR850_1 = SR850(GPIB号=8)


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 测定():
    K6220_1.K6.write('CALC3:FORC:STAT ON')
    while 1:
        with GPIB锁:
            K6220_1.K6.write('CALC3:FORC:PATT 15')
        time.sleep(10)
        for _ in range(100):
            小循环时间 = time.time()
            X = SR850_1.读取('X')
            time.sleep(0.2)
            Y = SR850_1.读取('Y')
            time.sleep(0.2)
            with 线程锁1:
                X表.append(X)
                Y表.append(Y)
                XY时间表.append(小循环时间 - 初始时间)
        温度 = np.mean(温度表[-15::])
        电容 = -1 / (2 * np.pi * 1000 * 1E-3 * (1 / complex(float(np.mean(X表)), float(np.mean(Y表)))).imag)
        with 线程锁1:
            C1表.append(电容)
            温度1表.append(温度)
        过程文件.write(str([X表, Y表]))
        X表.clear()
        Y表.clear()
        XY时间表.clear()

        with GPIB锁:
            K6220_1.K6.write('CALC3:FORC:PATT 0')
        time.sleep(10)
        for _ in range(100):
            小循环时间 = time.time()
            X = SR850_1.读取('X')
            time.sleep(0.2)
            Y = SR850_1.读取('Y')
            time.sleep(0.2)
            with 线程锁1:
                X表.append(X)
                Y表.append(Y)
                XY时间表.append(小循环时间 - 初始时间)
        温度 = np.mean(温度表[-15::])
        电容 = - 1 / (2 * np.pi * 1000 * 励起电压 * (1 / complex(float(np.mean(X表)), float(np.mean(Y表)))).imag)
        with 线程锁1:
            C2表.append(电容)
            温度2表.append(温度)
        过程文件.write(str([X表, Y表]) + '\n')
        结果文件.write(f'{温度1表[-1]}\t{C1表[-1]}\t{温度2表[-1]}\t{C2表[-1]}\n')
        结果文件.flush()
        X表.clear()
        Y表.clear()
        XY时间表.clear()


if __name__ == '__main__':
    if not os.path.exists(r'容量測定'):
        os.makedirs(r'容量測定')
    过程文件 = open(f'容量測定/過程{ファイル名}{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                encoding='utf-8')
    结果文件 = open(f'容量測定/結果{ファイル名}{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                encoding='utf-8')
    结果文件.write('{温度1表[-1]}\t{C1表[-1]}\t{温度2表[-1]}\t{C2表[-1]}\n')
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

        右图 = 窗口.addPlot(title="原始数据")
        右图.setLabel(axis='left', text='电流/A')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            X曲线 = 右图.plot(XY时间表, X表, pen='b', name='电流X', symbol='o', symbolBrush='b')
            Y曲线 = 右图.plot(XY时间表, Y表, pen='b', name='电流Y', symbol='o', symbolBrush='r')

        结果图 = 窗口.addPlot(title="结果")
        结果图.setLabel(axis='left', text='电容/F')
        结果图.setLabel(axis='bottom', text='温度/K', )
        结果图.addLegend()
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(温度1表, C1表, pen='c', name='电容1', symbol='o', symbolBrush='b')
            结果曲线2 = 结果图.plot(温度2表, C2表, pen='c', name='电容2', symbol='o', symbolBrush='r')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(时间表, 温度表)
            X曲线.setData(XY时间表, X表)
            Y曲线.setData(XY时间表, Y表)
            结果曲线.setData(温度1表, C1表)
            结果曲线2.setData(温度2表, C2表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()

    过程文件.close()
    结果文件.close()
    # 热浴稳定(1, 热浴)
    print('終わり')
