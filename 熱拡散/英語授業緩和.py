import os
import time
from threading import Thread, Lock
from scipy.optimize import curve_fit
import pyqtgraph as pg
import numpy as np

from 源.駆動 import SR850

# 频率0 = 1000
# 频率1 = 1
# 点数 = 50
SR850_1 = SR850(GPIB号=8)
初始时间 = time.time()
if not os.path.exists(r'结果'):
    os.makedirs(r'结果')
過程ファイル = open(f'结果/緩和水面0.4-1{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}.txt', mode='a', encoding='utf-8')
過程ファイル.write('緩和ファイル.write({time.time() - 初始时间},{X},{Y},)\n')

while 1:
    # 频率 = 频率0 ** (i / 点数) * 频率1 ** (1 - i / 点数)
    # SR850_1.设频率(频率)
    # X表, Y表 = [], []
    # time.sleep(3)
    for _ in range(20):
        X = SR850_1.读取('X')
        # X表.append(X)
        time.sleep(0.2)
        Y = SR850_1.读取('Y')
        # Y表.append(Y)
        time.sleep(0.2)
        過程ファイル.write(f'{time.time() - 初始时间},{X},{Y},\n')
        print(f'{time.time() - 初始时间},{X},{Y}')
    過程ファイル.flush()
# 過程ファイル.close()
