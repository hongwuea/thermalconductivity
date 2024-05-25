import os
import numpy as np
import pyqtgraph as pg
# import sys
import time
from threading import Thread, Lock
from scipy.optimize import curve_fit, OptimizeWarning

from 源.源v2_2 import 温度计转换, 塞贝克系数, 热浴稳定
from 源.駆動v2_1 import Ls350, K2182, K6220

# 共通設定
作图保留点数 = 3000
初始电流 = 1E-6
# 初始电流 = 5E-6
期望温差 = 1
τ_0 = 1
Ls350_1 = Ls350(GPIB号=19)
热浴 = ['B', 'X86763新', 'X86763逆新', 2, 1]  # Ls350格式，输入号，校正数据，逆校正，输出加热序号，磁场校正
RuO2低 = ['C', '热导右宽温度4', '', 0, 1]
RuO2高 = ['D', '热导左宽温度4', '', 0, 1]
K2182热电偶 = K2182(GPIB号=10)
K2182加热器 = K2182(GPIB号=17)
K6220加热器 = K6220(GPIB号=12)
温度勾配極性 = 1
# 模式 = '温度計校正'
# 模式 = '熱浴作図'
# 模式 = 'G118κsweep热电偶测量'
# 模式 = 'G118κstep热电偶测量'
模式 = 'G118κstepRuO2测量'
Ls350_1.设加热量程(通道=2, 量程=1)

# ステップ設定
初始温度 = 0.62
終了温度 = 40
# 平均回数 = 16000
平均回数 = 16
降温間隔 = -2  # 昇温では負,40Ｋ以下では絶対温度に比例して小さくなる

文件名 = f'{模式}まんがにん線2_v431_ΔT{期望温差}K{time.strftime("%H時%M分%S秒%Y年%m月%d日", time.localtime())}開始'
线程锁1 = Lock()
初始时间 = time.time()
数据表 = [热浴时间表, 热浴温度表, 样品时间表, 样品温差表, 结果温度表, 结果热导表, 拟合时间表, 拟合温差表, 切分表] = [[] for _ in range(9)]
高温时间表, 高温表, 高温拟合时间表, 高温拟合温差表, 低温时间表, 低温表 = [[] for _ in range(6)]


def 文件夹创建():
    if not os.path.exists(r'结果'):
        os.makedirs(r'结果')
    if not os.path.exists(r'过程'):
        os.makedirs(r'过程')
    if not os.path.exists(r'校正'):
        os.makedirs(r'校正')


def 热浴作图():
    while 1:
        热浴温度 = 温度计转换(Ls350_1.读电阻(), 热浴[1])
        with 线程锁1:
            热浴温度表.append(热浴温度)
            热浴时间表.append(time.time() - 初始时间)
        time.sleep(3)


def 升温拟合(时间, 延迟, τ_f):
    def mymax(n, li):
        return np.array([max(n, i) for i in li])

    return 1 - np.exp(-(mymax(0, 时间 - 延迟)) / τ_f)


def 降温拟合(时间, 延迟, τ_f):
    def mymax(n, li):
        return np.array([max(n, i) for i in li])

    return np.exp(-(mymax(0, 时间 - 延迟)) / τ_f)


def 读纳伏表(回数):
    小温度表, 小時間表 = [], []
    for _ in range(int(回数)):
        电压1, 时间 = K2182热电偶.读电压t()
        温差1 = 温度勾配極性 * 电压1 / 塞贝克系数(np.mean(热浴温度表[-5:]))
        小温度表.append(温差1)
        小時間表.append(时间 - 初始时间)
        time.sleep(0.1)
        with 线程锁1:
            样品时间表.append(时间 - 初始时间)
            样品温差表.append(温差1)
    return [小時間表, 小温度表]


