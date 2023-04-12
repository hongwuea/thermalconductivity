import numpy
import pyqtgraph as pg
from scipy import signal
from scipy.fft import fft
import numpy as np
from PySide6 import QtGui

font = QtGui.QFont()
font.setPixelSize(50)


def 塞贝克系数(塞_温度):  # 温度→V/K
    a3 = 2.034140227
    a2 = -1.341522423
    a1 = 0.432616895

    return 1E-06 * (1E-06 * a3 * 塞_温度 ** 3 + 1E-03 * a2 * 塞_温度 ** 2 + a1 * 塞_温度)


f = open(r'../結果/G118_2023_03_LIAノイズ検証τ_10s_12dBOct_固定100K_nVMAOUT+LIA_0.1Hz_5.0mA_2023年03月13日11時27分56秒_.txt',
         encoding='utf-8')
print(f.readline())

时间表, X表, Y表 = list(eval(f.readline()))
X表 = -1 * np.array(X表)
Y表 = 1 * np.array(Y表)
R表 = (X表 ** 2 + Y表 ** 2) ** 0.5
时间表 = np.array(时间表)

多項式あてはめ = np.polynomial.polynomial.Polynomial.fit
拟合 = 多項式あてはめ(时间表[500::], R表[500::], 3)
高频R = (R表 - 拟合(时间表)) * 1e5
print(f'噪声为{np.std(高频R[500::])}nVrms')
print(abs(fft(高频R[500::])))
print(abs(fft(R表[500::] * 1e5)) / len(R表[500::]))
# fft部分


# Cp表 = 塞贝克系数(温度表) / R表
# 時間表 = 時間表 - 時間表[0]
pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
pg.setConfigOption('background', 'w')  # 默认白背景
# 窗口2级
# 窗口 = pg.GraphicsLayoutWidget(show=True, title="鉴相热容测量结果")
# 窗口.resize(800, 500)
if 1:  # 窗口内图3级
    # 左图 = 窗口.addPlot(title="同相曲线")
    # 左图.setLabel(axis='left', text='信号/Volt')
    # 左图.setLabel(axis='bottom', text='温度/K', )
    # if 1:  # 窗口内曲线4级
    #     同相X = 左图.plot(温度表, X表, pen='b', name='同相X', symbol='o', symbolBrush='b')
    #
    # 右图 = 窗口.addPlot(title="直交曲线")
    # 右图.setLabel(axis='left', text='信号/Volt')
    # 右图.setLabel(axis='bottom', text='温度/K', )
    # if 1:  # 窗口内曲线4级
    #     正交Y = 右图.plot(温度表, Y表, pen='b', name='正交Y', symbol='o', symbolBrush='b')
    #
    # 右图2 = 窗口.addPlot(title="R曲线")
    # 右图2.setLabel(axis='left', text='信号/Volt')
    # 右图2.setLabel(axis='bottom', text='温度/K', )
    # # 窗口.nextRow()
    # if 1:  # 窗口内曲线4级
    #     R = 右图2.plot(温度表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')

    # 右图3 = 窗口.addPlot(title="Cp")
    # 右图3.setLabel(axis='left', text='Arb Uni')
    # 右图3.setLabel(axis='bottom', text='温度/K', )
    # if 1:  # 窗口内曲线4级
    #    Cp = 右图3.plot(温度表, Cp表, pen='b', name='Cp表', symbol='o', symbolBrush='b')

    # 温度图 = 窗口.addPlot(title="温度-時間")
    # 温度图.setLabel(axis='left', text='温度/K')
    # 温度图.setLabel(axis='bottom', text='時間/s', )
    # if 1:  # 窗口内曲线4级
    #     温度曲线 = 温度图.plot(時間表, 温度表, pen='b', name='温度', symbol='o', symbolBrush='b')
    # 窗口.nextRow()
    # styles = {'font-size':'30px'}
    窗口2 = pg.GraphicsLayoutWidget(show=True, title="鉴相热容测量结果2")
    时间图2 = 窗口2.addPlot(title="R時間曲线")
    时间图2.setLabel(axis='left', text='信号/nV')
    时间图2.setLabel(axis='bottom', text='時間/hour', )
    if 1:  # 窗口内曲线4级
        R2 = 时间图2.plot(np.array(时间表[500::]) / 3600, R表[500::] * 1e5, pen='b', name='R表', symbol='o', symbolBrush='b')
    #
    时间图3 = 窗口2.addPlot(title="R频率曲线")
    时间图3.setLogMode(x=True, y=True)
    时间图3.setLabel(axis='left', text='信号/nV')
    时间图3.setLabel(axis='bottom', text='频率/Hz')
    if 1:  # 窗口内曲线4级1
        输入 = R表[500:] * 1e5
        # 输入 =高频R[500:]
        长 = len(输入)
        # 高频R = 高频R[500::]
        频率表 = (0.1 * (np.array(range(长 - 1)) + 1) / 长)[:int(长 / 2)]
        R3 = 时间图3.plot(频率表, (abs(fft(输入))[1::] / len(R表[500::]))[:int(长 / 2)] / np.sqrt(频率表),
                       pen=None, name='R表',
                       symbol='o', symbolBrush='b')
        R3.setSymbolSize(2)
        print(fft(输入)[0] / len(输入))
        print(np.sqrt(sum(list(map(lambda x: x ** 2, 输入[1::]))))/ len(输入))

pg.mkQApp().exec_()
