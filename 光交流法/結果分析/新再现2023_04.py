import pyqtgraph as pg
from scipy import signal
import numpy as np


# def 塞贝克系数(塞_温度):  # 温度→V/K　ゼーベック係数
#    return 1E-06 * (1E-06 * 塞_温度 ** 3 - 0.0011 * 塞_温度 ** 2 + 0.398 * 塞_温度 + 1.2598)

def 塞贝克系数(塞_温度):  # 温度→V/K
    a3 = 2.034140227
    a2 = -1.341522423
    a1 = 0.432616895

    return 1E-06 * (1E-06 * a3 * 塞_温度 ** 3 + 1E-03 * a2 * 塞_温度 ** 2 + a1 * 塞_温度)


# 数据表 = [时间表, 温度表, X表, Y表] = [[] for _ in range(4)]
f = open('../結果/G118_2023_03_LIAノイズ検証τ_10s_12dBOct_固定100K_nVMAOUT+LIA_0.1Hz_5.0mA_2023年03月13日11時27分56秒_.txt',
         encoding='utf-8')
print(f.readline())
# for 行 in f:
#     list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
# print(len(eval(f.readline())))
时间表, X表, Y表 = eval(f.readline())
X表 = -1 * np.array(X表)
Y表 = 1 * np.array(Y表)
R表 = (X表 ** 2 + Y表 ** 2) ** 0.5 *1e-4
# Cp表 = 塞贝克系数(温度表) / R表
时间表 = np.array(时间表) - np.array(时间表[0])
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
    # 温度图 = 窗口.addPlot(title="温度-時間")    #
    #
    # 温度图.setLabel(axis='left', text='温度/K')
    # 温度图.setLabel(axis='bottom', text='時間/s', )
    # if 1:  # 窗口内曲线4级
    #     温度曲线 = 温度图.plot(时间表, 温度表, pen='b', name='温度', symbol='o', symbolBrush='b')
    # 窗口.nextRow()
    窗口2 = pg.GraphicsLayoutWidget(show=True, title="鉴相热容测量结果2")
    时间图2 = 窗口2.addPlot(title="R時間曲线")
    时间图2.setLabel(axis='left', text='信号/Volt')
    时间图2.setLabel(axis='bottom', text='時間/Hour', )
    if 1:  # 窗口内曲线4级
        R2 = 时间图2.plot(10 / 3600 * np.array(range(len(R表))), R表, pen='b', name='R表', symbol='o', symbolBrush='b')

# def 定时更新f():
#     同相X.setData(温度表, X表)
#     正交Y.setData(温度表, Y表)
#     温度曲线.setData(时间表, 温度表)
#
#
# print("准备链接更新函数...")
# 定时器 = pg.QtCore.QTimer()
# 定时器.timeout.connect(定时更新f)
# 定时器.start(3000)
# print("准备加载图像...")
pg.mkQApp().exec_()
