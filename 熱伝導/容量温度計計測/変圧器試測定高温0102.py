import os
import pyqtgraph as pg
import time
from threading import Thread, Lock
import numpy as np

from 源.源 import 温度计转换
from 源.駆動 import Ls350, K6220, SR850

初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, R表, 结果温度, 结果热导] = [[] for _ in range(6)]

线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', '热浴', '热浴逆', 2]

SR850_1 = SR850(GPIB号=8)
K2182_1 = SR850_1
K2182_1.读电压 = SR850_1.读取('R')
K6220_1 = K6220(GPIB号=13)


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 测定():
    if not os.path.exists(r'结果'):
        os.makedirs(r'结果')
    过程文件 = open(f'结果/电容过程{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
    过程文件.write('时间秒\tX\tY\n')
    平均文件 = open(f'结果/电容平均{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
    平均文件.write('温度K\tX1\tX2\tY1\tY2\n')
    print("\n创建文件成功\n")
    time.sleep(3)
    while 1:
        X表, Y表 = [], []
        K6220_1.设电流(0)
        for _ in range(200):
            小循环时间 = time.time()
            X = SR850_1.读取('X')
            X表.append(X)
            time.sleep(0.5)
            Y = SR850_1.读取('Y')
            Y表.append(Y)
            time.sleep(0.5)
            with 线程锁1:
                R表.append((X ** 2 + Y ** 2) ** 0.5)
                高低时间表.append(小循环时间 - 初始时间)

        K6220_1.设电流(1E-4)
        for _ in range(200):
            小循环时间 = time.time()
            X = SR850_1.读取('X')
            X表.append(X)
            time.sleep(0.5)
            Y = SR850_1.读取('Y')
            Y表.append(Y)
            time.sleep(0.5)
            with 线程锁1:
                R表.append((X ** 2 + Y ** 2) ** 0.5)
                高低时间表.append(小循环时间 - 初始时间)
        for i in range(400):
            过程文件.write(f'{高低时间表[-(400 - i)]}\t{X表[i]}\t{Y表[i]}\n')
        过程文件.flush()
        平均文件.write(f'{np.mean(温度表[-10::])}\t{np.mean(X表[180:199:1])}\t{np.mean(X表[380:399:1])}'
                   f'\t{np.mean(Y表[180:199:1])}\t{np.mean(Y表[380:399:1])}\n')
        平均文件.flush()


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
            热浴侧曲线 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')

        右图 = 窗口.addPlot(title="R值")
        右图.setLabel(axis='left', text='R值/A')
        右图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            高侧曲线 = 右图.plot(高低时间表, R表, pen='b', name='高', symbol='o', symbolBrush='b')

        # 结果图 = 窗口.addPlot(title="热导-温度")
        # 结果图.setLabel(axis='left', text='热导/WK^-1')
        # 结果图.setLabel(axis='bottom', text='温度/K', )
        # if 1:  # 窗口内曲线4级
        #     结果曲线 = 结果图.plot(结果温度, 结果热导, pen='c', name='热导', symbol='o', symbolBrush='c')
        # # 窗口.nextRow()
        # # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(时间表, 温度表)
            高侧曲线.setData(高低时间表, R表)
            # 结果曲线.setData(结果温度, 结果热导)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()

    # ここで全データ保存機能追加？
