import pyqtgraph as pg
import numpy as np

数据表 = [时间表, 温度表, 高侧表, 低侧表, 磁场表] = [[] for _ in range(5)]
f = open('断熱消磁15時46分07秒 2022年06月25日.log', encoding='utf-8')
print(f.readline())
for 行 in f:
    list(map(lambda x, y: x.append(float(y.strip('[]'))), 数据表, 行.strip().split('\t')))
数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))

if __name__ == '__main__':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="断熱消磁")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-時間")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='時間/s', )
        if 1:  # 窗口内曲线4级
            热浴 = 左图.plot(时间表, 温度表, pen='g', name='熱浴', symbol='o', symbolBrush='b')

        右图 = 窗口.addPlot(title="抵抗")
        右图.setLabel(axis='left', text='抵抗/Ω')
        右图.setLabel(axis='bottom', text='時間/s', )
        右图.showGrid(x=True, y=True)          # x有网格y没有
        # 右图.setLogMode(x=False, y=True)       # 非对数坐标
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高 = 右图.plot(时间表, 高侧表, pen='b', name='試料', symbol='o', symbolBrush='b')
            低 = 右图.plot(时间表, 低侧表, pen='g', name='参考', symbol='o', symbolBrush='g')

        磁场图 = pg.ViewBox()
        右图.showAxis('right')
        右图.scene().addItem(磁场图)
        右图.getAxis('right').linkToView(磁场图)
        磁场图.setXLink(右图)
        右图.getAxis('right').setLabel('磁場/T', color='#ff0000')
        磁场曲线 = pg.PlotDataItem()
        # 磁场曲线.addLegend()
        磁场曲线.setData(时间表, np.array(磁场表)*37, pen='r', name='磁场', symbol='o', symbolBrush='r')
        磁场图.addItem(磁场曲线)


        def 更新视图():
            ## view has resized; update auxiliary views to match
            # global 右图, 磁场图
            磁场图.setGeometry(右图.vb.sceneBoundingRect())
            磁场图.linkedViewChanged(右图.vb, 磁场图.XAxis)


        更新视图()
        右图.vb.sigResized.connect(更新视图)
        # 磁场图 = 窗口.addPlot(title="磁场-温度")
        # 磁场图.setLabel(axis='left', text='电压/V')
        # 磁场图.setLabel(axis='bottom', text='时间/s', )
        # if 1:  # 窗口内曲线4级
        #     磁场曲线 = 磁场图.plot(時間表, 磁场表, pen='c', name='磁场', symbol='o', symbolBrush='b')
        # 窗口.nextRow()
        # 3

    print("准备链接更新函数...")

    print("准备加载图像...")

    pg.mkQApp().exec_()
