import pyqtgraph as pg
from scipy import signal
import numpy as np

多项式拟合 = np.polynomial.polynomial.Polynomial.fit


def 塞贝克系数(塞_温度):  # 温度→V/K
    a3 = 2.034140227
    a2 = -1.341522423
    a1 = 0.432616895

    return 1E-06 * (1E-06 * a3 * 塞_温度 ** 3 + 1E-03 * a2 * 塞_温度 ** 2 + a1 * 塞_温度)


f = open('../結果/G118_2023_03_温度固定95k_20点_0.1Hz_5.0mA_2023年03月09日20時24分24秒_.txt',
         encoding='utf-8')
数据表 = 时间表, 温度表, X表, Y表 = [], [], [], []
print(f.readline())
for 行 in f:
    list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
R表 = abs(-1 * np.array(X表) + 1j * 1 * np.array(Y表))

时间表 = 时间表[300:]
R表 = R表[300:]
R表 = R表 - np.mean(R表[:100])
时间表 = np.array(时间表) - np.array(时间表[0])

f = open('../結果/G118_2023_03_LIAノイズ検証τ_10s_12dBOct_固定100K_nVMAOUT+LIA2_0.1Hz_5.0mA_2023年03月14日19時36分20秒_.txt',
         encoding='utf-8')
print(f.readline())
# for 行 in f:
#     list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
# print(len(eval(f.readline())))
时间表2, X表, Y表 = eval(f.readline())
R表2 = abs(-1 * np.array(X表) + 1j * 1 * np.array(Y表)) * 1e-4

时间表2 = 时间表2[300:]
R表2 = R表2[300:]
R表2 = R表2- np.mean(R表2[:100])
时间表2 = np.array(时间表2) - np.array(时间表2[0])
# R表 = R表 - 多项式拟合(时间表, R表, 1)(时间表)

f = open('../結果/G118_2023_03_LIAノイズ検証τ_10s_12dBOct_固定100K_0.1Hz_5.0mA_2023年03月11日11時42分23秒_.txt',
         encoding='utf-8')
print(f.readline())
# for 行 in f:
#     list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
# print(len(eval(f.readline())))
时间表3, X表, Y表 = eval(f.readline())
R表3 = abs(-1 * np.array(X表) + 1j * 1 * np.array(Y表))

时间表3 = 时间表3[500:]
R表3 = R表3[500:]
R表3 = R表3 - np.mean(R表3[:100])
时间表3 = np.array(时间表3) - np.array(时间表3[0])
# R表 = R表 - 多项式拟合(时间表, R表, 1)(时间表)

f = open('../結果/G118_2023_03_LIAノイズ検証τ_10s_12dBOct_固定100K_sr560予増幅_0.1Hz_5.0mA_2023年03月12日16時15分01秒_.txt',
         encoding='utf-8')
print(f.readline())
# for 行 in f:
#     list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
# print(len(eval(f.readline())))
时间表4, X表, Y表 = eval(f.readline())
R表4 = abs(-1 * np.array(X表) + 1j * 1 * np.array(Y表)) * 1e-3

时间表4 = 时间表4[600:]
R表4 = R表4[600:]
R表4 = R表4 - np.mean(R表4[:100])
时间表4 = np.array(时间表4) - np.array(时间表4[0])
# R表 = R表 - 多项式拟合(时间表, R表, 1)(时间表)


pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
pg.setConfigOption('background', 'w')  # 默认白背景

if 1:
    窗口2 = pg.GraphicsLayoutWidget(show=True, title="鉴相热容测量结果2")
    时间图2 = 窗口2.addPlot(title="R時間曲线")
    时间图2.setLabel(axis='left', text='信号変動/Volt')
    时间图2.setLabel(axis='bottom', text='時間/Hour', )
    if 1:  # 窗口内曲线4级

        R4 = 时间图2.plot(时间表3, R表3, pen='y', name='R表', symbol='o', symbolBrush='y')
        R4_5 = 时间图2.plot(时间表4, R表4, pen='r', name='R表', symbol='o', symbolBrush='r')
        R3 = 时间图2.plot(时间表2, R表2, pen='g', name='R表', symbol='o', symbolBrush='g')
        R2 = 时间图2.plot(时间表, R表, pen='b', name='R表', symbol='o', symbolBrush='b')

pg.mkQApp().exec_()
