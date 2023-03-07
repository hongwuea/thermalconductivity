import os
import sys
import time
from threading import Thread, Lock
import traceback
import numpy as np
import pyqtgraph as pg

# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
from 源.駆動 import Ls350, K2182, K6220
from 源.源 import 日志

スレッドロック1 = Lock()
Ls350_1 = Ls350(GPIB号=19)
K2182_1 = K2182(GPIB号=17)
K6220_1 = K6220(GPIB号=13)
Ls350加熱出力番号 = 2
初始电流 = 5E-3  # 電流/A
開始 = time.time()
X表, Y表, R表 = [], [], []
时间表, 温度表 = [], []


def 测量():
    初期 = time.time()
    电流 = 初始电流
    # Ls350_1.扫引控温(目标温度=160, 扫引速度K每min=0.2, 加热=3)  # 目標温度、変化速度、ヒーターのレンジを驱动.pyに入力
    # Ls340_2.扫引控温(目标温度=200,扫引速度K每min=1, 加热=5)
    K2182_1.触发切换('OFF')
    電圧表, 位相表 = [], []
    if not os.path.exists(r'結果'):
        os.makedirs(r'結果')
    結果 = open(f'結果/{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}0.1HzI35mA.txt', mode='a', encoding='utf-8')
    結果.write('時間秒\t温度\tX表\tY表\n')
    if not os.path.exists(r'日誌'):
        os.makedirs(r'日誌')
    sys.stdout = 日志(f'日誌/光交流法測定日誌{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}0.1HzI35mA.log')
    while 1:
        時間1 = time.time()
        # if 时间1 - 開始 >= 36000:
        #     Ls340_1.扫引控温(目标温度=120, 扫引速度K每min=0, 加热=3)
        #     sys.exit()
        K6220_1.设电流(电流)
        time.sleep(0.03)
        熱浴 = Ls350_1.读温度()
        # print(time.time() - 时间1)
        for i in range(9):
            try:
                time.sleep(0.5 * (i + 1) - (time.time() - 時間1))
            except:
                traceback.print_exc()
            else:
                電圧表.append(K2182_1.触发读电压())
                位相表.append(i + 1)
        # try:
        #     time.sleep(0.5 * 10 - (time.time() - 时间1))
        # except:
        #     traceback.print_exc()
        K6220_1.设电流(0)

        for i in range(9):
            try:
                time.sleep(0.5 * (i + 11) - (time.time() - 時間1))
            except:
                traceback.print_exc()
            else:
                電圧表.append(K2182_1.触发读电压())
                位相表.append(i + 11)
        with スレッドロック1:
            X表.append(sum(np.sin(2 * np.pi * np.array(位相表) / 20) * np.array(電圧表)) / 18)
            Y表.append(-sum(np.cos(2 * np.pi * np.array(位相表) / 20) * np.array(電圧表)) / 18)
            R表.append((X表[-1] ** 2 + Y表[-1] ** 2) ** 0.5)
            时间表.append(時間1 - 初期)
            温度表.append(熱浴)
        結果.write(f'{time.time() - 初期}\t{熱浴}\t{X表[-1]}\t{Y表[-1]}\n')
        結果.flush()
        print(電圧表)
        電圧表.clear()
        位相表.clear()
        # try:
        #     time.sleep(0.5 * 20 - (time.time() - 时间1))
        # except:
        #     traceback.print_exc()


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="位相検波光交流法熱容量測定")
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

        右图2 = 窗口.addPlot(title="R曲線")
        右图2.setLabel(axis='left', text='信号/Volt')
        右图2.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            R = 右图2.plot(温度表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')

        温度图 = 窗口.addPlot(title="温度-時間")
        温度图.setLabel(axis='left', text='温度/K')
        温度图.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            温度曲线 = 温度图.plot(时间表, 温度表, pen='b', name='温度', symbol='o', symbolBrush='b')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with スレッドロック1:
            # 同相X.setData(温度表, X表)
            # 正交Y.setData(温度表, Y表)
            R.setData(温度表, R表)
            温度曲线.setData(时间表, 温度表)

    print("関数リンク中...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("少女祈祷中...")
    Thread(target=测量, daemon=True, name='测量').start()
    pg.mkQApp().exec_()
