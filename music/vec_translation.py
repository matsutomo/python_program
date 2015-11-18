__author__ = 'matsui-pc'
# -*- coding: utf-8 -*-
u"""9/25
クロマベクトルの正規化方法を試すプログラム
最大値相対比，平均0分散1
 """

import sys
import numpy as np
import pylab as pl

# listv = [ 0.48317654, 0.44104936, 0.54192421, 0.68630097, 0.42248146, 0.66038036,
          # 0.62408371, 0.47746109, 0.83219153, 0.63641032, 0.86537763, 0.63777963]

listv = [ 2405.115 , 2514.552, 1805.221,  1084.662, 2786.232, 2222.115,
          2800.263, 2450.151, 2041.411, 1523.675, 1755.028, 1902.552]

max = 0

# リスト内の最大値の相対比に変換する関数
## 入力: なし
## 出力: なし
def Relativization(listin):
    listin_re = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # print np.max(listin)
    max = np.max(listin)

    ## i番目の値がリスト内の最大値と等しければ1.0を代入
    ## 異なれば最大値との相対比を算出し代入
    for i in range(len(listin)):
        listin_re[i] = round(listin[i] / max, 8) # 書式を統一するため小数点第8位まで（四捨五入して）代入
        # print listin_re

    print listin
    print listin_re

    return listin_re


# リスト内の値を「平均が0，分散が1」に変換する関数
## 入力: 正規化するリスト
## 出力: 正規化したリスト
def Normalization(listin):

    # ### リストが渡された場合
    # if flag == 1:
    listin = list(listin) # len()がないとなってエラーが出力されたためリストにする
    listin_nor = [0.0] * len(listin) # 渡されるリストの大きさに対応

    ave = np.average(listin) # listinの平均値
    # print listin
    # print "元の平均値: " + str(ave) + "\n"

    for i in range(len(listin)):
        listin_nor[i] = listin[i] - ave # 平均値を0にする

    ave_nor = np.average(listin_nor)
    # print "正規化後の平均値: " + str(ave_nor) + "\n"

    sd = np.std(listin_nor) # listinの平均値
    # print "元の標準偏差: " + str(sd) + "\n"

    for i in range(len(listin)):
        listin_nor[i] = listin_nor[i] / sd # 標準偏差を1にする

    listin_nor = list(listin_nor) # スペクトル重心のみarrayになるためリストにする

    # print listin_nor
    # sd_nor = np.std(listin_nor) # 標準偏差を計算
    # print "正規化後の標準偏差: " + str(sd_nor)

    # ### リストが渡された場合
    # elif flag == 0: # else if
    #
    #     ave = np.average(listin) # listinの平均値
    #     listin_nor = listin - ave # 平均値を0にする
    #
    #     # ave_nor = np.average(listin_nor)
    #
    #     sd = np.std(listin_nor) # listinの平均値
    #
    #     listin_nor = listin_nor / sd # 標準偏差を1にする
    #     # sd_nor = np.std(listin_nor) # 標準偏差を計算


    return listin_nor



# リスト内の総和を1に変換する関数(P(z|d)の正規化に使用)
## 入力: 正規化するリスト
## 出力: 正規化したリスト
def Normalization_sum(listin):

    sum = 0
    print listin
    # 総和を計算し確認
    for i in xrange(len(listin)):
        sum = sum + listin[i]
    print sum

    # 総和を1に正規化
    for i in xrange(len(listin)):
        listin[i] = listin[i] / sum

    sum = 0
    for i in xrange(len(listin)):
        sum = sum + listin[i]

    print sum
    print listin

    return listin



### main文は使っていない
if __name__ == '__main__':

    # listv_re = Relativization(listv) # 最大値の相対比に変換(listv_re)
    # print "元の標準偏差: " + str(np.std(listv)) # listvの標準偏差
    # print "最大値相対比の標準偏差: " + str(np.std(listv_re))
    # print "\n"

    listv_nor = Normalization(listv) # 平均0，分散(標準偏差)1に変換(listv_nor)

    # print listv_nor


    # labelx = [1,2,3,4,5,6,7,8,9,10,11,12] # グラフ表示のx軸
    # # pl.plot(feature_c) # 折れ線グラフ
    # pl.bar(labelx, listv, color='g', alpha=0.5, align="center") # 中央寄せ
    # # pl.subplots_adjust(wspace=0.3) # x軸の間隔
    # pl.xlabel("dimension") # 次元
    # pl.ylabel("Power") # クロマ値
    # pl.show() # 表示
    #
    # pl.bar(labelx, listv_re, color='g', alpha=0.5, align="center") # 中央寄せ
    # pl.xlabel("dimension") # 次元
    # pl.ylabel("Power") # クロマ値
    # pl.show() # 表示
    #
    # pl.bar(labelx, listv_nor, color='g', alpha=0.5, align="center") # 中央寄せ
    # pl.xlabel("dimension") # 次元
    # pl.ylabel("Power") # クロマ値
    # pl.show() # 表示

