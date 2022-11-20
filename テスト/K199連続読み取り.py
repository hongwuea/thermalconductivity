import pyqtgraph as pg
from 源.駆動 import K195
import time

初始时间 = time.time()
时间表, 电压表 = [], []
K199_1 = K195(GPIB号=26)

窗口 = pg.GraphicsLayoutWidget(show=True, title="热导测量")
左图 = 窗口.addPlot(title="热浴电压-时间")
左图.setLabel(axis='left', text='电压/K')
左图.setLabel(axis='bottom', text='时间/s', )

if 1:  # 窗口内曲线4级
    热浴侧曲线 = 左图.plot(时间表, 电压表, pen='g', name='热浴', symbol='o', symbolBrush='b')


def 定时更新f():
    时间表.append(time.time() - 初始时间)
    电压表.append(K199_1.读电压())
    热浴侧曲线.setData(时间表, 电压表)


定时器 = pg.QtCore.QTimer()
定时器.timeout.connect(定时更新f)
定时器.start(10)

pg.mkQApp().exec_()
print("测试测试")
