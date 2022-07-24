
import numpy as np
import os
import pyqtgraph as pg
import sys
import time
from threading import Thread, Lock

from scipy.optimize import curve_fit

from 源.源 import 日志, 温度计转换, 塞贝克系数
from 源.駆動 import Ls350, K2182, K6220

初始温度 = 300
終了温度 = 6

初始电流 = 8E-5  # 電流制限は手動で、電流源の電圧を設定することで実現しよう
期望温差 = 0.5  # 加熱による温度差、変化しないものとする

初始点数 = 200
初始时间 = time.time()
数据表 = [时间表, 温度表, 高低时间表, 温差表, 结果温度, 结果热导] = [[] for _ in range(6)]
初始猜测参数 = [2, 10, 1]
线程锁1 = Lock()
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', '热浴', '热浴逆', 2]
K2182_1 = K2182(GPIB号=17)
K6220_1 = K6220(GPIB号=13)

print(K2182_1.读电压())
print(K2182_1.读电压())
print(K2182_1.读电压())
print(K2182_1.读通道2后切回())
print(K2182_1.读电压())
