import os
import sys
import time
from threading import Thread, Lock
import traceback
import numpy as np
import pyqtgraph as pg

# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
from 源.駆動 import SR850, Ls350
from 源.源 import 日志

測定名 = 'G118_2023_03_nVM+LIA昇温'
光源電流 = 5E-3  # 電流/A
周波数 = 0.1  # 周波数/Hz
SR850_1 = SR850(GPIB号=8)
Ls350_1 = Ls350(GPIB号=19)
測定条件名 = f'{周波数}Hz_{光源電流 * 1e3}mA'
開始 = time.time()
X表, Y表, R表 = [], [], []
時間表, 温度表 = [], []
Ls350_1.扫引控温(目标温度=160, 扫引速度K每min=0.1, 加热=5)

if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title=f"位相検波光交流法熱容量測定_{測定名}_{測定条件名}")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级

        温度图 = 窗口.addPlot(title="温度-時間")
        温度图.setLabel(axis='left', text='温度/K')
        温度图.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            温度曲线 = 温度图.plot(時間表, 温度表, pen='b', name='温度', symbol='o', symbolBrush='b')

        右图2 = 窗口.addPlot(title="R曲線")
        右图2.setLabel(axis='left', text='信号/Volt')
        右图2.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            R = 右图2.plot(温度表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')


    def 定时更新f():
        時間表.append(time.time() - 開始)
        X, Y = SR850_1.读取('X')*1E-4, SR850_1.读取('Y')*1E-4
        X表.append(X)
        Y表.append(Y)
        R表.append(np.sqrt(X ** 2 + Y ** 2))
        熱浴 = Ls350_1.读温度()
        温度表.append(熱浴)
        温度曲线.setData(時間表, 温度表)
        R.setData(温度表, R表)


    print("関数リンク中...")
    タイマー = pg.QtCore.QTimer()
    タイマー.timeout.connect(定时更新f)
    タイマー.start(10000)
    print("少女祈祷中...")

    pg.mkQApp().exec_()

    if not os.path.exists(f'結果'):
        os.makedirs(f'結果')
    結果 = open(f'結果/{測定名}_{測定条件名}_{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}_.txt', mode='a',
              encoding='utf-8')
    結果.write('[時間表, X表, Y表]\n')
    結果.write(str([時間表, X表, Y表]))
    結果.flush()
    結果.close()
    print('完了しました！')
