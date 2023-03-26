import time

from 源.駆動 import Ls350
import numpy as np

Ls350_1 = Ls350(GPIB号=19)


def 读取csv(文件名, 是否去掉首行=False):
    def 添加(列表, 数据):
        if 数据 != '':
            列表.append(float(数据))

    f = open(文件名, encoding='utf-8')
    数据表 = [[] for _ in range(len(f.readline().strip().split('\t')))]
    f.seek(0, 0)
    if 是否去掉首行:
        print(f.readline())
    for 行 in f:
        list(map(lambda x, y: 添加(x, y), 数据表, 行.strip().split('\t')))
    数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))
    f.close()
    return 数据表


温度表 = 读取csv('R103.csv', True)
# 温度表 = 温度表[1::]
print(温度表)


# 必ずLOG入力、さもなきゃ温度計で選択できない
def 曲線情報打ち込む(番号=21, 名前='R103', シリアル番号='R103R103', 様式=4, 上限温度=400, 温度係数=1, ):
    Ls350_1.Ls3.write(f'CRVHDR {番号},{名前},{シリアル番号},{様式},{上限温度},{温度係数}')


# 6桁有効数字制限必須、科学計数法使用不可
# 降温順にする必要がある、さもなきゃ正温度係数温度計として認識してしまう
def 曲線データ打ち込む(番号=21):
    for i in range(len(温度表[0])):
        print(f'{i}CRVPT {番号},{i + 1},{np.log10(温度表[1][-i - 1]):.6},{温度表[0][-i - 1]:.6}')
        Ls350_1.Ls3.write(f'CRVPT {番号},{i + 1},{np.log10(温度表[1][-i - 1]):.6},{温度表[0][-i - 1]:.6}')


def 曲線削除(番号=21):
    Ls350_1.Ls3.write(f'CRVDEL {番号}')


曲線削除(26)
time.sleep(1)
曲線情報打ち込む(26)
time.sleep(3)
曲線データ打ち込む(26)
