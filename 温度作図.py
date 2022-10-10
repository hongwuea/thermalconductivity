
import time
from threading import Thread, Lock

import pyqtgraph as pg

from 源.駆動old import Ls350
from 源.源 import 温度计转换

初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, 温差表, 结果温度, 结果热导] = [[] for _ in range(6)]

线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)  # 350温控器约定：C=低温计，D=高温计，A,B使用非翻转的10mV激励，CD使用翻转1mV激励
热浴 = ['C', '热浴1030br202206', '热浴逆', 2]


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)
        time.sleep(3)


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="熱浴温度観察")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-时间")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴侧曲线 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')

    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(时间表, 温度表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
