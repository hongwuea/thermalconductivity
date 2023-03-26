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
    # 轴.set_yscale('log')
    # 轴.set_xscale('log')
    # 轴.set_ylim(0)
    # 轴.set_xlim(0, 250)


def 设置log轴(轴, x轴标记, y轴标记, 标题='deflut'):
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


热浴温度, R1, R2, R3 = 读取txt('3個ルテニウム温度計.txt')
温度, 电阻 = 读取txt('lakeshore103.txt')
温度3, 电阻3 = 读取txt('lakeshore102.txt')
电阻2, 温度2 = 读取txt('中澤0.08-3.6K.txt')
温度yu, 电阻yu1, 电阻yu2 = [[np.mean(i) for i in np.split(i, 100)] for i in 读取txt('yuruox.txt')]
电阻yu2[-6]-=39

图, [轴1, 轴2] = plt.subplots(1, 2, figsize=(10, 6))
图2, [轴21, 轴22] = plt.subplots(1, 2, figsize=(10, 6))
图3, [轴2, 轴22] = plt.subplots(1, 2, figsize=(10, 6))

# 图, [轴1, 轴2] = plt.subplots(1, 2)
# 符号大小 = 8
# 符号填充 = 'none'  # 'none'是空心
# 线宽 = 3
曲线表 = [轴1.plot(温度, 电阻, label=r'lakeshore10kΩ0805', marker='s', markersize=2),
       轴2.plot(差分横轴(温度), -np.diff(np.log(电阻)) *差分横轴(温度)**0.5/ np.diff(np.log(温度)), label=r'lakeshore10kΩ080', marker='*',
               markersize=2)]
for i in [(R1, 'R1'), (R2, 'R2'), (R3, 'R3')]:
    曲线表.append(轴1.plot(热浴温度, i[0], label='KOA10kΩ0402_' + i[1], marker='*', markersize=2))
    曲线表.append(轴2.plot(差分横轴(热浴温度), -np.diff(np.log(i[0]))*差分横轴(热浴温度)**0.5 / np.diff(np.log(热浴温度)),
                       label='KOA10kΩ0402_' + i[1], marker='*', markersize=2))
曲线表.append(轴2.plot(差分横轴(温度2), -np.diff(np.log(电阻2))*差分横轴(温度2)**0.5 / np.diff(np.log(温度2)),
                   label='nakazawa', marker='*', markersize=2))

曲线表.append(轴2.plot(差分横轴(温度yu), -np.diff(np.log(电阻yu1))*差分横轴(温度yu)**0.5 / np.diff(np.log(温度yu)),
                       label='KOA1kΩ0603yu1', marker='*', markersize=2))
曲线表.append(轴2.plot(差分横轴(温度yu), -np.diff(np.log(电阻yu2))*差分横轴(温度yu)**0.5 / np.diff(np.log(温度yu)),
                       label='KOA1kΩ0603yu2', marker='*', markersize=2))
曲线表.append(轴2.plot(差分横轴(温度3), -np.diff(np.log(电阻3))*差分横轴(温度3)**0.5 / np.diff(np.log(温度3)),
                       label='lakeshore102', marker='*', markersize=2))
# 轴3.plot(温度yu, label='nakazawa', marker='*', markersize=2)
设置轴(轴1, r'T/K', r'R/Ω', 'T/R')
设置log轴(轴2, r'T/K', r'$\sqrt{T} \frac {d \ln R}{d \ln T}$', 'dimesionless sensitivity')
# 设置轴(轴3, r'T/K', r'R/Ω', 'T/R')
# [print('\t'.join(map(str, 横行))) for 横行 in zip(温度yu, 电阻yu2)]
图.tight_layout()  # 图间距


曲线表 = [轴21.plot(温度, 电阻, label=r'lakeshore10kΩ0805', marker='s', markersize=2),
       轴22.plot(差分横轴(温度), -np.diff(np.log(电阻)) / np.diff(np.log(温度)), label=r'lakeshore10kΩ080', marker='*',
               markersize=2)]
for i in [(R1, 'R1'), (R2, 'R2'), (R3, 'R3')]:
    曲线表.append(轴21.plot(热浴温度, i[0], label='KOA10kΩ0402_' + i[1], marker='*', markersize=2))
    曲线表.append(轴22.plot(差分横轴(热浴温度), -np.diff(np.log(i[0])) / np.diff(np.log(热浴温度)),
                       label='KOA10kΩ0402_' + i[1], marker='*', markersize=2))
曲线表.append(轴22.plot(差分横轴(温度2), -np.diff(np.log(电阻2)) / np.diff(np.log(温度2)),
                   label='nakazawa', marker='*', markersize=2))

曲线表.append(轴22.plot(差分横轴(温度yu), -np.diff(np.log(电阻yu1)) / np.diff(np.log(温度yu)),
                       label='KOA1kΩ0603yu1', marker='*', markersize=2))
曲线表.append(轴22.plot(差分横轴(温度yu), -np.diff(np.log(电阻yu2))/ np.diff(np.log(温度yu)),
                       label='KOA1kΩ0603yu2', marker='*', markersize=2))
曲线表.append(轴22.plot(差分横轴(温度3), -np.diff(np.log(电阻3)) / np.diff(np.log(温度3)),
                       label='lakeshore102', marker='*', markersize=2))
# 轴3.plot(温度yu, label='nakazawa', marker='*', markersize=2)
设置轴(轴21, r'T/K', r'R/Ω', 'T/R')
设置log轴(轴22, r'T/K', r'$ \frac {d \ln R}{d \ln T}$', 'dimesionless sensitivity')


图2.tight_layout()  # 图间距
plt.show()

#
# def T到R(温度, R0, a):
#     return R0 * (1 + a / 温度)
#
#
# def R到T(电阻, R0, a):
#     return a / (电阻 / R0 - 1)