def 读350(回数):
    小高温表, 小低温表, 小高温時間表, 小低温時間表 = [], [], [], []
    for _ in range(int(回数)):
        电阻低, 时间低 = Ls350_1.读电阻t(通道=RuO2低[0])
        time.sleep(0.1)
        电阻高, 时间高 = Ls350_1.读电阻t(通道=RuO2高[0])
        time.sleep(0.1)
        小低温表.append(温度计转换(电阻低, RuO2低[1]))
        小低温時間表.append(时间低 - 初始时间)
        小高温表.append(温度计转换(电阻高, RuO2高[1]))
        小高温時間表.append(时间高 - 初始时间)
        with 线程锁1:
            高温时间表.append(时间高 - 初始时间)
            高温表.append(小高温表[-1])
            低温时间表.append(时间低 - 初始时间)
            低温表.append(小低温表[-1])
    return [[小高温時間表, 小高温表], [小低温時間表, 小低温表]]


def G118κsweep热电偶测量():
    time.sleep(10)
    设定电流, τ = 初始电流, τ_0
    K6220加热器.设电流t(0)
    读纳伏表(7 * max(2, int(τ)) * 3)
    温差rel1, 时间rel1 = np.mean(样品温差表[-5:]), np.mean(样品时间表[-5:])
    while 1:
        REL低温修正 = K2182热电偶.读通道2后切回()
        加热器零电压 = K2182加热器.读电压()
        时间_设电流高 = K6220加热器.设电流t(设定电流) - 初始时间
        读纳伏表点数, 安定点数 = int(7 * max(2, τ) * 3), int(2 * max(2, τ) * 3)
        升温时间表, 升温温差表 = 读纳伏表(读纳伏表点数)
        低温侧相对热浴温升 = abs(K2182热电偶.读通道2后切回() - REL低温修正) / 塞贝克系数(热浴温度表[-1])
        加热器高电压 = K2182加热器.读电压()
        时间_设电流低 = K6220加热器.设电流t(0) - 初始时间
        降温时间表, 降温温差表 = 读纳伏表(读纳伏表点数)
        温差rel2, 时间rel2 = np.mean(样品温差表[-安定点数:]), np.mean(样品时间表[-安定点数:])
        ΔT = np.mean(升温温差表[-安定点数:]) - (温差rel1 + 温差rel2) / 2

        def 线性背景拟合(时间):
            return 温差rel1 + (np.array(时间) - 时间rel1) * (温差rel2 - 温差rel1) / (时间rel2 - 时间rel1)

        升温整理表 = [np.array(升温时间表) - 时间_设电流高, (np.array(升温温差表) - 线性背景拟合(升温时间表)) / ΔT, ]
        降温整理表 = [np.array(降温时间表) - 时间_设电流低, (np.array(降温温差表) - 线性背景拟合(降温时间表)) / ΔT, ]
        try:
            [延迟时间, τ] = curve_fit(升温拟合, *升温整理表, p0=[1, τ], bounds=([-10, 0.05], [10, 50]))[0]
            [延迟时间降, τ降] = curve_fit(降温拟合, *降温整理表, p0=[1, τ], bounds=([-10, 0.05], [10, 50]))[0]
        except OptimizeWarning:
            print('フィッチング失敗,でも熱伝導率は求まるでしょう')
            延迟时间, τ, 延迟时间降, τ降 = 0, 0.1, 0, 0.1
        except RuntimeError:
            print('フィッチング失敗！')
            延迟时间, τ, 延迟时间降, τ降 = 0, 0.1, 0, 0.1
        with 线程锁1:
            拟合时间表.extend(升温时间表)
            拟合时间表.extend(降温时间表)
            拟合温差表.extend(
                ΔT * 升温拟合(np.array(升温时间表) - 时间_设电流高, 延迟时间, τ) + 线性背景拟合(升温时间表))
            拟合温差表.extend(
                ΔT * 降温拟合(np.array(降温时间表) - 时间_设电流低, 延迟时间降, τ降) + 线性背景拟合(降温时间表))
        切分表.append(len(样品时间表))
        温差rel1, 时间rel1 = 温差rel2, 时间rel2
        κ = abs(加热器高电压 - 加热器零电压) * 设定电流 / ΔT
        晶中温度 = np.mean(热浴温度表[-5:]) + 低温侧相对热浴温升 - ΔT / 2
        print(f'κ={κ},晶中温度={晶中温度}K,延迟时间={延迟时间}s,时间常数={τ}s,{τ降}s,设定电流={设定电流}A')
        with 线程锁1:
            结果温度表.append(晶中温度)
            结果热导表.append(κ)
        结果文件.write(f'{κ}\t{晶中温度}\t{延迟时间}\t{τ}\t{设定电流}\t{低温侧相对热浴温升}\n')
        结果文件.flush()
        设定电流 = min(设定电流 * ((期望温差 / ΔT * min(1, np.mean(热浴温度表[-5:]) / 40)) ** 0.5), 3e-4)


