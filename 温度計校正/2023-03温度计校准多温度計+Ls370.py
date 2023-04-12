# 20K~rt的自然降温校准。使用Ls350，热浴温度计B校准ACD，B使用10mV激励，ACD用1mV方波激励并且平均8次

import os
import sys
import time
from threading import Lock

import pyqtgraph as pg

from 源.源 import 日志, 温度计转换
from 源.駆動 import Ls350, Ls370

热浴cernox = ['B', '热浴', '热浴逆', 2]
初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, A表, B表, C表, D表] = [[] for _ in range(7)]
线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)  # 350温控器约定：C=低温计，D=高温计，A,B使用非翻转的10mV激励，CD使用翻转1mV激励
Ls370_1 = Ls370(GPIB号=12)
Ls350加热环路号 = 2
#
#
# def 热浴作图():
#     while 1:
#         热浴温度 = 温度计转换(Ls350_1.读电阻(通道='B'), '热浴1030br202206he3')
#         time.sleep(3)
#         with 线程锁1:
#             温度表.append(热浴温度)
#             時間表.append(time.time() - 初始时间)

#
# def 测定():
#     if not os.path.exists(r'日志'):
#         os.makedirs(r'日志')
#     sys.stdout = 日志(f'日志/校正日志{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')
#     # if not os.path.exists(r'结果'):
#     #     os.makedirs(r'结果')
#     # 结果文件 = open(f'结果/温度计校准结果{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
#     # 结果文件.write('时间秒\t热浴温度\tA侧\tB侧\tC侧\tD侧\n')
#     print("时间秒\t热浴温度\tA侧\tB侧\tC侧\tD侧\n")


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
            热浴 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="抵抗値")
        右图.setLabel(axis='left', text='抵抗/ohm')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            # A_ = 右图.plot(時間表, A表, pen='b', name='A', symbol='o', symbolBrush='b')
            # B_ = 右图.plot(時間表, B表, pen='r', name='B', symbol='o', symbolBrush='b')
            # C_ = 右图.plot(時間表, C表, pen='y', name='C', symbol='o', symbolBrush='b')
            # D_ = 右图.plot(時間表, D表, pen='g', name='D', symbol='o', symbolBrush='b')
            A_, B_, C_, D_ = map(lambda 表, 笔, 名: 右图.plot(时间表, 表, pen=笔, name=名, symbol='o', symbolBrush='b'),
                                 [A表, B表, C表, D表], ['b', 'r', 'y', 'g'], ['A', 'B', 'C', 'D'])

    # Ls350_1.设加热量程(量程=1)
    if not os.path.exists(r'日志'):
        os.makedirs(r'日志')
    sys.stdout = 日志(f'日志/3個CERNOX校正1mVRESERVE_Ls350{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')
    print("时间秒\t热浴温度\tA侧\tB侧\tC侧\tD侧")


    def 定时更新f():
        A = Ls370_1.读电阻()
        B, C, D = map(lambda x: Ls350_1.读电阻(通道=x), ['B', 'C', 'D'])

        # 热浴温度 = 温度计转换(B, '热浴1030br202206he3')
        热浴温度 = 温度计转换(Ls350_1.读电阻(), 热浴cernox[1])
        print(f"{time.time() - 初始时间}\t{热浴温度}\t{A}\t{B}\t{C}\t{D}")
        list(map(lambda x, y: x.append(y), [时间表, 温度表, A表, B表, C表, D表], [time.time() - 初始时间, 热浴温度, A, B, C, D]))
        热浴.setData(时间表, 温度表)
        list(map(lambda x, y: x.setData(时间表, y), [A_, B_, C_, D_], [A表, B表, C表, D表]))


    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    # print("准备加载图像...")
    # Thread(target=测定).start()
    # Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
