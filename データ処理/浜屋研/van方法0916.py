import pyqtgraph as pg
from scipy.interpolate import interp1d
import numpy as np
import os

if __name__ == '__main__':

    def 函数单值化(x, y):
        rx, ry = [], []
        # print(len(x))
        for i in range(len(x)):
            if x[i] not in rx:
                rx.append(x[i])
                ry.append(y[i])
        return rx, ry


    文件路径 = '/Zhang/0916/txt/面直'
    print(os.listdir(os.getcwd() + 文件路径))

    窗口表 = []
    正负转换 = iter([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    for 文件名 in os.listdir(os.getcwd() + 文件路径):
        数据表 = [磁场表, 电压表] = [[] for _ in range(2)]
        f = open(f'.{文件路径}/' + 文件名, encoding='utf-8')
        print(f.readline())
        for 行 in f:
            list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
        电压表 = next(正负转换) * np.array(电压表)
        # 数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))
        磁场表, 电压表 = 函数单值化(磁场表, 电压表)
        # print(磁场表, 电压表)

        电压表三次样条插值 = interp1d(磁场表, 电压表, kind='cubic')
        磁场插值采样 = np.linspace(-78000, 78000, num=1000, endpoint=True)
        电压奇成分 = list(map(lambda x: (电压表三次样条插值(x) - 电压表三次样条插值(-x)) / 2, 磁场插值采样))
        电压偶成分 = list(map(lambda x: (电压表三次样条插值(x) + 电压表三次样条插值(-x)) / 2 / abs(电压表三次样条插值(0)), 磁场插值采样))
        # pg全局1级/ 电压表三次样条插值(0)
        pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
        pg.setConfigOption('background', 'w')  # 默认白背景
        # 窗口2级
        窗口表.append(pg.GraphicsLayoutWidget(show=True, title=文件名))
        窗口 = 窗口表[-1]
        窗口.resize(600, 400)
        if 1:  # 窗口内图3级
            左图 = 窗口.addPlot(title="生データ")
            左图.setLabel(axis='left', text='電圧/V')
            左图.setLabel(axis='bottom', text='磁場/Oe')
            左图.addLegend()
            if 1:  # 窗口内曲线4级
                电压曲线 = 左图.plot(磁场表, 电压表, pen='g', name='磁場対電圧', symbol='o', symbolBrush='b')

            中图 = 窗口.addPlot(title="偶成分")
            中图.setLabel(axis='left', text='電圧/V')
            中图.setLabel(axis='bottom', text='磁場/Oe')
            中图.addLegend()
            if 1:  # 窗口内曲线4级
                偶成分曲线 = 中图.plot(磁场插值采样, 电压偶成分, pen='g', name='偶成分', symbol='o', symbolBrush='g')

        if 1:  # 窗口内图3级
            右图 = 窗口.addPlot(title="奇成分")
            右图.setLabel(axis='left', text='電圧/V')
            右图.setLabel(axis='bottom', text='磁場/Oe', )
            右图.addLegend()
            if 1:  # 窗口内曲线4级
                奇成分曲线 = 右图.plot(磁场插值采样, 电压奇成分, pen='g', name='奇成分', symbol='o', symbolBrush='b')

    pg.mkQApp().exec_()
