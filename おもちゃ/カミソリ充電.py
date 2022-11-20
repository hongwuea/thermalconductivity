import os
import sys
import time
import pyqtgraph as pg

from 源.駆動 import K2400
from 源.源 import 日志

K2400_1 = K2400(GPIB号=25)

电压表, 时间表 = [], []

if __name__ == '__main__':
    初始时间 = time.time()
    if not os.path.exists(r'日志'):
        os.makedirs(r'日志')
    sys.stdout = 日志(f'日志/高温熱伝導率{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')

    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="充电监测")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="电流-时间")
        左图.setLabel(axis='left', text='电流/A')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴 = 左图.plot(时间表, 电压表, pen='g', name='电流', symbol='o', symbolBrush='b')


    def 定时更新f():
        时间表.append(time.time() - 初始时间)
        电流 = float(K2400_1.读数据().split(',')[1])
        print(电流)
        电压表.append(电流)
        热浴.setData(时间表, 电压表)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    pg.mkQApp().exec_()
