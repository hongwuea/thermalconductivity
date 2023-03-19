import os
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

# 同一フォルダに同名モジュールが入る場合にライブラリ導入エラーあり
from 源.駆動 import SR850

測定名 = 'G118圧力_ステップ緩和検証300K_LIA'
利得 = 1
光源電流 = 0.5E-3  # 電流/A
周波数 = 0.1  # 周波数/Hz

频率1 = 0.1
频率2 = 10
点数 = 20  # 对数分布
平均次数 = 10
SR850_1 = SR850(GPIB号=8)
測定条件名 = f'{周波数}Hz_{光源電流 * 1e3}mA'
開始 = time.time()
频率表, 幅值表, 角度表 = [], [], []
スレッドロック1 = Lock()  # 作図エラー防止


# def 計測():
#     for i in range(点数):
#         频率 = 频率0 ** (i / (点数 - 1)) * 频率1 ** (1 - i / (点数 - 1))
#         SR850_1.设频率(频率)
#         X表, Y表 = [], []
#         time.sleep(10)
#         for _ in range(平均次数):
#             X表.append(SR850_1.读取('X'))
#             Y表.append(SR850_1.读取('Y'))
#             time.sleep(1)
#         X平均, Y平均 = np.mean(X表), np.mean(Y表)
#         with スレッドロック1:
#             频率表.append(频率)
#             幅值表.append(np.sqrt(X平均 ** 2 + Y平均 ** 2))
#             角度表.append(np.arctan(Y平均 / X平均) * 180 / np.pi)

def 計測():
    for i in range(点数):
        频率 = 频率2 ** (i / (点数 - 1)) * 频率1 ** (1 - i / (点数 - 1))
        SR850_1.设频率(频率)
        # X表, Y表 = [], []
        time.sleep(100)
        for _ in range(平均次数):
            X = SR850_1.读取('X')
            Y = SR850_1.读取('Y')
            time.sleep(10)
            with スレッドロック1:
                频率表.append(频率)
                幅值表.append(np.sqrt(X ** 2 + Y ** 2))
                角度表.append(np.arctan(Y / X) * 180 / np.pi)


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title=f"ステップ緩和検証_{測定名}_{測定条件名}")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        右图2 = 窗口.addPlot(title="内部pt100温度計")
        右图2.setLabel(axis='left', text='R値/Volt')
        右图2.setLabel(axis='bottom', text='周波数/Hz', )
        if 1:  # 窗口内曲线4级
            R = 右图2.plot(频率表, 幅值表, pen='b', name='R表', symbol='o', symbolBrush='b')
    if 1:  # 窗口内图3级
        右图2 = 窗口.addPlot(title="内部pt100温度計")
        右图2.setLabel(axis='left', text='φ値/°')
        右图2.setLabel(axis='bottom', text='周波数/Hz', )
        if 1:  # 窗口内曲线4级
            φ = 右图2.plot(频率表, 角度表, pen='b', name='φ表', symbol='o', symbolBrush='b')


    def 定时更新f():
        with スレッドロック1:
            R.setData(频率表, 幅值表)
            φ.setData(频率表, 角度表)


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
    結果.write('[频率表,幅值表,角度表]\n')
    結果.write(str([频率表, 幅值表, 角度表]))
    結果.flush()
    結果.close()
    print('完了しました！')