def G118κstep热电偶测量():  # 待验证
    设定温度, 设定电流, τ = 初始温度, 初始电流, τ_0
    Ls350_1.设加热量程(量程=1)
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        K6220加热器.设电流t(0)
        热浴稳定(设定温度, 热浴, Ls350_1)
        读纳伏表(7 * max(2, τ) * 3)
        温差rel1, 时间rel1 = np.mean(样品温差表[-5:]), np.mean(样品时间表[-5:])
        for i in range(平均回数):
            REL低温修正 = K2182热电偶.读通道2后切回()
            加热器零电压 = K2182加热器.读电压()
            时间_设电流高 = K6220加热器.设电流t(设定电流) - 初始时间
            读纳伏表点数, 安定点数 = int(7 * max(2, τ) * 3), int(2 * max(2, τ) * 3)
            升温时间表, 升温温差表 = 读纳伏表(读纳伏表点数)
            低温侧相对热浴温升 = abs(K2182热电偶.读通道2后切回() - REL低温修正) / 塞贝克系数(热浴温度表[-1])
            加热器高电压 = K2182加热器.读电压()
            时间_设电流低 = K6220加热器.设电流t(0) - 初始时间
            降温时间表, 降温温差表 = 读纳伏表(读纳伏表点数)
            温差rel2, 时间rel2 = np.mean(样品温差表[-安定点数:]), np.mean(样品时间表[-安定点数:])
            ΔT = np.mean(升温温差表[-安定点数:]) - (温差rel1 + 温差rel2) / 2

            def 线性背景拟合(时间):
                return 温差rel1 + (np.array(时间) - 时间rel1) * (温差rel2 - 温差rel1) / (时间rel2 - 时间rel1)

            升温整理表 = [np.array(升温时间表) - 时间_设电流高, (np.array(升温温差表) - 线性背景拟合(升温时间表)) / ΔT, ]
            降温整理表 = [np.array(降温时间表) - 时间_设电流低, (np.array(降温温差表) - 线性背景拟合(降温时间表)) / ΔT, ]
            try:
                [延迟时间, τ] = curve_fit(升温拟合, *升温整理表, p0=[1, τ], bounds=([-10, 0.05], [10, 50]))[0]
                [延迟时间降, τ降] = curve_fit(降温拟合, *降温整理表, p0=[1, τ], bounds=([-10, 0.05], [10, 50]))[0]
            except:
                print('フィッチング失敗！')
                延迟时间, τ = 0, 10
                延迟时间降, τ降 = 0, 10
            with 线程锁1:
                拟合时间表.extend(升温时间表)
                拟合时间表.extend(降温时间表)
                拟合温差表.extend(
                    ΔT * 升温拟合(np.array(升温时间表) - 时间_设电流高, 延迟时间, τ) + 线性背景拟合(升温时间表))
                拟合温差表.extend(
                    ΔT * 降温拟合(np.array(降温时间表) - 时间_设电流低, 延迟时间降, τ降) + 线性背景拟合(降温时间表))
            切分表.append(len(样品时间表))
            温差rel1, 时间rel1 = 温差rel2, 时间rel2
            κ = abs(加热器高电压 - 加热器零电压) * 设定电流 / ΔT
            晶中温度 = np.mean(热浴温度表[-5:]) + 低温侧相对热浴温升 - ΔT / 2
            print(
                f'κ={κ},晶中温度={晶中温度}K,延迟时间={延迟时间}s,时间常数={τ}s,{τ降}s,设定电流={设定电流}A,测量次数{i + 1}次')
            with 线程锁1:
                结果温度表.append(晶中温度)
                结果热导表.append(κ)
            结果文件.write(f'{κ}\t{晶中温度}\t{延迟时间}\t{τ}\t{设定电流}\t{低温侧相对热浴温升}\n')
            结果文件.flush()
            设定电流 = min(设定电流 * ((期望温差 / ΔT * min(1, np.mean(热浴温度表[-5:]) / 40)) ** 0.5), 3e-4)
        设定温度 = 设定温度 - 降温間隔 * min(1, 设定温度 / 40)


