import matplotlib.pyplot as plt
import math
import numpy as np
import pyqtgraph as pg
from scipy import signal


f = open('日志/热导测量日志2022年07月11日13時07分07秒.log', encoding='utf-8')
電圧=[]
while True:
  data = f.readline()
  if data == '':
    break
  mean = np.mean(eval(data))
  # mean = np.mean(data.strip('[]').split(','))

  電圧.append(mean)
  # print(mean)

数据表 = [时间表, 温度表, X表, Y表] = [[] for _ in range(4)]
g = open('结果/2022年07月11日13時07分07秒4mA.txt', encoding='utf-8')
print(g.readline())
for 行 in g:
    list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
时间表, 温度表, X表, Y表 = list(map(lambda x: np.array(x[::1]), 数据表))

plt.plot(温度表,電圧)
plt.show()