import matplotlib.pyplot as plt
import numpy as np

# from scipy.optimize import curve_fit
from データ処理.源 import 设置字大小

设置字大小(20)


def 设置轴(轴, x轴标记, y轴标记, 标题='deflut'):
    轴.minorticks_on()
    轴.tick_params(direction='in', right=True, top=True)
    轴.tick_params(which='minor', length=2, direction='in', right=True, top=True)
    轴.tick_params(direction='in')
    轴.tick_params(which='minor', length=2, direction='in')
    轴.legend(loc="best", handlelength=0.1, labelspacing=0.3)
    轴.set_xlabel(x轴标记)
    轴.set_ylabel(y轴标记)
    轴.set_title(标题, fontsize=16)
    轴.set_yscale('log')
    轴.set_xscale('log')
    # 轴.set_ylim(0)
    # 轴.set_xlim(0, 250)


def 读取txt(文件名):
    f = open(文件名, encoding='utf-8')
    数据表 = [[] for _ in range(len(f.readline().strip().split('\t')))]
    f.seek(0, 0)
    print(f.readline())
    for 行 in f:
        list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
    数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))
    f.close()
    return 数据表


def 差分横轴(表):
    return (np.array(list(表)[1::]) + np.array(list(表)[:-1:])) / 2


def 计算a(温度表, 电阻表):
    温度1 = 差分横轴(温度表)
    电阻1 = 差分横轴(电阻表)
    drdt = np.diff(电阻表) / np.diff(温度表)
    # a = -差分横轴(温度表) / (1 + 1 / (drdt * 温度1 / 电阻1))
    a = -drdt*温度1/电阻1
    return 温度1, a


热浴温度, R1, R2, R3 = 读取txt('3個ルテニウム温度計.txt')
温度4, RuO1, RuO2, Cernox1 = 读取txt('3個ルテニウム温度計3.txt')
温度yu, 电阻yu1, 电阻yu2 = [[np.mean(i) for i in np.split(i, 100)] for i in 读取txt('yuruox.txt')]
电阻yu2[-6] -= 39

图, [轴1, 轴2] = plt.subplots(1, 2, figsize=(10, 6))

数据表1 = [((热浴温度, R1), 'KOA10kΩ0402_R1'), ((热浴温度, R2), 'KOA10kΩ0402_R2'), ((热浴温度, R3), 'KOA10kΩ0402_R3')
    , (读取txt('lakeshore103.txt'), 'lakeshore103')
    , (读取txt('lakeshore102.txt'), 'lakeshore102')
    , ((温度yu, 电阻yu1), 'KOA1kΩ0603yu1'), ((温度yu, 电阻yu2), 'KOA1kΩ0603yu2')
    , ((温度4, RuO1), 'RuO1NZ1'), ((温度4, RuO2), 'RuO2NZ1')
        ]
数据表2 = [((温度4, Cernox1), 'Cernox1'), (读取txt('cernoxX86829.txt'), '1030X86829'),(读取txt('X86763.txt'), '1030X86763')]

曲线表1 = [轴1.plot(*计算a(*i[0]), label=i[1], marker='*', markersize=2) for i in 数据表1]
曲线表2 = [轴2.plot(*计算a(*i[0]), label=i[1], marker='*', markersize=2) for i in 数据表2]
设置轴(轴1, r'T/K', r'dlnrdlnt', 'RuOx')
设置轴(轴2, r'T/K', r'dlnrdlnt', 'cernox')
图.tight_layout()
plt.show()