def G118κstepRuO2测量():  # 待验证
    设定温度, 设定电流, τ = 初始温度, 初始电流, τ_0
    while (设定温度 - 終了温度) * (设定温度 - 初始温度) <= 0:
        K6220加热器.设电流t(0)
        热浴稳定(设定温度, 热浴, Ls350_1)
        读350(7 * max(2, τ) * 3)
        高温rel1, 时间rel1, 低温rel1 = np.mean(高温表[-5:]), np.mean(高温时间表[-5:]), np.mean(低温表[-5:])
        for i in range(平均回数):
            # REL低温修正 = K2182热电偶.读通道2后切回()
            加热器零电压 = K2182加热器.读电压()
            时间_设电流高 = K6220加热器.设电流t(设定电流) - 初始时间
            读350点数, 安定点数 = int(7 * max(2, τ) * 3), int(2 * max(2, τ) * 3)
            升温表 = 读350(读350点数)
            升温时间表, 升温高温表 = 升温表[0]
            升温低温表 = 升温表[1][1]
            # 低温侧相对热浴温升 = abs(K2182热电偶.读通道2后切回() - REL低温修正) / 塞贝克系数(热浴温度表[-1])
            加热器高电压 = K2182加热器.读电压()
            时间_设电流低 = K6220加热器.设电流t(0) - 初始时间
            降温表 = 读350(读350点数)
            降温时间表, 降温高温表 = 降温表[0]
            # 降温低温表 = 降温表[1][1]
            高温rel2, 时间rel2, 低温rel2 = np.mean(高温表[-安定点数:]), np.mean(高温时间表[-安定点数:]), np.mean(低温表[-安定点数:])
            ΔT高 = np.mean(升温高温表[-安定点数:]) - (高温rel1 + 高温rel2) / 2
            ΔT低 = np.mean(升温低温表[-安定点数:]) - (低温rel1 + 低温rel2) / 2

            def 线性背景拟合(时间):
                return 高温rel1 + (np.array(时间) - 时间rel1) * (高温rel2 - 高温rel1) / (时间rel2 - 时间rel1)

            升温整理表 = [np.array(升温时间表) - 时间_设电流高, (np.array(升温高温表) - 线性背景拟合(升温时间表)) / ΔT高, ]
            降温整理表 = [np.array(降温时间表) - 时间_设电流低, (np.array(降温高温表) - 线性背景拟合(降温时间表)) / ΔT高, ]
            try:
                [延迟时间, τ] = curve_fit(升温拟合, *升温整理表, p0=[1, τ], bounds=([-10, 0.05], [10, 50]))[0]
                [延迟时间降, τ降] = curve_fit(降温拟合, *降温整理表, p0=[1, τ], bounds=([-10, 0.05], [10, 50]))[0]

            except:
                print('フィッチング失敗！')
                延迟时间, τ = 0, 10
                延迟时间降, τ降 = 0, 10
            with 线程锁1:
                高温拟合时间表.extend(升温时间表)
                高温拟合时间表.extend(降温时间表)
                高温拟合温差表.extend(ΔT高 * 升温拟合(np.array(升温时间表) - 时间_设电流高, 延迟时间, τ) + 线性背景拟合(升温时间表))
                高温拟合温差表.extend(ΔT高 * 降温拟合(np.array(降温时间表) - 时间_设电流低, 延迟时间降, τ降) + 线性背景拟合(降温时间表))
            切分表.append(len(样品时间表))
            高温rel1, 时间rel1, 低温rel1 = 高温rel2, 时间rel2, 低温rel2
            ΔT = ΔT高 - ΔT低
            κ = abs((加热器高电压 - 加热器零电压) * 设定电流 / ΔT)
            晶中温度 = (np.mean(升温高温表[-安定点数:]) + np.mean(升温低温表[-安定点数:])) / 2
            print(
                f'κ={κ},晶中温度={晶中温度}K,延迟时间={延迟时间}s,时间常数={τ}s,{τ降}s,'
                f'设定电流={设定电流}A,测量次数{i + 1}次,ΔT高={ΔT高},ΔT低={ΔT低},加热器高电压={加热器高电压},加热器零电压={加热器零电压}')
            with 线程锁1:
                结果温度表.append(晶中温度)
                结果热导表.append(κ)
            结果文件.write(f'{κ}\t{晶中温度}\t{延迟时间}\t{τ}\t{设定电流}\t{ΔT高}\t{ΔT低}\t{加热器高电压}\t{加热器零电压}\n')
            结果文件.flush()
            校正文件.write(f'{np.mean(热浴温度表[-5:])}\t{高温rel1}\t{低温rel1}\n')
            校正文件.flush()
            设定电流 = min(设定电流 * ((期望温差 / abs(ΔT) * min(1, np.mean(热浴温度表[-5:]) / 40)) ** 0.5), 3e-4)
        设定温度 = 设定温度 - 降温間隔 * min(1, 设定温度 / 40)


