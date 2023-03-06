from 源.駆動 import Ls350
import numpy as np

Ls350_1 = Ls350(GPIB号=19)


def 读取csv(文件名, 是否去掉首行=False):
    def 添加(列表, 数据):
        if 数据 != '':
            列表.append(float(数据))

    f = open(文件名, encoding='utf-8')
    数据表 = [[] for _ in range(len(f.readline().strip().split(',')))]
    f.seek(0, 0)
    if 是否去掉首行:
        print(f.readline())
    for 行 in f:
        list(map(lambda x, y: 添加(x, y), 数据表, 行.strip().split(',')))
    数据表 = list(map(lambda x: np.array(x[0::1]), 数据表))
    f.close()
    return 数据表


温度表 = 读取csv('真鍋cernox.csv', True)
print(温度表)


def 曲線情報打ち込む(番号=59, 名前='manabe', シリアル番号='Xcernox', 様式=3, 上限温度=400, 温度係数=1, ):
    Ls350_1.Ls3.write(f'CRVHDR {番号},{名前},{シリアル番号},{様式},{上限温度},{温度係数}')


def 曲線データ打ち込む(番号=59):
    for i in range(len(温度表[0])):
        Ls350_1.Ls3.write(f'CRVPT {番号},{i+1},{温度表[2][i]},{温度表[1][i]}')


def 曲線削除(番号=59):
    Ls350_1.Ls3.write(f'CRVDEL {番号}')

