import os
import sys
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

from 源.駆動old import Ls350
from 源.源 import 日志, 温度计转换, 热浴稳定

初始温度 = 1.8
終了温度 = 40
降温間隔 = -10  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる
平均点数 = 200

初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, 高侧表, 低侧表, 结果温度, 结果热导] = [[] for _ in range(7)]
线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)  # 350温控器约定：C=低温计，D=高温计，A,B使用非翻转的10mV激励，CD使用翻转1mV激励

Ls350加热环路号 = 2


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道='B'), '热浴')
        time.sleep(3)
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)


def 测定():
    设定温度 = 初始温度
    if not os.path.exists(r'日志'):
        os.makedirs(r'日志')
    sys.stdout = 日志(f'日志/校正日志{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')
    if not os.path.exists(r'结果'):
        os.makedirs(r'结果')
    结果文件 = open(f'结果/温度计校准结果{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
    结果文件.write('时间秒\t热浴温度\t高侧\t低侧\n')
    print("\n创建文件成功\n")
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        print('---------------------少女祈禱中。。。--------------------')
        print(f'新温度循环')
        热浴稳定(设定温度, Ls350加热环路号)
        for i in range(平均点数):
            高_ = Ls350_1.读电阻(通道='C')
            time.sleep(0.1)
            低_ = Ls350_1.读电阻(通道='D')
            time.sleep(0.1)
            时间_ = time.time()
            with 线程锁1:
                高侧表.append(高_)
                低侧表.append(低_)
                高低时间表.append(时间_)
        高均 = np.mean(高侧表[-平均点数::])
        低均 = np.mean(低侧表[-平均点数::])
        print(f'高侧平均电阻{高均}Ω，低侧平均电阻{低均}Ω')
        结果文件.write(f'{time.time()}\t{设定温度}\t{高均}\t{低均}\n')
        结果文件.flush()

        设定温度 = 设定温度 - 降温間隔 * min(1, 设定温度 / 40)
    热浴稳定(1.8, Ls350加热环路号)


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
            热浴 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="抵抗値")
        右图.setLabel(axis='left', text='抵抗/ohm')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高 = 右图.plot(高低时间表, 高侧表, pen='b', name='高', symbol='o', symbolBrush='b')
            低 = 右图.plot(高低时间表, 低侧表, pen='r', name='低', symbol='o', symbolBrush='b')


    def 定时更新f():
        with 线程锁1:
            热浴.setData(时间表, 温度表)
            高.setData(高低时间表, 高侧表)
            低.setData(高低时间表, 低侧表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
