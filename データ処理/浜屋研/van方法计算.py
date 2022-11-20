import pyqtgraph as pg
from scipy.interpolate import interp1d
import numpy as np
from scipy.optimize import root, brentq

if __name__ == '__main__':

    def 函数单值化(x, y):
        rx, ry = [], []
        # print(len(x))
        for i in range(len(x)):
            if x[i] not in rx:
                rx.append(x[i])
                ry.append(y[i])
        return rx, ry


    文件表 = ['20220808_CFVMS_BAT-0V-2_out-of-plane_I(11-16)_V1(NONE)_V2(1-6)_V3(NONE)_300K_1mA_0deg_0Ω_1-1.txt',
           '20220808_CFVMS_BAT-0V-2_out-of-plane_I(6-16)_V1(NONE)_V2(1-11)_V3(NONE)_300K_1mA_0deg_0Ω_1-1.txt',
           '20220808_CFVMS_BAT-0V-2_out-of-plane_I(1-16)_V1(NONE)_V2(6-11)_V3(NONE)_300K_1mA_0deg_0Ω_1-1.txt', ]
    窗口表 = []
    正负转换 = iter([-1, -1, 1])
    样条插值 = []
    for 文件名 in 文件表:
        数据表 = [磁场表, 电压表] = [[] for _ in range(2)]
        f = open(文件名, encoding='utf-8')
        print(f.readline())
        for 行 in f:
            list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
        电压表 = next(正负转换) * np.array(电压表)
        # 数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))
        磁场表, 电压表 = 函数单值化(磁场表, 电压表)
        # print(磁场表, 电压表)
        样条插值.append(interp1d(磁场表, 电压表, kind='cubic'))
        电阻表 = []

    # 磁场插值采样 = np.linspace(-78000, 78000, num=1000, endpoint=True)
    # 电压奇成分 = list(map(lambda x: (电压表三次样条插值(x) - 电压表三次样条插值(-x)) / 2, 磁场插值采样))
    # 电压偶成分 = list(map(lambda x: (电压表三次样条插值(x) + 电压表三次样条插值(-x)) / 2, 磁场插值采样))
    d = 1
    for 磁场 in range(0, 78000, 100):
        电阻表.append(brentq(lambda ρ: np.exp(-np.pi * d * (样条插值[0](磁场) + 样条插值[0](磁场)) / 2 / ρ) +
                                    np.exp(-np.pi * d * (样条插值[1](磁场) + 样条插值[1](磁场)) / 2 / ρ) - 1, 0.0001,
                          100))
        # print(电阻表[-1])

    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口表.append(pg.GraphicsLayoutWidget(show=True, title='计算阻值'))
    窗口 = 窗口表[-1]
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="0V_I1-16V6-11")
        左图.setLabel(axis='left', text='電圧/V')
        左图.setLabel(axis='bottom', text='磁場/Oe')
        左图.addLegend()
        if 1:  # 窗口内曲线4级
            电压曲线 = 左图.plot(range(0, 78000, 100), 电阻表, pen='g', name='磁場対電圧', symbol='o', symbolBrush='b')


    pg.mkQApp().exec_()
