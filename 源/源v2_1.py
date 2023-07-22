import sys
import numpy as np
import time
from 源.温度計データ import 转换


def 塞贝克系数(塞_温度):  # 温度→V/K
    a3 = 2.034140227
    a2 = -1.341522423
    a1 = 0.432616895

    return 1E-06 * (1E-06 * a3 * 塞_温度 ** 3 + 1E-03 * a2 * 塞_温度 ** 2 + a1 * 塞_温度)


def 热浴稳定(温度, 热浴, 温控器, 稳定次数=3, 变动上限=2e-4, 误差上限=1e-4):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
    通道 = 热浴[3]
    温控器.设温度(温度计转换(温度, 热浴[2]), 通道=通道)
    温控器.设PID(P=(温度 / 10) * 10 ** (3 - 温控器.读加热量程(通道=通道) / 2),
             I=max(3, min(150, 3 * 30 ** 3 / 温度 ** 3)), 通道=通道)
    print('开始检查温度稳定性')
    稳定标志 = 0
    while 稳定标志 < 稳定次数:
        功率表, 热浴稳定温度表, 电阻表 = [], [], []
        for _ in range(64):
            电阻 = 温控器.读电阻(通道=热浴[0])
            电阻表.append(电阻)
            热浴稳定温度表.append(温度计转换(电阻, 热浴[1]))
            time.sleep(0.3)
            功率表.append(温控器.读加热(通道=2))
            time.sleep(0.3)

        变动 = np.std(电阻表) / np.mean(电阻表)
        绝对误差 = abs((np.mean(电阻表) - 温度计转换(温度, 热浴[2])) / 温度计转换(温度, 热浴[2]))
        稳定标志 = 稳定标志 + 1
        if 变动 > 变动上限:
            稳定标志 = 0
        if 绝对误差 > 误差上限 and np.mean(功率表) > 0.2:
            稳定标志 = 0

        print(f'稳定检测中({稳定标志}/3)，变动={变动}，绝对误差={绝对误差}')
        print(f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')

    加热量程 = 温控器.读加热(通道=通道)

    if 加热量程 < 1:
        温控器.设加热量程(通道=通道, 量程=max(1, 温控器.读加热量程(通道=通道) - 1))
    if 加热量程 > 50:
        温控器.设加热量程(通道=通道, 量程=min(4, 温控器.读加热量程(通道=通道) + 1))


# def 热浴稳定370(温度, 热浴, 温控器):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
#     通道 = 热浴[3]
#     温控器.设温度(温度计转换(温度, 热浴[2]), 通道=通道)
#     温控器.设PID(P=(温度 / 10) * 10 ** (3 - 温控器.读加热量程(通道=通道) / 2),
#              I=max(3, min(150, 温度*4)), 通道=通道)
#     print('开始检查温度稳定性')
#     稳定标志 = 0
#     while 稳定标志 < 稳定次数:
#         功率表, 热浴稳定温度表, 电阻表 = [], [], []
#         for _ in range(64):
#             电阻 = 温控器.读电阻(通道=热浴[0])
#             电阻表.append(电阻)
#             热浴稳定温度表.append(温度计转换(电阻, 热浴[1]))
#             time.sleep(0.3)
#             功率表.append(温控器.读加热(通道=2))
#             time.sleep(0.3)
#
#         变动 = np.std(电阻表) / np.mean(电阻表)
#         # / max(1, 20 / 温度 ** 2)
#         绝对误差 = abs((np.mean(电阻表) - 温度计转换(温度, 热浴[2])) / 温度计转换(温度, 热浴[2]))
#         稳定标志 = 稳定标志 + 1
#         if 变动 > 2E-4:
#             稳定标志 = 0
#         if 绝对误差 > 1E-4 and np.mean(功率表) > 0.2:
#             稳定标志 = 0
#
#         print(f'稳定检测中({稳定标志}/3)，变动={变动}，绝对误差={绝对误差}')
#         print(f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')
#     加热量程 = 温控器.读加热(通道=通道)
#
#     if 加热量程 < 1:
#         温控器.设加热量程(通道=通道, 量程=max(1, 温控器.读加热量程(通道=通道) - 1))
#     if 加热量程 > 50:
#         温控器.设加热量程(通道=通道, 量程=min(8, 温控器.读加热量程(通道=通道) + 1))
#
#
# def 热浴稳定he3(温度, 热浴, 温控器):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
#     通道 = 热浴[3]
#     温控器.设温度(温度计转换(温度, 热浴[2]), 通道=通道)
#     温控器.设PID(P=(温度 / 10) * 10 ** (3 - 温控器.读加热量程(通道=通道) / 2),
#              I=max(10, min(100, 16000 / 温度 ** 2)), 通道=通道)
#     # time.sleep(0.2)
#     print('开始检查温度稳定性')
#     稳定标志 = 0
#     while 稳定标志 < 稳定次数:
#         功率表, 热浴稳定温度表 = [], []
#         for _ in range(64):
#             热浴稳定温度表.append(温度计转换(温控器.读电阻(通道=热浴[0]), 热浴[1]))
#             time.sleep(0.1 * max(1, 温度 / 4))
#             功率表.append(温控器.读加热(通道=热浴[3]))
#         二次拟合 = np.polyfit(range(64), 热浴稳定温度表, 2)
#         稳定标志 = 稳定标志 + 1
#         print(f'稳定检测中({稳定标志}/3)，拟合系数表{np.array(二次拟合) * 稳定常数 / max(温度, 10)}'
#               f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')
#     加热量程 = Ls350_1.读加热(通道=通道)
#
#     if 加热量程 < 1:
#         温控器.设加热量程(通道=通道, 量程=max(1, 温控器.读加热量程(通道=通道) - 1))
#     if 加热量程 > 50:
#         温控器.设加热量程(通道=通道, 量程=min(4, 温控器.读加热量程(通道=通道) + 1))
#

def 热浴稳定Ls370(温度, 热浴, 温控器, 稳定次数=3, 变动上限=2e-4, 误差上限=1e-4):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
    温控器.设温度(温度计转换(温度, 热浴[2]))
    温控器.设PID(P=温度 * 2, I=温度 * 2, )
    print('开始检查温度稳定性')
    稳定标志 = 0
    while 稳定标志 < 稳定次数:
        功率表, 热浴稳定温度表, 电阻表 = [], [], []
        for _ in range(max(10, min(64, 温度 * 2))):
            电阻 = 温控器.读电阻()
            电阻表.append(电阻)
            热浴稳定温度表.append(温度计转换(电阻, 热浴[1]))
            time.sleep(0.3)
            功率表.append(温控器.读加热())
            time.sleep(0.3)

        变动 = np.std(电阻表) / np.mean(电阻表)
        # / max(1, 20 / 温度 ** 2)
        绝对误差 = abs((np.mean(电阻表) - 温度计转换(温度, 热浴[2])) / 温度计转换(温度, 热浴[2])) * (1 - np.exp(-温度))
        稳定标志 = 稳定标志 + 1
        if 变动 > 变动上限:
            稳定标志 = 0
        if 绝对误差 > 误差上限:
            稳定标志 = 0

        print(f'稳定检测中({稳定标志}/3)，变动={变动}，绝对误差={绝对误差}')
        print(f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')

    加热输出 = 温控器.读加热()
    加热量程 = 10 ** (温控器.读加热量程() - 8)
    print(f'加热输出={加热输出}W，加热量程={加热量程}W')
    if 加热输出 < 0.01 * 加热量程:
        温控器.设加热量程(量程=max(1, 温控器.读加热量程() - 1))
        热浴稳定Ls370(温度, 热浴, 温控器)
    if 加热输出 > 0.5 * 加热量程:
        温控器.设加热量程(量程=min(7, 温控器.读加热量程() + 1))
        热浴稳定Ls370(温度, 热浴, 温控器)


class 日志(object):
    def __init__(self, 日志文件='Default.log'):
        self.终端 = sys.stdout
        self.log = open(日志文件, 'a', encoding='UTF-8')

    def write(self, 信息):
        self.终端.write(信息)
        self.log.write(信息)
        self.log.flush()

    def flush(self):
        pass


def 温度计转换(输入, 转换号):
    号 = 转换[转换号]
    Amax, Amin, 底 = 号[0:3]  # 切比雪夫拟合
    チェビシェフ係数 = 号[3:]
    if 输入 - 底 < 0:
        print(f"温度計'{转换号}',输入 - 底<0,{输入}ohm\n")
        A = np.log10(0.0001 / 底)
    else:
        A = np.log10((输入 - 底) / 底)
    if A > Amax:
        print(f"温度計'{转换号}',A>Amax,{输入}ohm\n")
        Ra = np.arccos(0.9999)
    elif A < Amin:
        print(f"温度計'{转换号}'A<Amin,{输入}ohm\n")
        Ra = np.arccos(-0.9999)
    else:
        Ra = np.arccos(((A - Amax) - (Amin - A)) / (Amax - Amin))
    return 10 ** sum(map(lambda 系数, 序数: 系数 * np.cos(Ra * 序数), チェビシェフ係数, range(len(チェビシェフ係数))))


def 温度计转换范围输出(转换号):
    号 = 转换[转换号]
    Amax, Amin, 底 = 号[0:3]  # 切比雪夫拟合
    チェビシェフ係数 = 号[3:]
    Inmax = (10 ** Amax * 底 + 底)
    Inmin = (10 ** Amin * 底 + 底)
    Rmin = 10 ** sum(map(lambda 系数, 序数: 系数 * np.cos(np.arccos(0.99) * 序数), チェビシェフ係数, range(len(チェビシェフ係数))))
    Rmax = 10 ** sum(map(lambda 系数, 序数: 系数 * np.cos(np.arccos(-0.99) * 序数), チェビシェフ係数, range(len(チェビシェフ係数))))
    print(f'{转换号},Inmin={Inmin},Inmax={Inmax},OUTmin={Rmin},OUTmax={Rmax}')


if __name__ == '__main__':
    print(温度计转换范围输出("热导左宽温度"))
    #
    # l = [x for x in range(50)]
    # 输入 = 13090
    # for i in range(50):
    #     输入 += l[i] / sum(l) * (59217 - 13090)
    #     print(f'{输入}\t{温度计转换(输入, "10kRuOx0402_2左")}')
