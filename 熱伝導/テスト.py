from 源.源 import 塞贝克系数
import pyqtgraph as pg
import PyQt5
# 窗口 = pg.GraphicsLayoutWidget(show=True, title="热导测量")
# 结果图 = 窗口.addPlot(title="热导-温度")
# 结果图.plot([塞贝克系数(i) for i in range(300)])
pg.plot([塞贝克系数(i)*1e6 for i in range(300)])

# pg.show()
print([塞贝克系数(i) for i in range(272)])
pg.mkQApp().exec_()