# -*- coding: utf-8 -*-
u"""
PyMIRを使って様々な音響特徴量を求めてみるサンプルプログラム
サンプルで使っている以外にもいくつか関数があります。
ファイルの読み込み・フレーム化・特徴量の算出すべてをPyMIRの関数でできます。
"""

"""
csvファイルに書き込む際のファイル名指定を忘れないこと！！！
使用楽曲のパス指定は全てで3箇所！！！
"""

import sys
sys.path.append("/home/matsui-pc/matsui/pymir") # pymirディレクトリの場所

import numpy as np
import pylab as pl
import pymir
from pymir import AudioFile
import wave
import os
import re
import MeCab
import math
import csv

import config
import vec_translation as v_t


##################### 音響特徴量を求めるための関数 ##########################


# ファイル名をリストに追加する関数(音響用)
## 入力: パス名
## 出力: リスト化したファイル名
def Get_File_Contents(path):

    filelist = []
    filenamelist = os.listdir(path)
    filenamelist.sort() # ソートする

    return filenamelist



# 特徴量抽出に必要な変数の計算を行う関数
## 入力: 各変数の値
## 出力: 特徴量抽出に必要な変数
def Prepare(fs, flength, fshift):

    flength = int(flength / 1000.0 * fs) # フレーム長をpointに直す
    'フレームシフトを利用する場合'
    fshift = int(fshift / 1000.0 * fs) # フレームシフトをpointに直す

    binsize = int(math.floor(fs / flength))
    freqbin = np.arange(0, fs, binsize)     # 周波数ビンを求める (現在は20Hz)

    # print "*******************"
    # for i in range(len(freqbin)):
    # 	print freqbin[i]
    # print "*******************"

    return flength, fshift, freqbin


# wavファイルを読み込み、フレーム化を行う関数
## 入力: ファイル名
## 出力: フレーム化した音声
def Get_Frames(wavfilepath, flength, fshift):

    wavFilePath = "/home/matsui-pc/matsui/sound/newsound_section01~10/" + wavfilepath
    wavefile = AudioFile.open(wavFilePath) # WAVファイルの読み込み

    # print len(wavefile)

    'フレームシフトを利用する場合'
    frames = wavefile.frames(flength, fshift, np.hamming) # フレーム化(フレームシフトを追加したもの)(フレーム数が倍になっていたためきちんと動いている)
    'フレームシフトを利用しない場合' "pymirのFrame.pyを変更"
    # frames = wavefile.frames(flength, np.hamming) # フレーム化

    # print "############# frames ###################"
    # print len(frames)

    return frames


# クロマベクトル値をプロットする関数
## 入力: フレーム化した楽曲
## 出力: 楽曲ごとのクロマ値の平均
def Chroma_last(frames):

    len_frames = len(frames)

    chroma_sum = [0,0,0,0,0,0,0,0,0,0,0,0]
    chroma_ave = [0,0,0,0,0,0,0,0,0,0,0,0]

    # print frames
    # print "\n"

    for frame in frames:
        spectrum = frame.spectrum() # スペクトル(虚数も入ってます)
        # spectrum_abs = np.abs(spectrum) # 振幅スペクトルが欲しいならNumPyのabsを使う
        chroma = spectrum.chroma() # クロマベクトル

        # print chroma
        # print "\n"
        # print "***********************"

        for i in range(len(chroma)):
            chroma_sum[i] = chroma_sum[i] + chroma[i] # 平均を得るため和をとる
        # chroma_sum = chroma_sum + chroma # 平均を得るため和をとる

    # print "************************"
    # print chroma_sum
    # print "************************"
    for i in range(len(chroma_sum)):
        chroma_ave[i] = chroma_sum[i] / len_frames # フレームごとを総和したクロマベクトルの平均を求める

    return chroma_ave

