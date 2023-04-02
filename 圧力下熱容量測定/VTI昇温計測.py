import os
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
from 源.駆動 import SR850, K6220, Ls350

測定名 = 'G118圧力_VTI昇温計測_LIA'
利得 = 1000
最大電流 = 0.5E-3  # 電流/A
励起電流 = 0.5E-3
周波数 = 10  # 周波数/Hz

# 点数 = 100  # 对数分布
# 平均次数 = 10
K6220_1 = K6220(GPIB号=13)
SR850_1 = SR850(GPIB号=8)
Ls350_1 = Ls350(GPIB号=19)
測定条件名 = f'{周波数}Hz_{最大電流 * 1e3}mA'
開始 = time.time()
X表, Y表, 熱容量表 = [], [], []
時間表, 電流表, 幅值表, 角度表, 温度表 = [], [], [], [], []
スレッドロック1 = Lock()  # 作図エラー防止


def 計測():
    while 1:
        X = SR850_1.读取('X') / 利得
        Y = SR850_1.读取('Y') / 利得
        # 電圧 = (SR850_1.读取('X') + 1j * SR850_1.读取('Y')
        P = 最大電流 ** 2 * 1e4
        ω = 2 * np.pi * 周波数
        R = np.sqrt(X ** 2 + Y ** 2)
        ΔTrms = 3 * R / 励起電流
        C_p = P / (ω * ΔTrms)

        温度 = Ls350_1.读温度(通道='D')
        X表.append(X)
        Y表.append(Y)
        with スレッドロック1:
            時間表.append(time.time() - 開始)
            温度表.append(温度)
            熱容量表.append(C_p)
        time.sleep(2)


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title=f"自然降温計測_{測定名}_{測定条件名}")
    窗口.resize(800, 500)

    if 1:  # 窗口内图3级
        左図0 = 窗口.addPlot(title="時間-温度")
        左図0.setLabel(axis='left', text='温度/K')
        左図0.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            熱浴温度曲線 = 左図0.plot(時間表, 温度表, pen='g', name='　', symbol='o', symbolBrush='b')

    if 1:  # 窗口内图3级
        図1 = 窗口.addPlot(title="温度-熱容量")
        図1.setLabel(axis='left', text='熱容量/JK^-1')
        図1.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            熱容量曲線 = 図1.plot(温度表, 熱容量表, pen='g', name='　', symbol='o', symbolBrush='b')

    # if 1:  # 窗口内图3级
    #     右图2 = 窗口.addPlot(title="内部pt100温度計")
    #     右图2.setLabel(axis='left', text='R値/Volt')
    #     右图2.setLabel(axis='bottom', text='電流^2/A^2', )
    #     if 1:  # 窗口内曲线4级
    #         R = 右图2.plot(電流表, 幅值表, pen='b', name='R表', symbol='o', symbolBrush='b')
    # if 1:  # 窗口内图3级
    #     右图2 = 窗口.addPlot(title="内部pt100温度計")
    #     右图2.setLabel(axis='left', text='φ値/°')
    #     右图2.setLabel(axis='bottom', text='電流^2/A^2', )
    #     if 1:  # 窗口内曲线4级
    #         φ = 右图2.plot(電流表, 角度表, pen='b', name='φ表', symbol='o', symbolBrush='b')

    def 定时更新f():
        with スレッドロック1:
            熱浴温度曲線.setData(時間表, 温度表)
            熱容量曲線.setData(温度表, 熱容量表)


    print("関数リンク中...")
    タイマー = pg.QtCore.QTimer()
    タイマー.timeout.connect(定时更新f)
    タイマー.start(5000)
    print("少女祈祷中...")
    計測線 = Thread(target=計測, daemon=True, name='計測線')
    # 热浴作图線 = Thread(target=热浴作图, daemon=True, name='热浴作图')
    # 曲線更新 = Thread(target=定時更新f, daemon=True, name='曲線更新')
    計測線.start()
    # 热浴作图線.start()

    pg.mkQApp().exec_()

    if not os.path.exists(f'結果'):
        os.makedirs(f'結果')
    結果 = open(f'結果/{測定名}_{測定条件名}_{time.strftime("%Y年%m月%d日%H時%M分%S秒", time.localtime())}_.txt', mode='a',
              encoding='utf-8')
    結果.write('X表\tY表\t熱容量表\t 時間表\t 温度表\n')
    # 結果.write(str([X表, Y表, 熱容量表, 時間表, 温度表]))
    [結果.write('\t'.join(map(str, 横行)) + '\n') for 横行 in zip(X表, Y表, 熱容量表, 時間表, 温度表)]
    結果.flush()
    結果.close()
    print('完了しました！')
