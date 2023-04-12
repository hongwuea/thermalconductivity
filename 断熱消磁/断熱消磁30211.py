import os
import sys
import time
from threading import Thread, Lock

# import numpy as np
import pyqtgraph as pg

from 源.源 import 日志
from 源.駆動 import K2182, Ls370, K195, Ls350

数据表 = [时间表, 高侧表, 低侧表, 磁场表] = [[] for _ in range(4)]

线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)
# Ls370_1 = Ls370(GPIB号=12)
# Ls370_2 = Ls370(GPIB号=11)
# K2182_1 = K2182(GPIB号=17)
K195_1 = K195(GPIB号=16)


def 测定():
    if not os.path.exists(r'日誌'):
        os.makedirs(r'日誌')
    sys.stdout = 日志(f'日誌/断熱消磁{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')
    print('时间\t热浴温度/K\t样品电阻/Ω\t参考电阻/Ω\t磁场电压')
    初始时间 = time.time()
    while 1:
        time.sleep(0.1)
        # 参考 = Ls370_2.读电阻()

        time.sleep(0.1)
        样品 = Ls350_1.读电阻()
        time.sleep(0.1)
        参考 = 样品
        磁场 = K195_1.读电压()
        表_ = [time.time() - 初始时间, 样品, 参考, 磁场]
        print('\t'.join(map(str, 表_)))
        with 线程锁1:
            list(map(lambda 表, 值: 表.append(值), 数据表, 表_))


if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="断熱消磁")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        # 左图 = 窗口.addPlot(title="热浴温度-時間")
        # 左图.setLabel(axis='left', text='温度/K')
        # 左图.setLabel(axis='bottom', text='時間/s', )
        # if 1:  # 窗口内曲线4级
        #     热浴 = 左图.plot(時間表, 温度表, pen='g', name='熱浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="抵抗")
        右图.setLabel(axis='left', text='抵抗/Ω')
        右图.setLabel(axis='bottom', text='時間/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高 = 右图.plot(时间表, 高侧表, pen='b', name='試料', symbol='o', symbolBrush='b')
            低 = 右图.plot(时间表, 低侧表, pen='r', name='参考', symbol='o', symbolBrush='g')

        磁场图 = 窗口.addPlot(title="磁場ー温度")
        磁场图.setLabel(axis='left', text='電圧/V')
        磁场图.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            磁场曲线 = 磁场图.plot(时间表, 磁场表, pen='c', name='磁場', symbol='o', symbolBrush='b')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            # 热浴.setData(時間表, 温度表)
            高.setData(时间表, 高侧表)
            低.setData(时间表, 低侧表)
            磁场曲线.setData(时间表, 磁场表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    # Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