# 5区間でクロマベクトルを抽出
## 入力: フレーム化した楽曲
## 出力: 5区間のクロマベクトルをまとめたリスト
def Chroma(frames):

    len_frames = len(frames)
    # print "フレーム数: " + str(len_frames) # 確認用
    interval = int(len_frames / 5) # 1楽曲を5区間に分けるため
    rest = len_frames - (interval * 5) # 割り切れなかった場合は最後の区間で調節
    # print "余ったフレーム数: " + str(rest) # 確認用

    chroma_sum = [0,0,0,0,0,0,0,0,0,0,0,0]
    chroma_ave = [0,0,0,0,0,0,0,0,0,0,0,0]
    chroma_ave_all = [] # 楽曲ごとのクロマベクトル（5区間）を保存
    count = 0 # 5区間に分けるためにフレームを数える
    count_inter = 1 # 区間を数える

    ### 5区間に分けて特徴量を抽出
    for frame in frames:
        spectrum = frame.spectrum() # スペクトル(虚数も入ってます)
        # spectrum_abs = np.abs(spectrum) # 振幅スペクトルが欲しいならNumPyのabsを使う
        chroma = spectrum.chroma() # クロマベクトル取得

        for i in range(len(chroma)):
            chroma_sum[i] = chroma_sum[i] + chroma[i] # 平均を得るため和をとる

        count += 1

        # intervalまで来たら平均を求める
        if count == interval:
            # print count # 確認用
            for i in range(len(chroma_sum)):
                chroma_ave[i] = chroma_sum[i] / interval # フレームごとを総和したクロマベクトルの平均を求める
            # print chroma_ave # 確認用

            chroma_ave_all.append(chroma_ave) # 各区間ごとのクロマの平均をリストに追加していく

            # 各値を初期化
            chroma_sum = [0,0,0,0,0,0,0,0,0,0,0,0]
            chroma_ave = [0,0,0,0,0,0,0,0,0,0,0,0]
            count = 0

            count_inter += 1 # 区間を数える
            if count_inter == 5:
                interval = interval + rest # 最後の区間でフレーム数を調節するため
                # print "最後の区間のフレーム数: " + str(interval) # 確認用

    return chroma_ave_all



# クロマベクトルの平均を出力する関数
## 入力: 特徴量(クロマの平均)，ファイル名
## 出力:
def Out_Chroma_last(feature_c, filename):

    print filename + ":"
    print "********************"
    print "クロマの平均"
    print feature_c
    print "\n"

    feature_c_csv = [0] # ファイル名とクロマ特徴量を同じ行に書き込むため
    feature_c_csv[0] = filename

    for f in feature_c:
        feature_c_csv.append(f) # 特徴量をリストに追加していく

    """ 上書きするために最初のファイル名を指定する """""
    if filename == "01_01.wav":
        fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma_test.csv" ,"w") # 新しく書き込む
    else:
        fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma_test.csv" ,"a") # 追加で書き込む

    csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
    csvWriter.writerow(feature_c_csv) # ファイル名と特徴量をcsvファイルへ書き込む

    'txtファイルに書き込む場合'
    # fw.write(str(filename))
    # fw.write("\n********************\n")
    # fw.write("クロマの平均\n")
    # fw.write(str(feature_c))
    # fw.write("\n\n\n")

    fw.close()


# 各楽曲の各区間ごとのクロマベクトルの平均を出力する関数
## 入力: 特徴量(クロマの平均(12次元✕5区間))，ファイル名
## 出力:
def Out_Chroma(feature_c, filename):

    print filename + ":"
    print "********************"
    print "クロマの平均"
    print feature_c
    print "\n"

    for i in range(len(feature_c)):
        feature_c_csv = [0] # ファイル名とクロマ特徴量を同じ行に書き込むため
        if i == 0:
            feature_c_csv[0] = filename # 1区間目の0番目にファイル名を入れる
        else:
            feature_c_csv[0] = " " # 2区間目以降の0番目には何も入れない

        for f in feature_c[i]:
            feature_c_csv.append(f)

        fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma.csv" ,"a") # 書き込んでいく

        csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
        csvWriter.writerow(feature_c_csv) # ファイル名と特徴量をcsvファイルへ書き込む

    # csvWriter.writerow("\n") # 1楽曲ごとに改行を入れる → リストにする際エラーが出てしまうため省く

    fw.close()

    #
    # feature_c_csv = [0] # ファイル名とクロマ特徴量を同じ行に書き込むため
    # feature_c_csv[0] = filename
    #
    # for f in feature_c:
    #     feature_c_csv.append(f) # 特徴量をリストに追加していく
    #
    # """ 上書きするために最初のファイル名を指定する """""
    # # if filename == "01_01.wav":
    # #     fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma_test.csv" ,"w") # 新しく書き込む
    # # else:
    #
    #
    # fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma_test.csv" ,"a") # 追加で書き込む
    #
    # csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
    # csvWriter.writerow(feature_c_csv) # ファイル名と特徴量をcsvファイルへ書き込む
    #
    # 'txtファイルに書き込む場合'
    # # fw.write(str(filename))
    # # fw.write("\n********************\n")
    # # fw.write("クロマの平均\n")
    # # fw.write(str(feature_c))
    # # fw.write("\n\n\n")
    #
    # fw.close()

