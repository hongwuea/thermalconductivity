# 熱電対接続の極性に特に注意すること

import numpy as np
import os
import pyqtgraph as pg
import sys
import time
from threading import Thread, Lock

from scipy.optimize import curve_fit

from 源.源 import 日志, 温度计转换, 塞贝克系数
from 源.駆動 import Ls350, K2182, K6220

初始电流 = 0.5E-4  # 電流制限は手動で、電流源の電圧を設定することで実現しよう
期望温差 = 0.5  # 加熱による温度差、変化しないものとする

初始点数 = 200
初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, 温差表, 结果温度, 结果热导] = [[] for _ in range(6)]
初始猜测参数 = [2, 10, 1]
线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', '热浴', '热浴逆', 2]
K2182_1 = K2182(GPIB号=17)
K6220_1 = K6220(GPIB号=13)


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 测定():
    # Ls350_1.扫引控温()
    拟合参数表 = 初始猜测参数
    设定点数, 设定电流 = 初始点数, 初始电流

    if not os.path.exists(r'日志'):
        os.makedirs(r'日志')
    sys.stdout = 日志(f'日志/高温熱伝導率{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')
    if not os.path.exists(r'结果'):
        os.makedirs(r'结果')
    平均前文件 = open(f'结果/高温熱伝導率{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
    平均前文件.write('时间秒\t晶中温度K\t设定电流\t电压差V\tκ\t时间常数\n')
    print("\n创建文件成功\n")
    time.sleep(3)
    while 1:

        K6220_1.设电流(0)

        print(f'新设定点数={设定点数}个，设定电流={设定电流:e}A\n开始取REL')
        for _ in range(128):
            小循环时间 = time.time()
            温差 = K2182_1.读电压() / 塞贝克系数(温度表[-1])
            time.sleep(0.1)
            with 线程锁1:
                温差表.append(温差)
                高低时间表.append(小循环时间 - 初始时间)
        REL = np.mean(温差表[-128::])
        REL低温修正 = K2182_1.读通道2后切回()

        print(f'REL={REL}K，开始升温。。。')
        K6220_1.设电流(设定电流)
        for _ in range(设定点数):
            小循环时间 = time.time()
            温差 = K2182_1.读电压() / 塞贝克系数(温度表[-1])
            time.sleep(0.1)
            with 线程锁1:
                温差表.append(温差)
                高低时间表.append(小循环时间 - 初始时间)
        # ΔT = np.mean(温差表[-1*设定点数::]) - REL
        低温侧相对热浴温升 = abs(K2182_1.读通道2后切回() - REL低温修正) / 塞贝克系数(温度表[-1])
        拟合温差列 = np.array(温差表[-1 * 设定点数::]) - REL
        拟合时间列 = [0.5 * 序 for 序 in range(len(拟合温差列))]
        print(拟合温差列)
        if 温度表[-1] > 50:
            try:
                拟合参数表, 协方差矩阵 = curve_fit(lambda 时间, 电压差, 时间常数, 时间偏移: 电压差 * (1 - np.exp(-(时间 - 时间偏移)
                                                                                       / 时间常数)), 拟合时间列, 拟合温差列, p0=拟合参数表)
            except:
                print(sys.exc_info())
                拟合参数表 = [np.mean(拟合温差列[100:]), 1, 0.5]

        else:
            拟合参数表 = [np.mean(拟合温差列[-100::]), 1, 0.5]

        ΔT, τ, t_0 = list(map(abs, 拟合参数表))
        κ = 10000 * (1 + 2.8 / 温度表[-1]) * 设定电流 ** 2 / ΔT

        晶中温度 = 温度表[-1] + 低温侧相对热浴温升 - ΔT / 2
        K6220_1.设电流(0)

        with 线程锁1:
            结果温度.append(晶中温度)
            结果热导.append(κ)

        设定点数 = int(max(200, min(500, 5 * τ / 0.65)))
        平均前文件.write(f'{int(time.time() - 初始时间)}\t{晶中温度}\t{设定电流}\t{ΔT}\t{κ}\t{τ}\n')
        平均前文件.flush()
        print(f"低温侧相对热浴温升 = {低温侧相对热浴温升}K")
        print(f'设定电流={设定电流},期望温差={期望温差},晶中温度={晶中温度},温度差={ΔT}')
        print(f'单次测量结束，时间={int(time.time() - 初始时间)}s\t'
              f'温度差={ΔT}K\t相对热导{κ}W/K\t时间常数={τ}s\t时间偏离={t_0}s\n结束小循环')
        print(f'等待{max(30, min(5 * τ, 600)):.4g}秒降温缓和')
        # 设定电流 = min(设定电流 * ((期望温差 / ΔT) ** 0.5), 2E-4)
        设定电流 = min(设定电流 * ((期望温差 / ΔT) ** 0.5), 0.0003)
        for _ in range(int(max(30, min(5 * τ, 600)) * 2)):
            小循环时间 = time.time()
            温差 = K2182_1.读电压() / 塞贝克系数(温度表[-1])
            time.sleep(0.2)
            with 线程锁1:
                温差表.append(温差)
                高低时间表.append(小循环时间 - 初始时间)


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
            热浴侧曲线 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')

        右图 = 窗口.addPlot(title="温升")
        右图.setLabel(axis='left', text='温度/K')
        右图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            高侧曲线 = 右图.plot(高低时间表, 温差表, pen='b', name='高', symbol='o', symbolBrush='b')

        结果图 = 窗口.addPlot(title="热导-温度")
        结果图.setLabel(axis='left', text='热导/WK^-1')
        结果图.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(结果温度, 结果热导, pen='c', name='热导', symbol='o', symbolBrush='c')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(时间表, 温度表)
            高侧曲线.setData(高低时间表, 温差表)
            结果曲线.setData(结果温度, 结果热导)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
    # ここで全データ保存機能追加？
