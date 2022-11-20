import os
import sys
import time
from threading import Thread, Lock

import numpy as np
import pyqtgraph as pg

from 源.駆動 import Ls350, K2182, K6220, K195, GPIB锁
from 源.源 import 日志, 热浴稳定, 温度计转换

初始温度 = 40
終了温度 = 1
平均回数 = 3
降温間隔 = 2  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる
初始电流 = 5 * 10 ** -5  # 开始电流
期望温差 = 0.5  # 加熱による温度差、低温では小さくなる
初始点数 = 200

初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, 高侧表, 低侧表, 结果温度, 结果热导] = [[] for _ in range(7)]
线程锁1 = Lock()
ファイル名 = 'bt錯体3t'
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', '热浴', '热浴逆', 2]  # 通道，校正曲线，逆曲线，输出通道
低 = ['D', '热导左1T']
高 = ['C', '热导右1T']
K2182_1 = K2182(GPIB号=17)
K6220_1 = K6220(GPIB号=13)
K199_1 = K195(GPIB号=26)


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1])
        with 线程锁1:
            温度表.append(热浴温度)
            时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 测定():
    设定温度, 设定点数, 设定电流 = 初始温度, 初始点数, 初始电流
    if not os.path.exists(r'日志'):
        os.makedirs(r'日志')
    sys.stdout = 日志(f'日志/低温{time.strftime("%H時%M分%S秒 %Y年%m月%d日", time.localtime())}.log')
    if not os.path.exists(r'结果'):
        os.makedirs(r'结果')
    平均前文件 = open(f'结果/平均前{ファイル名}低温{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                 encoding='utf-8')
    平均前文件.write('时间秒\t晶中温度K\t设定电流\t电压差V\tκ\t时间常数\n')
    结果文件 = open(f'结果/结果{ファイル名}低温{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                encoding='utf-8')
    结果文件.write('时间秒\t热浴温度K\tκ\t变异系数\t时间常数平均\n')
    温升文件 = open(f'结果/温升{ファイル名}低温{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a',
                encoding='utf-8')
    print("\n创建文件成功\n")

    # Ls350初始化
    Ls350_1.设加热量程(量程=5)
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        小循环初始时间 = time.time()
        κ表 = []
        print('---------------------少女祈禱中。。。--------------------\n'+f'新温度循环\n'+f'调节热浴温度为{设定温度}K\n')
        K6220_1.设电流(0)
        热浴稳定(设定温度, 热浴)

        for i in range(平均回数):
            print(f'温度{设定温度}K下的第{i + 1}次测量开始')
            print(f'新设定点数={设定点数}个，设定电流={设定电流:e}A\n开始取REL')

            def 高低温侧取值(次数):
                for _ in range(次数):
                    小循环时间 = time.time()
                    低温侧 = 温度计转换(Ls350_1.读电阻(通道=低[0]), 低[1])
                    高温侧 = 温度计转换(Ls350_1.读电阻(通道=高[0]), 高[1])
                    with 线程锁1:
                        高侧表.append(高温侧)
                        低侧表.append(低温侧)
                        高低时间表.append(小循环时间 - 小循环初始时间)

            高低温侧取值(100)
            REL = np.mean(高侧表[-100::]) - np.mean(低侧表[-100::])
            # 未进行稳定判定，考虑使用一次方拟合来判断稳定性，并且增加重复次数以提高精度
            print(f'REL={REL}K，开始升温。。。')
            K6220_1.设电流(设定电流)
            高低温侧取值(设定点数)
            晶中温度 = (np.mean(高侧表[-100:]) + np.mean(低侧表[-100:])) / 2
            ΔT = np.mean(高侧表[-100:]) - np.mean(低侧表[-100:]) - REL
            # 测量功率
            加热器正电压 = np.mean([K199_1.读电压() for _ in range(5)])
            K6220_1.设电流(-1 * 设定电流)
            time.sleep(3)
            加热器负电压 = np.mean([K199_1.读电压() for _ in range(5)])
            K6220_1.设电流(0)
            κ = 设定电流 * abs(加热器正电压 - 加热器负电压) * 0.5 / ΔT
            κ表.append(κ)

            with 线程锁1:
                结果温度.append(晶中温度)
                结果热导.append(κ)
            平均前文件.write(f'{int(time.time() - 初始时间)}\t{晶中温度}\t{设定电流}\t{ΔT}\t{κ}\n')
            平均前文件.flush()
            print(f'设定电流={设定电流},期望温差={期望温差},设定温度={设定温度},晶中温度={晶中温度},温度差={ΔT}')
            print(f'单次测量结束，时间={int(time.time() - 初始时间)}s\t'
                  f'设定温度={设定温度}\t温度差={ΔT}K\t相对热导{κ}V/W\n结束小循环')
            print(f'等待降温缓和')
            设定电流 = min(设定电流 * (abs((期望温差 / ΔT * min(1, (设定温度 ** 1.5 / 250)))) ** 0.5), 0.0002)
            高低温侧取值(设定点数)

        结果文件.write(f'{int(time.time() - 初始时间)}\t{设定温度}\t{np.mean(κ表)}\t{np.std(κ表) / np.mean(κ表)}\n')
        结果文件.flush()
        温升文件.write(str([高低时间表, 高侧表, 低侧表]))
        温升文件.flush()
        高低时间表.clear()
        高侧表.clear()
        低侧表.clear()
        设定温度 = 设定温度 - 降温間隔 * min(1, 设定温度 / 40)
        # print(高侧表, 低侧表)

    热浴稳定(1, 热浴)


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
            热浴侧曲线 = 左图.plot(时间表, 温度表, pen='g', name='热浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="温升")
        右图.setLabel(axis='left', text='温度/K')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高温侧曲线 = 右图.plot(高低时间表, 高侧表, pen='b', name='高', symbol='o', symbolBrush='b')
            低温侧曲线 = 右图.plot(高低时间表, 低侧表, pen='r', name='低', symbol='o', symbolBrush='r')

        结果图 = 窗口.addPlot(title="热导-温度")
        结果图.setLabel(axis='left', text='热导/WK-1')
        结果图.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(结果温度, 结果热导, pen='c', name='热导', symbol='o', symbolBrush='b')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(时间表, 温度表)
            高温侧曲线.setData(高低时间表, 高侧表)
            低温侧曲线.setData(高低时间表, 低侧表)
            结果曲线.setData(结果温度, 结果热导)


    print("准备链接更新函数...")
    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(3000)
    print("准备加载图像...")
    Thread(target=测定).start()
    Thread(target=热浴作图).start()
    pg.mkQApp().exec_()
