# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
import os
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

from 源.源 import 温度计转换, 热浴稳定
from 源.駆動 import Ls350
from 源.駆動 import SR850

測定名 = 'G118_2023_03_nVM+LIA昇温step'
光源電流 = 5E-3  # 電流/A
周波数 = 0.1  # 周波数/Hz
SR850_1 = SR850(GPIB号=8)
Ls350_1 = Ls350(GPIB号=19)
測定条件名 = f'{周波数}Hz_{光源電流 * 1e3}mA'
開始 = time.time()
X表, Y表, R表 = [], [], []

スレッドロック1 = Lock()  # 作図エラー防止
時間表, 温度表, R温度表 = [], [], []
热浴 = ['B', '真鍋熱浴', '真鍋熱浴逆', 2]
初始温度 = 140
終了温度 = 130
平均回数 = 100
降温間隔 = 1  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる

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

        # 右图2 = 窗口.addPlot(title="R曲線")
        # 右图2.setLabel(axis='left', text='信号/Volt')
        # 右图2.setLabel(axis='bottom', text='温度/K', )
        # if 1:  # 窗口内曲线4级
        #     R = 右图2.plot(R温度表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')


    def 定时更新f():
        with スレッドロック1:
            時間表.append(time.time()-開始)
            温度表.append(Ls350_1.读温度(通道='D'))
            温度曲线.setData(時間表, 温度表)
            # R.setData(R温度表, R表)


    print("関数リンク中...")
    タイマー = pg.QtCore.QTimer()
    タイマー.timeout.connect(定时更新f)
    タイマー.start(500)
    print("少女祈祷中...")


    pg.mkQApp().exec_()

    print('完了しました！')
