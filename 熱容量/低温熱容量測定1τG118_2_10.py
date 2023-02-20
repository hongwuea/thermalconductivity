import os
import time
from threading import Thread, Lock, Event
from scipy.optimize import curve_fit
import pyqtgraph as pg
import numpy as np

from 源.駆動 import K195, K6220, Ls350
from 源.源 import 温度计转换, 塞贝克系数, 热浴稳定

# ----------全局変数初期値----------
初期τ = 10
初期電流 = 3e-6

初始温度 = 6
終了温度 = 40
平均回数 = 10
降温間隔 = -2  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる

# ----------設定値----------
期待温昇 = 1
昇温安定判断 = 5e-5
# ------------------------
Ls350_1 = Ls350(GPIB号=19)
K6220_1 = K6220(GPIB号=13)
K195_1 = K195(GPIB号=26)

热浴 = ['B', '热浴', '热浴逆', 2]
温度計 = ['D', '热导左0T']
初期時間 = time.time()
スレッドロック1 = Lock()  # 作図エラー防止
線標識 = Event()  # 緩和中の熱浴計測一時停止
線標識.set()
時間表, 温度差表, 当てはめ時間表, 当てはめ曲線 = [], [], [], []
結果温度表, 熱容量表 = [], []
熱浴温度表, 熱浴時間表 = [], []
時間ずれ表 = []


def 热浴作图():
    while 1:
        線標識.wait()
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with スレッドロック1:
            熱浴温度表.append(热浴温度)
            熱浴時間表.append(time.time() - 初期時間)
        time.sleep(3)


def 計測():
    電流 = 初期電流
    τ, t0, シフト傾き = 初期τ, 0, 0

    def 温度読み取り(回数):
        小温度表, 小時間表 = [], []
        for _ in range(int(回数)):
            温度1 = 温度计转换(Ls350_1.读电阻(通道=温度計[0]), 温度計[1])
            時間1 = time.time() - 初期時間
            小温度表.append(温度1)
            小時間表.append(時間1)
            time.sleep(0.1)
            with スレッドロック1:
                時間表.append(時間1)
                温度差表.append(温度1)
        return [小時間表, 小温度表]

    def 加熱過程():
        T_01 = np.mean(温度差表[-10:])
        多項式あてはめ = np.polynomial.polynomial.Polynomial.fit
        while 1:
            傾き = 多項式あてはめ(*温度読み取り(30), 1).convert().coef[1]
            if abs(傾き) < 昇温安定判断:
                print(f'傾き={傾き}<{昇温安定判断}、昇温安定判断成功')
                break
            else:
                print(f'傾き={傾き}>{昇温安定判断}、昇温安定判断失败')
        ΔT1 = np.mean(温度差表[-10:]) - T_01
        κ1 = 電流 ** 2 * 1e3 / ΔT1
        print(f'ΔT, κ, T_0 = {ΔT1, κ1, T_01}')
        return ΔT1, κ1, T_01

    Ls350_1.设加热量程(量程=2)
    设定温度, 设定电流 = 初始温度, 初期電流
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        K6220_1.设电流(0)
        热浴稳定(设定温度, 热浴)

        for i in range(平均回数):
            print(f'温度{设定温度}K下的第{i + 1}次测量开始,電流値={電流}A')
            # for _ in range(10):
            #     热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
            #     with スレッドロック1:
            #         熱浴温度表.append(热浴温度)
            #         熱浴時間表.append(time.time() - 初期時間)
            #     time.sleep(0.1)
            # 温度読み取り(10)
            温度読み取り(30)
            K6220_1.设电流(電流)
            ΔT, κ, T_0 = 加熱過程()  # 安定化判断
            電流 = 電流 * (期待温昇 / ΔT * min(1, (设定温度 ** 1.5 / 250))) ** 0.5  # 電流調整

            線標識.clear()  # 緩和データ
            K6220_1.设电流(0)
            時間_0 = time.time() - 初期時間
            緩和曲線 = 温度読み取り(8 * τ * 3)
            線標識.set()
            # 緩和曲線 = [np.array(緩和曲線[0]), np.array(緩和曲線[1]) - ]  # 緩和データを原点に移動する
            try:
                当てはめてみる = curve_fit(lambda t_l, τ_l: ΔT * np.exp(-(t_l - 時間_0 - 0.1) / τ_l) + T_0, *緩和曲線, p0=[τ])  #
                # フィッティング
            except:
                pass
            else:
                [τ], 誤差行列 = 当てはめてみる

            # 時間ずれ表.append(t0)

            with スレッドロック1:  # 結果更新保存
                当てはめ時間表.extend(緩和曲線[0])
                当てはめ曲線.extend(ΔT * np.exp(-(np.array(緩和曲線[0]) - 時間_0 - 0.1) / τ) + T_0)
                結果温度表.append(np.mean(熱浴温度表[-10:]))
                熱容量表.append(τ * κ)

            print(f'τ={τ}s')
            過程ファイル.write(str([np.mean(熱浴時間表[-10:]), np.mean(熱浴温度表[-10:]), τ, ΔT, κ, T_0, 緩和曲線, ]) + '\n')
            過程ファイル.flush()

        设定温度 = 设定温度 - 降温間隔 * min(1, 设定温度 / 40)


pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
pg.setConfigOption('background', 'w')  # 默认白背景
ウィンドウ = pg.GraphicsLayoutWidget(show=True, title="熱容量測定")

左図0 = ウィンドウ.addPlot(title="時間-温度")
左図0.setLabel(axis='left', text='温度/K')
左図0.setLabel(axis='bottom', text='時間/s', )
if 1:  # 窗口内曲线4级
    熱浴温度曲線 = 左図0.plot(熱浴時間表, 熱浴温度表, pen='g', name='　', symbol='o', symbolBrush='b')

左図 = ウィンドウ.addPlot(title="時間-温度")
左図.setLabel(axis='left', text='温度/K')
左図.setLabel(axis='bottom', text='時間/s', )
if 1:  # 窗口内曲线4级
    試料温度曲線 = 左図.plot(時間表, 温度差表, pen='g', name='　', symbol='o', symbolBrush='b')
    当てはめ曲線 = 左図.plot(当てはめ時間表, 当てはめ曲線)

右図 = ウィンドウ.addPlot(title="温度-熱容")
右図.setLabel(axis='left', text='熱容/JK-1')
右図.setLabel(axis='bottom', text='温度/K', )
if 1:  # 窗口内曲线4级
    熱容量結果 = 右図.plot(結果温度表, 熱容量表, pen='g', name='　', symbol='o', symbolBrush='r')


def 定時更新f():
    with スレッドロック1:
        試料温度曲線.setData(時間表, 温度差表)
        熱容量結果.setData(結果温度表, 熱容量表)
        熱浴温度曲線.setData(熱浴時間表, 熱浴温度表)


計測線 = Thread(target=計測, daemon=True)
热浴作图線 = Thread(target=热浴作图, daemon=True)
計測線.start()
热浴作图線.start()
タイマー = pg.QtCore.QTimer()
タイマー.timeout.connect(定時更新f)
タイマー.start(3000)

if not os.path.exists(r'過程'):
    os.makedirs(r'過程')
過程ファイル = open(f'過程/緩和曲線{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
過程ファイル.write('str([np.mean(熱浴時間表[-10:]), np.mean(熱浴温度表[-10:]), τ, ΔT, κ, T_0, 緩和曲線, ]) \n')

pg.mkQApp().exec_()  # メインスレッド実行

print("終了")
過程ファイル.flush()
過程ファイル.close()

if not os.path.exists(r'結果'):  # データ保存
    os.makedirs(r'結果')
曲線ファイル = open(f'結果/高温熱容量{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
曲線ファイル.write('時間表, 温度差表, 結果温度表, 熱容量表\n')
曲線ファイル.write(str([時間表, 温度差表, 結果温度表, 熱容量表]))
曲線ファイル.flush()
曲線ファイル.close()

print("終了")
# sys.exit()
