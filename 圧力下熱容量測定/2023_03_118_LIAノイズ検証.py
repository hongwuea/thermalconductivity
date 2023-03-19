import os
import sys
import time
from threading import Thread, Lock
import traceback
import numpy as np
import pyqtgraph as pg

# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
from 源.駆動 import SR850
from 源.源 import 日志

測定名 = 'G118圧力_LIAノイズ検証τ_1_12dBOct_300K_LIA'
利得 = 1
光源電流 = 0.5E-3  # 電流/A
周波数 = 5  # 周波数/Hz
SR850_1 = SR850(GPIB号=8)
測定条件名 = f'{周波数}Hz_{光源電流 * 1e3}mA'
開始 = time.time()
X表, Y表, R表 = [], [], []
時間表, 温度表 = [], []

if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title=f"圧力下交流法熱容量測定_{測定名}_{測定条件名}")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级

        右图2 = 窗口.addPlot(title="R曲線")
        右图2.setLabel(axis='left', text='信号/Volt')
        右图2.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            R = 右图2.plot(時間表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')


    def 定时更新f():
        時間表.append(time.time() - 開始)
        X, Y = SR850_1.读取('X')/利得, SR850_1.读取('Y')/利得
        X表.append(X)
        Y表.append(Y)
        R表.append(np.sqrt(X ** 2 + Y ** 2))
        R.setData(時間表, R表)


    print("関数リンク中...")
    タイマー = pg.QtCore.QTimer()
    タイマー.timeout.connect(定时更新f)
    タイマー.start(1000)
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
