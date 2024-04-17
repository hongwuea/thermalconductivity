# Amax, Amin, 底,チェビシェフ係数
转换 = {
    # X86763,SD1030,0.3K~300K lakeshore cal
    'X86763': [3.1370706260, -0.9419809565, 31.1355065340, 0.8985929852, -1.7105170129, 0.0624105876, 0.4084016962,
               -0.0677766330, 0.0305181214, 0.0521930989, 0.0815308455, 0.0143915160, 0.0232346105, 0.0394865639,
               0.0128335945, 0.0163157530, 0.0013120119, 0.0127207052, -0.0011770961],
    'X86763逆': [3.5821890294, -0.9824462659, 0.2073244864, 2.6157587564, -1.4693632300, -0.3412338246, 0.0932799274,
                -0.4444565589, 0.1045076577, -0.2413682977, 0.0287180041, -0.1480131406, 0.0144954979, -0.0715157995,
                0.0022336613, -0.0246261317, -0.0016672277, -0.0051739322, -0.0003042981],

    # 1.21K~330K lakeshore cal
    "X215477": [2.0110131609082584, -0.8396120960767098, 28.54488001488072, 1.4167565902064758, -1.7831666054379633,
                -0.08845002128183405, -0.1522528940384309, 0.09739035948544457, -0.24904567504241967,
                0.028649370954221536, -0.1531841875768033, 0.02986364188636778, -0.08958819884347194,
                0.011430162255390793, -0.04463176164939255, 0.005326009432814974, -0.015527948014763886,
                0.0011969924847366382, -0.00448242813045697],

    "X215477逆": [2.8446912107940765, -0.9154010097026932, 0.9683387620224639, 2.4239106398637977, -0.8972787428918169,
                 -0.07706421151367829, 0.10773136374889637, -0.013365574517613955, 0.07761127448308475,
                 0.008640134068310535, 0.043971285580971756, -0.00017821631552247816, 0.027274536466658884,
                 -0.0005727157992517648, 0.012462557892046035, -0.0003614227107017193, 0.005035704313905159,
                 0.00022210369042878524, 0.001281710746010722],
    # X59416,SD1030
    # 0.2K~30K
    '热浴cernox银yu23-2': [2.8230148019, -0.9134304271, 245.5334400000, 0.0915123833, -1.9381860828, -0.8771928025,
                        -0.6236837898, -0.8394310675, -0.5602550134, -0.5250013902, -0.3441027797, -0.3056279648,
                        -0.1652741534, -0.1330598406, -0.0625556244, -0.0416730958, -0.0153888395, -0.0082713645,
                        -0.0016405371, ],
    # 0.6K~30K
    # '热浴cernox银yu23': [2.3755238099, -0.8727494278, 245.5334400000, 0.5637283046, -1.1968368881, -0.2113581053,
    #                   -0.0414939691, -0.2382711086, -0.1332432600, -0.1373644364, -0.0822459468, -0.0916738498,
    #                   -0.0481312569, -0.0435574211, -0.0243189697, -0.0160446381, -0.0089073868, -0.0042658209,
    #                   -0.0023841512, ],
    # 0.6K~30K
    '热浴cernox银yu23逆': [2.0558370648, -0.8436869964, 0.5880000000, 3.3054826780, -1.3633458193, -0.2239144573,
                       -0.1052912236, -0.2595764265, -0.1181148046, -0.1536917133, -0.0819450945, -0.0949067494,
                       -0.0489574043, -0.0458916867, -0.0261190402, -0.0165727051, -0.0099156016, -0.0039837479,
                       -0.0029650508, ],

    # X38425,Br1030 1.5K~40K
    '热浴1030br202206': [0.9310938486, -0.7414376131, 87.5449560000, 0.9579911592, -0.8015018331, -0.0817201075,
                       0.0406861532, 0.0066560142, -0.0086647719, -0.0012288231, -0.0014943564, -0.0002508411,
                       -0.0014979927, 0.0000219024, -0.0005051331, 0.0000053491, -0.0001972710, 0.0000420501, ],
    # 0.72K~2.3K
    '热浴1030br202206he3': [0.7286794443, -0.7230363037, 366.5740800000, 0.1379742777, -0.3330111368, -0.0516231899,
                          0.0003025203, -0.0141623651, -0.0235675760, -0.0064655204, -0.0325686340, 0.0000323073,
                          -0.0344339188, 0.0018979186, -0.0276547667, 0.0010867117, -0.0158671114, 0.0001234303,
                          -0.0052645900, ],
    '热浴1030br202206he3逆': [0.6809246022, -0.7186949544, 0.5600000000, 2.8682023380, -0.3677856953, -0.2518746654,
                           0.0063097251, -0.1638605317, -0.0267506757, -0.0945225288, -0.0402350456, -0.0401487480,
                           -0.0369585217, -0.0111266666, -0.0233875652, -0.0010771471, -0.0099301267, 0.0003326627,
                           -0.0022770414, ],

    # 0.7K~40K
    "X152854": [2.716664184619718, -0.9037621891413883, 315.38228000000004, 1.0383626292513313, 0.4629550988199473,
                0.7151052113653107, 1.419934376964997, 0.4989636896281228, 0.9956108619243638, 0.393519929887441,
                0.6662934210222712, 0.22517710910198757, 0.3734652039437372, 0.1105923826283991, 0.16517920595771685,
                0.03983021136885133, 0.05409501568030517, 0.007876111144963952, 0.009478811655593724],

    # Pt100标准曲线 10K~600K
    'Pt100': [2.4465425556, -0.8792056774, 1.2596115632, 1.7881123890, 1.0244559793, 0.0373734500, 0.1144959879,
              -0.0855576903, 0.0138721301, -0.0354176192, 0.0013689901, -0.0110946448, -0.0066300969, -0.0029422839,
              -0.0052837281, 0.0001334706, -0.0022878764, 0.0002312690, -0.0006147233, ],

    # # 0.7K~10K
    # '10kRuOx0402_1右': [0.6519298167, -0.7160590648, 10548.3231999999, 0.4085268107, -0.7079103954, -0.0441095561,
    #                    -0.0251695416, -0.0405903308, -0.0241840687, -0.0278092525, -0.0157480838, -0.0165178750,
    #                    -0.0090667445, -0.0081347041, -0.0041704102, -0.0030779444, -0.0015359367, -0.0006324233,
    #                    -0.0004178722, ],
    # '10kRuOx0402_2左': [0.6429805412, -0.7152454943, 10975.9175999999, 0.4082056038, -0.7079592306, -0.0434721319,
    #                    -0.0251945259, -0.0406492098, -0.0243098474, -0.0280088261, -0.0159032767, -0.0167088203,
    #                    -0.0091919993, -0.0082733120, -0.0042695433, -0.0031565859, -0.0015716598, -0.0006828080,
    #                    -0.0004221820, ],
    #
    # # 1.8k~40k
    # "热导右0T": [0.3554197025, -0.6891035999, 8829.2968000000, 0.8878615598, -0.8218248515, 0.1072452499, -0.0428851496,
    #           0.0101150949, -0.0084182837, -0.0029280348, -0.0013942870, -0.0036846236, 0.0002519617, -0.0022443937,
    #           0.0003141367, -0.0008786052, 0.0001215227, -0.0001988252, 0.0000308837, ],
    # "热导左0T": [0.3478168231, -0.6884124290, 9196.1116000000, 0.8943162086, -0.8251614320, 0.1207984712, -0.0463805287,
    #           0.0206537157, -0.0105713342, 0.0042976802, -0.0026950283, 0.0006140985, -0.0004587201, -0.0001320833,
    #           -0.0000240096, -0.0000798147, -0.0000034596, -0.0000040399, -0.0000034404, ],

    # 0.7k~40k
    "热导左宽温度": [0.8342835845644205, -0.732636680045452, 9176.881632, 0.16436214748602437, -2.332864405714064,
               -0.7267558673721415, -1.1069098130113906, -0.6728100742864561, -0.7595371559168678, -0.45054537263253164,
               -0.4460646848047629, -0.23956668701621261, -0.21465921081771447, -0.09828635173490376,
               -0.08001278651400742, -0.028265793864763907, -0.02085351301816642, -0.004332946033835056,
               -0.002990044521081738],
    # 0.7k~40k
    "热导右宽温度": [0.844982161599542, -0.7336092779577357, 8800.0, 0.16500112574592243, -2.384625081849763,
               -0.7299186324756829, -1.1485260861636057, -0.676115041615781, -0.7913821432605828, -0.4527045321486382,
               -0.4674573326952996, -0.24069213586422597, -0.22726168434705324, -0.09894553913443108,
               -0.08624256938588531, -0.02848457164492418, -0.023264472802936913, -0.004474396947129156,
               -0.0036664398188902786],

    # 0402RuO2 1.8K~30K
    "0402RuO2": [0.5367897464959888, -0.7055917856755942, 8721.652, 0.8593820549436804, -0.869235694905547,
                 0.10075636072009554,
                 -0.1260202555011199, 0.030632058607528854, -0.08935212652675549, 0.01858944709701887,
                 -0.05846396880822883,
                 0.010146404873348705, -0.03290649465328069, 0.004345816389581963, -0.014930232178379478,
                 0.0013427350652555502,
                 -0.005135791435147253, 0.00011235219683766764, -0.0011075821537367822
                 ]

    # # 1.8k~40k
    # "热导左0220": [0.2623431217246753, -0.6806420925145661, 9208.6592, 0.9540545059123812, -0.7585571642730484,
    #             0.13423348059213316, -0.029683501000400514, 0.03978536907455287, -0.00037859315252690564,
    #             0.01692284441575595, 0.0041247202024804995, 0.008494773170768828, 0.002884689550579226,
    #             0.003921952127461157, 0.0013231853959048423, 0.0014169804822727016, 0.0003932610112694841,
    #             0.00034012256935398767, 0.0001301452060385628],
    # # 1.8k~40k
    # "热导右0220": [0.2819936182914204, -0.6824285012933607, 8649.187199999998, 0.932090158052204, -0.796920458301729,
    #             0.0853428226018411, -0.06164016065122963, 0.0032794951198370577, -0.027513442981754642,
    #             -0.007133093431743518, -0.015077979216892815, -0.005162681556088694, -0.008467014294340271,
    #             -0.0024750316571756754, -0.004091776291379441, -0.0007870138542150658, -0.0015852349405588784,
    #             -0.000139378691372074, -0.0003010334834813353],

}
