import os
import sys
import time
from threading import Thread, Lock
import traceback
import numpy as np
import pyqtgraph as pg

# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
from 源.駆動 import SR850, Ls350, K6220
from threading import Thread, Lock, Event
from 源.源 import 日志

測定名 = 'G118圧力_ステップ緩和検証300K_LIA'
利得 = 1
光源電流 = 0.5E-3  # 電流/A
周波数 = 5  # 周波数/Hz
Ls350_1 = Ls350(GPIB号=19)
# SR850_1 = SR850(GPIB号=8)
K6220_1 = K6220(GPIB号=13)
測定条件名 = f'{周波数}Hz_{光源電流 * 1e3}mA'
開始 = time.time()
# X表, Y表, R表 = [], [], []
時間表, 温度表 = [], []
スレッドロック1 = Lock()  # 作図エラー防止


def 热浴作图():
    while 1:
        热浴温度 = Ls350_1.读温度(通道='D')
        with スレッドロック1:
            温度表.append(热浴温度)
            時間表.append(time.time() - 開始)
        time.sleep(0.1)


def 电流源开关():
    for i in range(10):
        j = i+1
        K6220_1.设电流(0)
        time.sleep(j ** 2)
        K6220_1.设电流(5e-4)
        time.sleep(j ** 2)
    print('完成')


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title=f"ステップ緩和検証_{測定名}_{測定条件名}")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级

        右图2 = 窗口.addPlot(title="内部pt100温度計")
        右图2.setLabel(axis='left', text='温度/K')
        右图2.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            R = 右图2.plot(時間表, 温度表, pen='b', name='R表', symbol='o', symbolBrush='b')


    def 定时更新f():
        R.setData(時間表, 温度表)


    print("関数リンク中...")
    タイマー = pg.QtCore.QTimer()
    タイマー.timeout.connect(定时更新f)
    タイマー.start(5000)
    print("少女祈祷中...")
    計測線 = Thread(target=电流源开关, daemon=True, name='計測線')
    热浴作图線 = Thread(target=热浴作图, daemon=True, name='热浴作图')
    # 曲線更新 = Thread(target=定時更新f, daemon=True, name='曲線更新')
    計測線.start()
    热浴作图線.start()

    pg.mkQApp().exec_()

    if not os.path.exists(f'結果'):
        os.makedirs(f'結果')
    結果 = open(f'結果/{測定名}_{測定条件名}_{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}_.txt', mode='a',
              encoding='utf-8')
    結果.write('[時間表, 温度表]\n')
    結果.write(str([時間表, 温度表]))
    結果.flush()
    結果.close()
    print('完了しました！')