### グラフ表示
# labelx = [1,2,3,4,5,6,7,8,9,10,11,12] # グラフ表示のx軸
# # pl.plot(feature_c) # 折れ線グラフ
# pl.bar(labelx, feature_c, color='g', alpha=0.5, align="center") # 中央寄せ
# # pl.subplots_adjust(wspace=0.3) # x軸の間隔
# pl.xlabel("dimension") # 次元
# pl.ylabel("Power") # クロマ値
# pl.show() # 表示


if __name__ == '__main__':

    list_filename_sound = [] # 楽曲のファイル名を格納するリスト
    # list_filename_lyrics1 = [] # 歌詞のファイル名を格納するリスト
    list_frames = [] # フレーム化した音源を格納するリスト
    list_chroma_ave = [] # クロマベクトルの平均を格納するリスト
    list_filecount = [] # 表のようにcsvに書き込む際の列番号を格納するリスト
    
    list_chroma_ave_all = [] # 各区間のクロマの平均を格納するリスト(1要素が1区間のクロマ平均)

    ### クロマベクトル用のフレーム長とフレームシフト
    F_LENGTH_CHROMA = 500
    F_SHIFT_CHROMA = 250
    fs = 44100 # サンプリング周波数

    ###################
    ## クロマベクトルによる特徴量抽出
    ###################

    print "〜楽曲のファイル名を取得〜"
    print "\n"
    list_filename_sound = Get_File_Contents("/home/matsui-pc/matsui/sound/newsound_section01~10") # ファイル名をリスト型で取得
    # list_filename_sound = Get_File_Contents("/home/matsui-pc/matsui/sound/sound_test2") # ファイル名をリスト型で取得

    print "〜特徴量抽出準備〜"
    print "\n"
    ### 特徴量抽出に必要な変数の計算
    flength, fshift, freqbin = Prepare(fs, F_LENGTH_CHROMA, F_SHIFT_CHROMA)

    print "〜楽曲ごとにフレーム化を行う〜"
    print "\n"
    ### 楽曲ごとにフレーム化を行いリストに追加していく
    for i in range(len(list_filename_sound)):
        print str(list_filename_sound[i]) + "読み込み"
        list_frames.append(Get_Frames(list_filename_sound[i], flength, fshift))

    print "〜クロマベクトルによる特徴量を計算中〜"
    print "\n"

    ### クロマベクトルにより特徴量(平均)抽出
    for i in range(len(list_frames)):
        list_chroma_ave_all.append(Chroma(list_frames[i]))

    print "\n"
    print list_chroma_ave_all # 確認用
    print len(list_chroma_ave_all) # 確認用
    print len(list_chroma_ave_all[0]) # 確認用

    ### 平均0分散1に正規化(各楽曲の各区間において)
    for i in range(len(list_chroma_ave_all)):
        for j in range(len(list_chroma_ave_all[0])):
            list_chroma_ave_all[i][j] = v_t.Normalization(list_chroma_ave_all[i][j])

    ### 特徴量（各区間のクロマベクトルの平均）の出力
    for i in range(len(list_chroma_ave_all)):
        Out_Chroma(list_chroma_ave_all[i], list_filename_sound[i])


    sys.exit()
    
    ### 平均0分散1に正規化
    for i in range(len(list_chroma_ave)):
        # 	# print "元の値"
        # 	# print list_chroma_ave[i]
        list_chroma_ave[i] = v_t.Normalization(list_chroma_ave[i])
    # 	# print "正規化"
    # 	# print list_chroma_ave[i]

    # ### 各楽曲の特徴量を次元ごとに平均0分散1に正規化 → できているか怪しい(11/13)
    # Pre_Normalization(list_chroma_ave)

    ### 特徴量(クロマベクトルの平均)出力
    for i in range(len(list_chroma_ave)):
        Out_Chroma(list_chroma_ave[i], list_filename_sound[i])


