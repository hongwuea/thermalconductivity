from 源.驱动 import Ls350, K2182, K6220

from threading import Thread, Lock




def 热浴作图():
    Ls350_1 = Ls350(GPIB号=19)
    while 1:
        print(f"the1\t{Ls350_1.读电阻(通道='B')}")


def 热浴作图2():
    Ls350_2 = Ls350(GPIB号=19)
    while 1:
        # print(f"the2\t{Ls350_2.读电阻(通道='B')}")
        print(f"the2\t{Ls350_2.读加热(通道=2)}")


Thread(target=热浴作图2).start()
Thread(target=热浴作图).start()
