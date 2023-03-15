import numpy as np

from データ処理.源 import 读取csv

抵抗, 温度 = 读取csv()
底 = 0.8 * min(抵抗)
log抵抗 = np.log10((抵抗 - 底) / 底)
Zu = 1.1 * max(log抵抗) - 0.1 * min(log抵抗)
Zl = 1.1 * min(log抵抗) - 0.1 * max(log抵抗)
Z = ((log抵抗 - Zu) - (Zl - log抵抗)) / (Zu - Zl)
X = np.arccos(Z)


def 转换函数(输入, チェビシェフ係数):
    A = np.log10((输入 - 底) / 底)
    return 10 ** sum(
        map(lambda 系数, 序数: 系数 * np.cos(np.arccos(((A - Amax) - (Amin - A)) / (Amax - Amin)) * 序数), チェビシェフ係数,
            range(len(チェビシェフ係数))))


号 = 转换[转换号]
# if len(号) == 2:
#     return 转换[转换号][1] / (输入 / 转换[转换号][0] - 1)  # 多项式拟合

Amax, Amin, 底 = 号[0:3]  # 切比雪夫拟合
チェビシェフ係数 = 号[3:]
