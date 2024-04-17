import numpy as np
import pyqtgraph as pg
import sys
import time
from threading import Thread, Lock
from scipy.optimize import curve_fit

from 源.源v2_1 import 温度计转换, 塞贝克系数, 热浴稳定Ls370
from 源.駆動v2_0 import Ls370, K2182, K6220

初始电流 = 6.26E-5
期望温差 = 0.5

初始温度 = 300
終了温度 = 40
平均回数 = 3

初始时间 = time.time()
数据表 = [热浴时间表, 温度表, 时间表, 温差表, 结果温度表, 结果热导表] = [[] for _ in range(6)]

τ_0 = 7
线程锁1 = Lock()
Ls370_1 = Ls370(GPIB号=10)
热浴 = ['B', '热浴', '热浴逆', 2]
K2182_1 = K2182(GPIB号=7)
K6220_1 = K6220(GPIB号=15)
Ls370_1.设加热量程(量程=7)
读电压 = -1  # 熱電対接続の極性
文件名 = f'v4高温熱伝導率{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}'


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls370_1.读电阻(), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            热浴时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 测定():
    def 读纳伏表(回数):
        小温度表, 小時間表 = [], []
        for _ in range(int(回数)):
            电压1, 时间 = K2182_1.读电压t()
            温差1 = 读电压 * 电压1 / 塞贝克系数(np.mean(温度表[-5:]))
            小温度表.append(温差1)
            小時間表.append(时间 - 初始时间)
            time.sleep(0.1)
            with 线程锁1:
                时间表.append(时间 - 初始时间)
                温差表.append(温差1)
        return [小時間表, 小温度表]

    time.sleep(10)
    设定温度, 设定电流 = 初始温度, 初始电流
    τ = τ_0
    K6220_1.设电流t(0)
    读纳伏表(7 * max(10, τ * 3))
    温差rel1, 时间rel1 = np.mean(温差表[-5:]), np.mean(时间表[-5:])
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        热浴稳定Ls370(设定温度, 热浴, 温控器=Ls370_1)
        for i in range(平均回数):
            REL低温修正 = K2182_1.读通道2后切回()
            时间_设电流高 = K6220_1.设电流t(设定电流) - 初始时间
            升温时间表, 升温温差表 = 读纳伏表(7 * max(10, τ * 3))
            低温侧相对热浴温升 = abs(K2182_1.读通道2后切回() - REL低温修正) / 塞贝克系数(温度表[-1])
            K6220_1.设电流t(0)
            读纳伏表(7 * max(10, τ * 3))
            温差rel2, 时间rel2 = np.mean(温差表[-5:]), np.mean(时间表[-5:])
            ΔT = np.mean(升温温差表[-5:]) - (温差rel1 + 温差rel2) / 2

            try:
                [延迟时间, τ], 协方差矩阵 = curve_fit(
                    lambda 时间, 延迟, τ_f: ΔT * (1 - np.exp(-(时间 - 延迟) / τ_f)) + 温差rel1 + (时间 - 时间rel1) * (温差rel2 - 温差rel1) / (
                            时间rel2 - 时间rel1), 升温时间表, 升温温差表, p0=[时间_设电流高, τ])
            except:
                print(sys.exc_info())
                print(升温时间表, 升温温差表)
                延迟时间, τ = 0, 10
            温差rel1, 时间rel1 = 温差rel2, 时间rel2

            # 计算，打印
            κ = 10000 * (1 + 2.8 / np.mean(温度表[-5:])) * 设定电流 ** 2 / ΔT
            晶中温度 = np.mean(温度表[-5:]) + 低温侧相对热浴温升 - ΔT / 2
            print(f'κ={κ},晶中温度={晶中温度}K,延迟时间={延迟时间 - 时间_设电流高}s,时间常数={τ}s,设定电流={设定电流}A')
            with 线程锁1:
                结果温度表.append(晶中温度)
                结果热导表.append(κ)
            # 保存
            结果文件.write(f'{κ}\t{晶中温度}\t{延迟时间 - 时间_设电流高}\t{τ}\t{设定电流}\n')
            结果文件.flush()

            设定电流 = min(设定电流 * ((期望温差 / ΔT) ** 0.5), 3e-4)


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
            热浴侧曲线 = 左图.plot(热浴时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')

        右图 = 窗口.addPlot(title="温升")
        右图.setLabel(axis='left', text='温度/K')
        右图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            高侧曲线 = 右图.plot(时间表, 温差表, pen='b', name='高', symbol='o', symbolBrush='b')

        结果图 = 窗口.addPlot(title="热导-温度")
        结果图.setLabel(axis='left', text='热导/WK^-1')
        结果图.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(结果温度表, 结果热导表, pen='c', name='热导', symbol='o', symbolBrush='c')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(热浴时间表[-2000:], 温度表[-2000:])
            高侧曲线.setData(时间表[-2000:], 温差表[-2000:])
            结果曲线.setData(结果温度表, 结果热导表)


    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(10000)

    结果文件 = open(f'结果/结果{文件名}.txt', mode='a', encoding='utf-8')
    结果文件.write('κ\t晶中温度\t延迟时间\t时间常数\t设定电流\n')
    Thread(target=测定, daemon=True).start()
    Thread(target=热浴作图, daemon=True).start()
    pg.mkQApp().exec_()
    print('正在保存过程文件，请稍后')
    过程文件 = open(f'结果/过程{文件名}.txt', mode='a',   encoding='utf-8')
    过程文件.write('[热浴时间表, 温度表, 时间表, 温差表]\n')
    过程文件.write(str([热浴时间表, 温度表, 时间表, 温差表, 结果温度表, 结果热导表]) + '\n')
    过程文件.close()
    结果文件.close()
    print('終わり')
