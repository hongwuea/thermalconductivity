import time
from threading import Thread, Lock
import pyqtgraph as pg
import os
import numpy as np

from 源.駆動 import Ls350, K6220, SR850, K195, GPIB锁
from 源.源 import 温度计转换

激励电压 = 1e-2
初始时间 = time.time()
数据表 = [时间表, 磁场电压表, 热浴温度表, 电容温度表] = [[] for _ in range(4)]
线程锁1 = Lock()
ファイル名 = '容量測定不依存检查'
Ls350_1 = Ls350(GPIB号=19)
热浴温度計 = ['B', '热浴', '热浴逆', 2]  # 通道，校正曲线，逆曲线，输出通道

K6220_1 = K6220(GPIB号=13)
K199_1 = K195(GPIB号=26)
SR850_1 = SR850(GPIB号=8)

if __name__ == '__main__':
    if not os.path.exists(r'容量測定'):
        os.makedirs(r'容量測定')
    结果文件 = open(f'容量測定/結果{ファイル名}{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                encoding='utf-8')
    结果文件.write('時間表\t磁场电压表\t 热浴温度表\t 电容温度表\n')
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="容量磁场不依存")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级

        右图 = 窗口.addPlot(title="磁场")
        右图.setLabel(axis='left', text='电压/V')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            磁场曲线 = 右图.plot(时间表, 磁场电压表, pen='b', name='磁场', symbol='o', symbolBrush='b')

        结果图 = 窗口.addPlot(title="结果")
        结果图.setLabel(axis='left', text='温度/K')
        结果图.setLabel(axis='bottom', text='时间/s', )
        结果图.addLegend()
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(时间表, 热浴温度表, pen='c', name='热浴', symbol='o', symbolBrush='b')
            结果曲线2 = 结果图.plot(时间表, 电容温度表, pen='c', name='电容', symbol='o', symbolBrush='r')
        # 窗口.nextRow()
        # 3

        拟合式 = np.polynomial.Polynomial([384.9671756876404, -351.17026336328047, 103.075606405421, -9.708245023480092])


    def 定时更新f():
        X = SR850_1.读取('X')
        time.sleep(0.2)
        Y = SR850_1.读取('Y')
        time.sleep(0.2)
        电容值 = -1e9 / (2 * np.pi * 1000 * 激励电压 * (1 / complex(float(X), float(Y))).imag)
        电容温度 = 拟合式(电容值)
        时间 = time.time() - 初始时间
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴温度計[0]), 热浴温度計[1])
        磁场电压 = K199_1.读电压()
        结果文件.write(f'{时间}\t{磁场电压}\t {热浴温度}\t {电容温度}\n')
        with 线程锁1:
            时间表.append(时间)
            磁场电压表.append(磁场电压)
            热浴温度表.append(热浴温度)
            电容温度表.append(电容温度)
            磁场曲线.setData(时间表, 磁场电压表)
            结果曲线.setData(时间表, 热浴温度表)
            结果曲线2.setData(时间表, 电容温度表)



    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")

    pg.mkQApp().exec_()

    结果文件.flush()
    结果文件.close()
    # 热浴稳定(1, 热浴)
    print('終わり')
