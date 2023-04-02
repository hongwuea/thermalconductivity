import time
from threading import Thread, Lock

import pyqtgraph as pg

from 源.源 import 温度计转换
from 源.駆動 import Ls370

初始温度 = 40
終了温度 = 2
降温間隔 = 2  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる
平均点数 = 200

初始时间 = time.time()
数据表 = [时间表, 温度表, 热浴时间表, A表, B表, C表, D表] = [[] for _ in range(7)]
线程锁1 = Lock()
Ls370_1 = Ls370(GPIB号=12)  # 350温控器约定：C=低温计，D=高温计，A,B使用非翻转的10mV激励，CD使用翻转1mV激励
热浴温度計 = ['B', '热浴', '热浴逆', 2]


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls370_1.读电阻(), 热浴温度計[1])
        time.sleep(3)
        with 线程锁1:
            温度表.append(热浴温度)
            热浴时间表.append(time.time() - 初始时间)


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
            热浴 = 左图.plot(热浴时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='b')
        #
        # 右图 = 窗口.addPlot(title="抵抗値")
        # 右图.setLabel(axis='left', text='抵抗/ohm')
        # 右图.setLabel(axis='bottom', text='时间/s', )
        # 右图.addLegend()
        # if 1:  # 窗口内曲线4级
        #     A_, B_, C_, D_ = map(lambda 表, 笔, 名: 右图.plot(时间表, 表, pen=笔, name=名, symbol='o', symbolBrush=笔),
        #                          [A表, B表, C表, D表], ['b', 'r', 'y', 'g'], ['A', 'B', 'C', 'D'])
        #


    def 定时更新f():
        with 线程锁1:
            热浴.setData(热浴时间表, 温度表)
            # list(map(lambda x, y: x.setData(时间表, y), [A_, B_, C_, D_], [A表, B表, C表, D表]))


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    Thread(target=热浴作图, daemon=True, name='热浴').start()

    pg.mkQApp().exec_()
