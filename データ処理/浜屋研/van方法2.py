import pyqtgraph as pg
from scipy.interpolate import interp1d
import numpy as np


def 函数单值化(x, y):
    rx, ry = [], []
    # print(len(x))
    for i in range(len(x)):
        if x[i] not in rx:
            rx.append(x[i])
            ry.append(y[i])
    return rx, ry


数据表 = [磁场表, 电压表] = [[] for _ in range(2)]
f = open('20220808_CFVMS_BAT-0V-2_out-of-plane_I(1-16)_V1(NONE)_V2(6-11)_V3(NONE)_300K_1mA_0deg_0Ω_1-1.txt',
         encoding='utf-8')
print(f.readline())
for 行 in f:
    list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
# 数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))
磁场表, 电压表 = 函数单值化(磁场表, 电压表)
print(磁场表, 电压表)
电压表三次样条插值 = interp1d(磁场表, 电压表, kind='cubic')
磁场插值采样 = np.linspace(-78000, 78000, num=1000, endpoint=True)
电压奇成分 = list(map(lambda x: (电压表三次样条插值(x) - 电压表三次样条插值(-x)) / 2, 磁场插值采样))
电压偶成分 = list(map(lambda x: (电压表三次样条插值(x) + 电压表三次样条插值(-x)) / 2, 磁场插值采样))
# map(磁场表,(h(x)-h(-x))/2)
# 偶成分 =

if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="断熱消磁")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="磁場ー電圧")
        左图.setLabel(axis='left', text='電圧/V')
        左图.setLabel(axis='bottom', text='磁場/Oe', )
        if 1:  # 窗口内曲线4级
            电压表 = 左图.plot(磁场表, 电压表, pen='g', name='磁場対電圧', symbol='o', symbolBrush='b')
            偶成分 = 左图.plot(磁场插值采样, 电压偶成分, pen='g', name='奇成分', symbol='o', symbolBrush='g')

    if 1:  # 窗口内图3级
        右图 = 窗口.addPlot(title="奇成分")
        右图.setLabel(axis='left', text='電圧/V')
        右图.setLabel(axis='bottom', text='磁場/Oe', )
        if 1:  # 窗口内曲线4级
            奇成分 = 右图.plot(磁场插值采样, 电压奇成分, pen='g', name='奇成分', symbol='o', symbolBrush='b')
    pg.mkQApp().exec_()