# if __name__ == '__main__':
if 模式 == 'G118κsweep热电偶测量' or 模式 == 'G118κstep热电偶测量':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="热导测量")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-时间")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴侧曲线 = 左图.plot(热浴时间表, 热浴温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')

        右图 = 窗口.addPlot(title="温升")
        右图.setLabel(axis='left', text='温度/K')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高侧曲线 = 右图.plot(样品时间表, 样品温差表, pen='b', name='温度差', symbol='o', symbolBrush='b')
            あてはめ曲線 = 右图.plot(拟合时间表, 拟合温差表, pen='g', name='あてはめ', symbol='o', symbolBrush='g')

        结果图 = 窗口.addPlot(title="热导-温度")
        结果图.setLabel(axis='left', text='热导/WK^-1')
        结果图.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(结果温度表, 结果热导表, pen='c', name='热导', symbol='o', symbolBrush='c')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            保留点数 = 3000
            热浴侧曲线.setData(热浴时间表[-保留点数:], 热浴温度表[-保留点数:])
            高侧曲线.setData(样品时间表[-保留点数:], 样品温差表[-保留点数:])
            结果曲线.setData(结果温度表, 结果热导表)
            あてはめ曲線.setData(拟合时间表[-保留点数:], 拟合温差表[-保留点数:])


    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(10000)
    文件夹创建()
    结果文件 = open(f'结果/结果{文件名}.txt', mode='a', encoding='utf-8')
    结果文件.write('{κ}\t{晶中温度}\t{延迟时间}\t{τ}\t{设定电流}\t{ΔT高}\t{ΔT低}\t{加热器高电压}\t{加热器零电压}\n')
    Thread(target=G118κsweep热电偶测量 if 模式 == 'G118κsweep热电偶测量' else G118κstep热电偶测量, daemon=True).start()
    Thread(target=热浴作图, daemon=True).start()
    pg.mkQApp().exec_()
    print('正在保存过程文件，请稍后')
    过程文件 = open(f'过程/过程{文件名}.txt', mode='a', encoding='utf-8')
    过程文件.write('[热浴时间表, 热浴温度表, 样品时间表, 样品温差表, 结果温度表, 结果热导表, 切分表]\n')
    过程文件.write(str([热浴时间表, 热浴温度表, 样品时间表, 样品温差表, 结果温度表, 结果热导表, 切分表]) + '\n')
    过程文件.close()
    结果文件.close()
    print('終わり')
