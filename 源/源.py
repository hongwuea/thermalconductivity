import sys
import numpy as np
import time
from 源.駆動 import Ls350

稳定常数 = 300  # 高值要求更高
稳定次数 = 3
Ls350_1 = Ls350(GPIB号=19)


# def 塞贝克系数(塞_温度):  # 温度→V/K
#     return 1E-06 * (1E-06 * 塞_温度 ** 3 - 0.0011 * 塞_温度 ** 2 + 0.398 * 塞_温度 + 1.2598)

def 塞贝克系数(塞_温度):  # 温度→V/K
    a3 = 2.034140227
    a2 = -1.341522423
    a1 = 0.432616895

    return 1E-06 * (1E-06 * a3 * 塞_温度 ** 3 + 1E-03 * a2 * 塞_温度 ** 2 + a1 * 塞_温度)


def 热浴稳定_0(温度, 通道):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
    Ls350_1.设温度(温度计转换(温度, '热浴逆'), 通道=通道)
    # time.sleep(0.2)
    Ls350_1.设PID(P=(温度 / 10) * 10 ** (3 - Ls350_1.读加热量程(通道=通道) / 2),
                 I=max(10, min(100, 16000 / 温度 ** 2)), 通道=通道)
    # time.sleep(0.2)
    print('开始检查温度稳定性')
    稳定标志 = 0
    while 稳定标志 < 稳定次数:
        功率表, 热浴稳定温度表 = [], []
        for _ in range(64):
            热浴稳定温度表.append(温度计转换(Ls350_1.读电阻(通道='B'), '热浴'))
            time.sleep(0.3)
            功率表.append(Ls350_1.读加热(通道=2))
            time.sleep(0.3)
        二次拟合 = np.polyfit(range(64), 热浴稳定温度表, 2)
        if abs(二次拟合[0]) < 1E-5 * 温度 / 稳定常数 and abs(二次拟合[1]) < 1E-3 * 温度 / 稳定常数:
            稳定标志 = 稳定标志 + 1
        else:
            稳定标志 = 0
        print(f'稳定检测中({稳定标志}/3)，拟合系数表{np.array(二次拟合) * 稳定常数 / max(温度, 10)}'
              f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')
    加热量程 = Ls350_1.读加热(通道=通道)
    # time.sleep(0.2)
    if 加热量程 < 1:
        Ls350_1.设加热量程(通道=通道, 量程=max(1, Ls350_1.读加热量程(通道=通道) - 1))
    if 加热量程 > 50:
        Ls350_1.设加热量程(通道=通道, 量程=min(4, Ls350_1.读加热量程(通道=通道) + 1))


# def 热浴稳定(温度, 通道):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
#     Ls350_1.设温度(温度计转换(温度, '热浴逆'), 通道=通道)
#     # time.sleep(0.2)
#     Ls350_1.设PID(P=(温度 / 10) * 10 ** (3 - Ls350_1.读加热量程(通道=通道) / 2),
#                  I=max(10, min(100, 16000 / 温度 ** 2)), 通道=通道)
#     # time.sleep(0.2)
#     print('开始检查温度稳定性')
#     稳定标志 = 0
#     while 稳定标志 < 稳定次数:
#         功率表, 热浴稳定温度表, 电阻表 = [], [], []
#         for _ in range(64):
#             电阻 = Ls350_1.读电阻(通道='B')
#             电阻表.append(电阻)
#             热浴稳定温度表.append(温度计转换(电阻, '热浴'))
#             time.sleep(0.3)
#             功率表.append(Ls350_1.读加热(通道=2))
#             time.sleep(0.3)
#
#         变动 = np.std(电阻表) / np.mean(电阻表)
#         # / max(1, 20 / 温度 ** 2)
#         绝对误差 = abs((np.mean(电阻表) - 温度计转换(温度, '热浴逆')) / 温度计转换(温度, '热浴逆'))
#         稳定标志 = 稳定标志 + 1
#         if 变动 > 1E-4:
#             稳定标志 = 0
#         if 绝对误差 > 1E-4 and np.mean(功率表) > 0.2:
#             稳定标志 = 0
#
#         print(f'稳定检测中({稳定标志}/3)，变动={变动}，绝对误差={绝对误差}')
#         print(f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')
#     加热量程 = Ls350_1.读加热(通道=通道)
#
#     if 加热量程 < 1:
#         Ls350_1.设加热量程(通道=通道, 量程=max(1, Ls350_1.读加热量程(通道=通道) - 1))
#     if 加热量程 > 50:
#         Ls350_1.设加热量程(通道=通道, 量程=min(4, Ls350_1.读加热量程(通道=通道) + 1))


def 热浴稳定(温度, 热浴):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
    通道 = 热浴[3]
    Ls350_1.设温度(温度计转换(温度, 热浴[2]), 通道=通道)
    Ls350_1.设PID(P=(温度 / 10) * 10 ** (3 - Ls350_1.读加热量程(通道=通道) / 2),
                 I=max(5, min(100, 16000 / 温度 ** 2)), 通道=通道)
    print('开始检查温度稳定性')
    稳定标志 = 0
    while 稳定标志 < 稳定次数:
        功率表, 热浴稳定温度表, 电阻表 = [], [], []
        for _ in range(64):
            电阻 = Ls350_1.读电阻(通道=热浴[0])
            电阻表.append(电阻)
            热浴稳定温度表.append(温度计转换(电阻, 热浴[1]))
            time.sleep(0.3)
            功率表.append(Ls350_1.读加热(通道=2))
            time.sleep(0.3)

        变动 = np.std(电阻表) / np.mean(电阻表)
        # / max(1, 20 / 温度 ** 2)
        绝对误差 = abs((np.mean(电阻表) - 温度计转换(温度, 热浴[2])) / 温度计转换(温度, 热浴[2]))
        稳定标志 = 稳定标志 + 1
        if 变动 > 2E-4:
            稳定标志 = 0
        if 绝对误差 > 1E-4 and np.mean(功率表) > 0.2:
            稳定标志 = 0

        print(f'稳定检测中({稳定标志}/3)，变动={变动}，绝对误差={绝对误差}')
        print(f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')
    加热量程 = Ls350_1.读加热(通道=通道)

    if 加热量程 < 1:
        Ls350_1.设加热量程(通道=通道, 量程=max(1, Ls350_1.读加热量程(通道=通道) - 1))
    if 加热量程 > 50:
        Ls350_1.设加热量程(通道=通道, 量程=min(4, Ls350_1.读加热量程(通道=通道) + 1))


def 热浴稳定he3(温度, 热浴):  # 用二次函数拟合最近2分钟内的取的128个点，一次和二次项小于某一限值即可，并输出过程中的温度表和稳定时间
    通道 = 热浴[3]
    Ls350_1.设温度(温度计转换(温度, 热浴[2]), 通道=通道)
    Ls350_1.设PID(P=(温度 / 10) * 10 ** (3 - Ls350_1.读加热量程(通道=通道) / 2),
                 I=max(10, min(100, 16000 / 温度 ** 2)), 通道=通道)
    # time.sleep(0.2)
    print('开始检查温度稳定性')
    稳定标志 = 0
    while 稳定标志 < 稳定次数:
        功率表, 热浴稳定温度表 = [], []
        for _ in range(64):
            热浴稳定温度表.append(温度计转换(Ls350_1.读电阻(通道=热浴[0]), 热浴[1]))
            time.sleep(0.1 * max(1, 温度 / 4))
            功率表.append(Ls350_1.读加热(通道=热浴[3]))
        二次拟合 = np.polyfit(range(64), 热浴稳定温度表, 2)
        稳定标志 = 稳定标志 + 1
        print(f'稳定检测中({稳定标志}/3)，拟合系数表{np.array(二次拟合) * 稳定常数 / max(温度, 10)}'
              f'，热浴温度表\n{热浴稳定温度表}\n输出功率表\n{功率表}')
    加热量程 = Ls350_1.读加热(通道=通道)

    if 加热量程 < 1:
        Ls350_1.设加热量程(通道=通道, 量程=max(1, Ls350_1.读加热量程(通道=通道) - 1))
    if 加热量程 > 50:
        Ls350_1.设加热量程(通道=通道, 量程=min(4, Ls350_1.读加热量程(通道=通道) + 1))


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
    转换 = {'热浴': [3.1370706260, -0.9419809565, 31.1355065340, 0.8985929852, -1.7105170129, 0.0624105876,
                 0.4084016962,
                 -0.0677766330, 0.0305181214, 0.0521930989, 0.0815308455, 0.0143915160, 0.0232346105, 0.0394865639,
                 0.0128335945, 0.0163157530, 0.0013120119, 0.0127207052, -0.0011770961],
          '热浴cernox银yu23': [1.4187214586,
                            -0.7857673959,
                            245.5334400000,
                            0.8996247566,
                            -0.9279709763,
                            -0.1586768141,
                            -0.0545132125,
                            -0.0724748492,
                            -0.0988961306,
                            -0.0540293374,
                            -0.0589237912,
                            -0.0317242453,
                            -0.0349917266,
                            -0.0148203630,
                            -0.0160577256,
                            -0.0052333328,
                            -0.0057012382,
                            -0.0010211369,
                            -0.0011765961,

                            ],
          '热浴1030br202206': [
              0.9310938486,
              -0.7414376131,
              87.5449560000,
              0.9579911592,
              -0.8015018331,
              -0.0817201075,
              0.0406861532,
              0.0066560142,
              -0.0086647719,
              -0.0012288231,
              -0.0014943564,
              -0.0002508411,
              -0.0014979927,
              0.0000219024,
              -0.0005051331,
              0.0000053491,
              -0.0001972710,
              0.0000420501,

          ],
          '热浴1030br202206he3': [
              0.7286794443,
              -0.7230363037,
              366.5740800000,
              0.1379742777,
              -0.3330111368,
              -0.0516231899,
              0.0003025203,
              -0.0141623651,
              -0.0235675760,
              -0.0064655204,
              -0.0325686340,
              0.0000323073,
              -0.0344339188,
              0.0018979186,
              -0.0276547667,
              0.0010867117,
              -0.0158671114,
              0.0001234303,
              -0.0052645900,
          ],
          '热浴1030br202206he3逆': [0.6809246022,
                                 -0.7186949544,
                                 0.5600000000,
                                 2.8682023380,
                                 -0.3677856953,
                                 -0.2518746654,
                                 0.0063097251,
                                 -0.1638605317,
                                 -0.0267506757,
                                 -0.0945225288,
                                 -0.0402350456,
                                 -0.0401487480,
                                 -0.0369585217,
                                 -0.0111266666,
                                 -0.0233875652,
                                 -0.0010771471,
                                 -0.0099301267,
                                 0.0003326627,
                                 -0.0022770414,
                                 ],
          '热浴逆': [3.5821890294, -0.9824462659, 0.2073244864, 2.6157587564, -1.4693632300, -0.3412338246, 0.0932799274,
                  -0.4444565589, 0.1045076577, -0.2413682977, 0.0287180041, -0.1480131406, 0.0144954979, -0.0715157995,
                  0.0022336613, -0.0246261317, -0.0016672277, -0.0051739322, -0.0003042981],
          '低温侧0T_L': [0.4894213220,
                      -0.7012855653,
                      14066.1760000000,
                      0.2569172526,
                      -0.4295243262,
                      -0.0196994897,
                      0.0103301237,
                      0.0019369482,
                      0.0002804097,
                      0.0001491251,
                      -0.0001768994,
                      -0.0001065447,
                      -0.0001943761,
                      -0.0000654201,
                      -0.0000917213,
                      -0.0000059295,
                      -0.0000303136,
                      0.0000024821,
                      ],
          '高温侧0T_L': [0.4820961632,
                      -0.7006196417,
                      13563.3680000000,
                      0.2583323550,
                      -0.4303924690,
                      -0.0244093082,
                      0.0077471671,
                      0.0012536119,
                      0.0000893589,
                      0.0002210831,
                      -0.0001265641,
                      -0.0000821759,
                      -0.0001337384,
                      -0.0000665141,
                      -0.0000412941,
                      -0.0000094252,
                      0.0000013051,
                      0.0000046301,
                      ],
          '低温侧0.3T': [0.7425406734,
                      -0.7242964154,
                      9469.7280000000,
                      0.6116234443,
                      -0.9334114395,
                      0.0943272833,
                      -0.0209048835,

                      ],
          '高温侧0.3T': [0.7399401488,
                      -0.7240600041,
                      9082.9143999999,
                      0.6150239901,
                      -0.9329423915,
                      0.0896153896,
                      -0.0221985402,

                      ],
          '低温侧0.3T_H': [0.3103518559,
                        -0.6850065229,
                        9397.6324000000,
                        0.8451124072,
                        -0.7189727756,
                        0.0715147505,
                        -0.0203174019,
                        0.0053314805,
                        -0.0020724377,
                        -0.0009501447,
                        -0.0000538765,
                        -0.0009183393,
                        0.0000820371,
                        -0.0003469539,
                        -0.0000311380,
                        -0.0000284560,
                        -0.0000344838,
                        0.0000303423,
                        ],
          '高温侧0.3T_H': [0.3174666169,
                        -0.6856533194,
                        9012.7083999999,
                        0.8456984532,
                        -0.7190351142,
                        0.0711262234,
                        -0.0200701131,
                        0.0055609940,
                        -0.0020926689,
                        -0.0007360373,
                        -0.0000441064,
                        -0.0008502543,
                        0.0001215779,
                        -0.0003762359,
                        0.0000141012,
                        -0.0000755632,
                        -0.0000018013,
                        0.0000052189,
                        ],
          '低温侧1T': [0.7558144581,
                    -0.7255031231,
                    9383.1903999999,
                    0.6303693148,
                    -0.9484461261,
                    0.1123299266,
                    -0.0194037882,
                    ],
          '高温侧1T': [0.7564558888,
                    -0.7255614350,
                    8998.4279999999,
                    0.6331248894,
                    -0.9483469352,
                    0.1087598657,
                    -0.0203566509,
                    ],
          '低温侧1T_L': [0.3489370403,
                      -0.6885142669,
                      16227.8000000000,
                      0.2011863604,
                      -0.3180445663,
                      -0.0218507953,
                      0.0045589216,
                      -0.0012092236,
                      -0.0010920455,
                      -0.0011162453,
                      -0.0007432452,
                      -0.0003586673,
                      -0.0004405268,
                      0.0000678038,
                      -0.0002175683,
                      0.0001499639,
                      -0.0000675002,
                      0.0000670682,
                      ],
          '高温侧1T_L': [0.3409702264,
                      -0.6877900111,
                      15672.9600000000,
                      0.2032171954,
                      -0.3175400042,
                      -0.0234589589,
                      0.0037374563,
                      -0.0003495572,
                      -0.0005099272,
                      -0.0004542519,
                      -0.0002936883,
                      -0.0001714138,
                      -0.0001852585,
                      -0.0000217248,
                      -0.0001081331,
                      0.0000124617,
                      -0.0000335207,
                      -0.0000009002,
                      ],
          '低温侧1T_H': [0.3340385336,
                      -0.6767381402,
                      9397.8336000000,
                      0.8239009054,
                      -0.7157660253,
                      0.0711242757,
                      -0.0162733595,
                      0.0048308251,
                      -0.0000845614,
                      -0.0017381149,
                      0.0011630457,
                      -0.0017633284,
                      0.0008064736,
                      -0.0010921306,
                      0.0003410048,
                      -0.0004948725,
                      0.0000779183,
                      -0.0001592391,
                      ],
          '高温侧1T_H': [0.3410848767,
                      -0.6772767787,
                      9012.8416000000,
                      0.8246711470,
                      -0.7153408952,
                      0.0710718027,
                      -0.0157019939,
                      0.0054633289,
                      0.0000683652,
                      -0.0010347402,
                      0.0011417288,
                      -0.0012321329,
                      0.0007211150,
                      -0.0007791193,
                      0.0002599786,
                      -0.0003588614,
                      0.0000528889,
                      -0.0001286113,
                      ],
          '低温侧3T': [0.7831731236,
                    -0.7279902745,
                    9378.7983999999,
                    0.6336606778,
                    -0.9381798960,
                    0.1235554041,
                    -0.0227012133,
                    ],
          '高温侧3T': [0.7816166817,
                    -0.7278487798,
                    8994.3239999999,
                    0.6367474307,
                    -0.9380952929,
                    0.1192368660,
                    -0.0237537921,
                    ],
          '低温侧3T_H': [0.3305302904,
                      -0.6868409260,
                      9368.2888000000,
                      0.8469379398,
                      -0.7405928556,
                      0.0781311075,
                      -0.0303366773,
                      0.0027872230,
                      -0.0091053953,
                      -0.0037856829,
                      -0.0030609591,
                      -0.0029012617,
                      -0.0005333246,
                      -0.0016712897,
                      0.0005409792,
                      -0.0007412280,
                      0.0003973887,
                      -0.0000215025,
                      ],
          '高温侧3T_H': [0.3376949742,
                      -0.6874922609,
                      8983.5520000000,
                      0.8479450764,
                      -0.7399192450,
                      0.0784313420,
                      -0.0296462882,
                      0.0035169246,
                      -0.0092446880,
                      -0.0033035592,
                      -0.0035605513,
                      -0.0027727361,
                      -0.0010976210,
                      -0.0017397484,
                      0.0001455536,
                      -0.0008492772,
                      0.0002398429,
                      -0.0000761613, ],
          '低温侧8T': [0.7919813738,
                    -0.7287910245,
                    9390.7815999999,
                    0.6631026741,
                    -0.9249950508,
                    0.1524989583,
                    -0.0283310088,
                    0.0127690866,
                    -0.0034033749,
                    0.0004428896,
                    ],
          '高温侧8T': [0.7892487130,
                    -0.7285426008,
                    9005.7716000000,
                    0.6646271424,
                    -0.9253983059,
                    0.1454176702,
                    -0.0295802201,
                    0.0110725738,
                    -0.0034916104,
                    0.0003377674,
                    ],
          "热导上0T": [
              0.3377497157,
              -0.6874972374,
              8897.2175999999,
              0.8881179019,
              -0.8212172636,
              0.1082607735,
              -0.0432015917,
              0.0109093292,
              -0.0076728170,
              -0.0027109210,
              -0.0005906401,
              -0.0036027828,
              0.0008286536,
              -0.0021772349,
              0.0006273633,
              -0.0008199902,
              0.0002505101,
              -0.0001684954,
              0.0000620031,
          ],
          "热导右0T": [
              0.3554197025,
              -0.6891035999,
              8829.2968000000,
              0.8878615598,
              -0.8218248515,
              0.1072452499,
              -0.0428851496,
              0.0101150949,
              -0.0084182837,
              -0.0029280348,
              -0.0013942870,
              -0.0036846236,
              0.0002519617,
              -0.0022443937,
              0.0003141367,
              -0.0008786052,
              0.0001215227,
              -0.0001988252,
              0.0000308837,
          ],
          "热导左0T": [
              0.3478168231,
              -0.6884124290,
              9196.1116000000,
              0.8943162086,
              -0.8251614320,
              0.1207984712,
              -0.0463805287,
              0.0206537157,
              -0.0105713342,
              0.0042976802,
              -0.0026950283,
              0.0006140985,
              -0.0004587201,
              -0.0001320833,
              -0.0000240096,
              -0.0000798147,
              -0.0000034596,
              -0.0000040399,
              -0.0000034404,
          ],
          "热导右8T": [
              0.4035722243,
              -0.6934811018,
              8842.3956000000,
              0.8844127680,
              -0.8263442372,
              0.1297942446,
              -0.0454442625,
              0.0147614466,
              -0.0118315617,
              0.0003807931,
              -0.0032511134,
              -0.0018616087,
              -0.0008410366,
              -0.0013341123,
              -0.0002513498,
              -0.0005199378,
              -0.0001234722,
              -0.0000886337,
              -0.0000543817,
          ],
          "热导左8T": [
              0.3959897502,
              -0.6927917860,
              9210.5220000000,
              0.8878844986,
              -0.8279983928,
              0.1375494711,
              -0.0474741690,
              0.0205701121,
              -0.0128216810,
              0.0040505571,
              -0.0037671105,
              0.0001740493,
              -0.0010842552,
              -0.0004151178,
              -0.0003789424,
              -0.0002237264,
              -0.0001921563,
              -0.0000350469,
              -0.0000692989,
          ],
          "热导上8T": [
              0.3852684368,
              -0.6918171212,
              8949.2600000000,
              0.8880351227,
              -0.8281186041,
              0.1371162138,
              -0.0480579869,
              0.0206257492,
              -0.0128563344,
              0.0039883964,
              -0.0037440420,
              0.0001119278,
              -0.0010888987,
              -0.0004422793,
              -0.0003905320,
              -0.0002239363,
              -0.0001992663,
              -0.0000270306,
              -0.0000757080,
          ],
          "热导右3T": [
              0.3749660790,
              -0.6908805432,
              8837.9272000000,
              0.8902407206,
              -0.8268644124,
              0.1269006877,
              -0.0460322360,
              0.0190866036,
              -0.0124030442,
              0.0026353712,
              -0.0038750700,
              -0.0005681141,
              -0.0013791073,
              -0.0008643329,
              -0.0005790646,
              -0.0004595192,
              -0.0002767539,
              -0.0001237571,
              -0.0001090734,
          ],
          "热导左3T": [
              0.3667816695,
              -0.6901365059,
              9205.6300000000,
              0.8900277868,
              -0.8273602917,
              0.1277152509,
              -0.0469242856,
              0.0193331372,
              -0.0126480745,
              0.0025473319,
              -0.0039069468,
              -0.0006477434,
              -0.0013817428,
              -0.0008930583,
              -0.0005875696,
              -0.0004603973,
              -0.0002829325,
              -0.0001166764,
              -0.0001152419,
          ],
          "热导上3T": [
              0.3562715039,
              -0.6891810363,
              8944.5003999999,
              0.8902714564,
              -0.8280520057,
              0.1274614940,
              -0.0480401633,
              0.0195313024,
              -0.0129754114,
              0.0025312412,
              -0.0040146048,
              -0.0007084893,
              -0.0014060993,
              -0.0009238580,
              -0.0005921319,
              -0.0004573237,
              -0.0002855152,
              -0.0001026566,
              -0.0001246300,
          ],
          "热导右1T": [
              0.3587332582,
              -0.6894048322,
              8836.4311999999,
              0.8869071230,
              -0.8334046309,
              0.1092592740,
              -0.0529391246,
              0.0103234437,
              -0.0168550098,
              -0.0030473633,
              -0.0072733688,
              -0.0036881238,
              -0.0033828124,
              -0.0020971443,
              -0.0016238629,
              -0.0007166164,
              -0.0006881302,
              -0.0001227320,
              -0.0001752885,
          ],
          # "热导左1T": [
          #     0.3504321618,
          #     -0.6886501871,
          #     9204.3124000000,
          #     0.8865070560,
          #     -0.8343069552,
          #     0.1095732283,
          #     -0.0542922166,
          #     0.0101488564,
          #     -0.0174316156,
          #     -0.0035276912,
          #     -0.0075554663,
          #     -0.0041250688,
          #     -0.0035466531,
          #     -0.0023733749,
          #     -0.0017406346,
          #     -0.0008374901,
          #     -0.0007568749,
          #     -0.0001523460,
          #     -0.0002079646,
          # ],
          #
          # "热导上1T": [
          #     0.3400612329,
          #     -0.6877073754,
          #     8943.0580000000,
          #     0.8865511372,
          #     -0.8347390239,
          #     0.1091614875,
          #     -0.0551011003,
          #     0.0101012722,
          #     -0.0176170436,
          #     -0.0036345841,
          #     -0.0075738643,
          #     -0.0041945813,
          #     -0.0035372485,
          #     -0.0023918789,
          #     -0.0017278896,
          #     -0.0008374076,
          #     -0.0007592995,
          #     -0.0001463800,
          #     -0.0002128842,
          # ],
          "热导左1T": [
              0.3503606312,
              -0.6886436843,
              9204.4463999999,
              0.8843899810,
              -0.8351263024,
              0.1058311991,
              -0.0550849984,
              0.0072854110,
              -0.0180949848,
              -0.0053005256,
              -0.0080616864,
              -0.0049191837,
              -0.0038662126,
              -0.0025634005,
              -0.0018535996,
              -0.0008439020,
              -0.0007249808,
              -0.0001518789,
              -0.0001627253,
          ],
          "热导上1T": [
              0.3399563783,
              -0.6876978431,
              8942.6268000000,
              0.8845124745,
              -0.8357496560,
              0.1053735270,
              -0.0560896225,
              0.0072635834,
              -0.0183883486,
              -0.0053931177,
              -0.0081199534,
              -0.0049929885,
              -0.0038865280,
              -0.0025913541,
              -0.0018627392,
              -0.0008516158,
              -0.0007177378,
              -0.0001596486,
              -0.0001455543,
          ],
          }

    号 = 转换[转换号]
    # if len(号) == 2:
    #     return 转换[转换号][1] / (输入 / 转换[转换号][0] - 1)  # 多项式拟合

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
        Ra = np.arccos(0.0001)
    else:
        Ra = np.arccos(((A - Amax) - (Amin - A)) / (Amax - Amin))
    # except Exception:
    #     print(f"温度計'{转换号}'のあてはめ範囲を超えたよ")
    #     Ra = 0
    return 10 ** sum(map(lambda 系数, 序数: 系数 * np.cos(Ra * 序数), チェビシェフ係数, range(len(チェビシェフ係数))))