if 模式 == 'G118κstepRuO2测量':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="热导测量RuO2")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-时间")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴侧曲线 = 左图.plot(热浴时间表, 热浴温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')

        右图 = 窗口.addPlot(title="温升")
        右图.setLabel(axis='left', text='温度/K')
        右图.setLabel(axis='bottom', text='时间/s', )
        右图.addLegend()
        if 1:  # 窗口内曲线4级
            高侧曲线 = 右图.plot(高温时间表, 高温表, pen='b', name='高', symbol='o', symbolBrush='b')
            あてはめ曲線 = 右图.plot(高温拟合时间表, 高温拟合温差表, pen='g', name='あてはめ', symbol='o', symbolBrush='g')
            低侧曲线 = 右图.plot(低温时间表, 低温表, pen='r', name='低', symbol='o', symbolBrush='r')
        结果图 = 窗口.addPlot(title="热导-温度")
        结果图.setLabel(axis='left', text='热导/WK^-1')
        结果图.setLabel(axis='bottom', text='温度/K', )
        if 1:  # 窗口内曲线4级
            结果曲线 = 结果图.plot(结果温度表, 结果热导表, pen='c', name='热导', symbol='o', symbolBrush='c')
        # 窗口.nextRow()
        # 3


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(热浴时间表[-作图保留点数:], 热浴温度表[-作图保留点数:])
            结果曲线.setData(结果温度表[-作图保留点数:], 结果热导表[-作图保留点数:])
            あてはめ曲線.setData(高温拟合时间表[-作图保留点数:], 高温拟合温差表[-作图保留点数:])
            高侧曲线.setData(高温时间表[-作图保留点数:], 高温表[-作图保留点数:])
            低侧曲线.setData(低温时间表[-作图保留点数:], 低温表[-作图保留点数:])


    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(10000)
    文件夹创建()
    结果文件 = open(f'结果/结果{文件名}.txt', mode='a', encoding='utf-8')
    结果文件.write('{κ}\t{晶中温度}\t{延迟时间 - 时间_设电流高}\t{τ}\t{设定电流}\t{ΔT高}\t{ΔT低}\n')
    校正文件 = open(f'校正/校正{文件名}.txt', mode='a', encoding='utf-8')
    校正文件.write(f'温度\t高{RuO2高[1]}\t低{RuO2低[1]}\n')
    Thread(target=G118κstepRuO2测量, daemon=True).start()
    Thread(target=热浴作图, daemon=True).start()
    pg.mkQApp().exec_()
    print('正在保存过程文件，请稍后')
    过程文件 = open(f'过程/过程{文件名}.txt', mode='a', encoding='utf-8')
    过程文件.write('[热浴时间表, 热浴温度表, 高温时间表, 高温表, 低温时间表, 低温表, 结果温度表, 结果热导表, 切分表]\n')
    过程文件.write(
        str([热浴时间表, 热浴温度表, 高温时间表, 高温表, 低温时间表, 低温表, 结果温度表, 结果热导表, 切分表]) + '\n')
    过程文件.close()
    结果文件.close()
    校正文件.close()
    print('終わり')
if 模式 == '温度計校正':
    print(温度计转换(Ls350_1.读电阻t(通道=RuO2低[0])[0], RuO2低[1]),
          温度计转换(Ls350_1.读电阻t(通道=RuO2高[0])[0], RuO2高[1]))
if 模式 == '熱浴作図':
    # pg全局1级
    pg.setConfigOption('foreground', 'k')  # 默认文本、线条、轴black
    pg.setConfigOption('background', 'w')  # 默认白背景
    # 窗口2级
    窗口 = pg.GraphicsLayoutWidget(show=True, title="熱浴作図")
    窗口.resize(800, 500)
    if 1:  # 窗口内图3级
        左图 = 窗口.addPlot(title="热浴温度-时间")
        左图.setLabel(axis='left', text='温度/K')
        左图.setLabel(axis='bottom', text='时间/s', )
        if 1:  # 窗口内曲线4级
            热浴侧曲线 = 左图.plot(热浴时间表, 热浴温度表, pen='g', name='热浴', symbol='o', symbolBrush='g')


    def 定时更新f():
        with 线程锁1:
            热浴侧曲线.setData(热浴时间表, 热浴温度表)


    定时器 = pg.QtCore.QTimer()
    定时器.timeout.connect(定时更新f)
    定时器.start(10000)

    Thread(target=热浴作图, daemon=True).start()
    pg.mkQApp().exec_()
    print('正在保存过程文件，请稍后')
    过程文件 = open(f'过程/过程{文件名}.txt', mode='a', encoding='utf-8')
    过程文件.write('[热浴时间表, 热浴温度表, 高温时间表, 高温表, 低温时间表, 低温表, 结果温度表, 结果热导表, 切分表]\n')
    过程文件.write(
        str([热浴时间表, 热浴温度表, 高温时间表, 高温表, 低温时间表, 低温表, 结果温度表, 结果热导表, 切分表]) + '\n')
    过程文件.close()
    print('終わり')
