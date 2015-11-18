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



# 森長先輩のプログラム
##
##
def Get_Centroid(wavfilepath, fs, flength, fshift, freqbin):

	wavFilePath = "/home/matsui-pc/matsui/sound/newsound_section01~10/" + wavfilepath
	wavefile = AudioFile.open(wavFilePath) # WAVファイルの読み込み

	slength = len(wavefile) # 音声の長さ
	# print "******************"
	# print slength
	fnum = int(math.floor((slength - flength) / fshift + 1))

	""" pymir/Frame.py """
	frames = wavefile.frames(flength, fshift, np.hamming) # フレーム化

	""" 関数preprocess """
	preprocess_result = preprocess(wavefile, fs, flength, fshift, fnum)

	spectrum_complex = preprocess_result[0]
	spectrum_abs = preprocess_result[1]
	powerspec = spectrum_abs ** 2

	""" 関数Centroid """
	centroid = Centroid(powerspec, freqbin, fs, wavfilepath)
	return centroid


# 森長先輩のプログラム
##
##
def ham(frame):
	u"""ハミング窓を掛ける
    frame: 一フレーム分（array型）
    """
	n = frame.shape[0]
	i = np.array([range(1, n + 1)])
	wh = 0.54 - 0.46 * np.apply_along_axis(math.cos, 0, 2 * i * math.pi / n)    # ハミング窓
	w = frame * wh

	return w


# 森長先輩のプログラム
##
##
def preprocess(y, fs, flength, fshift, fnum):
	u"""音響信号の前処理（フレーム化・窓掛け・FFT）をする
    y: 音響信号
    fs: サンプリング周波数
    flength: フレーム長
    fshift: フレームシフト
    fnum: フレーム数
    """
	X = np.zeros([fnum, flength])    # フレーム化後のデータを格納する
	binSize = int(math.floor(fs / X.shape[1]))
	freqBin = np.arange(0, fs, binSize)

	start = 0       # 切り取り開始点
	end = flength - 1   # 切り取り終了点
	for t in range(fnum):   # フレーム化する
		X[t, 0:(flength - 1)] = y[start:end]
		start += fshift
		end += fshift

	""" 関数ham """
	W = np.apply_along_axis(ham, 1, X)          # 窓を掛ける

	S = np.apply_along_axis(np.fft.fft, 1, W)   # FFTする
	spe = np.absolute(S)        # 振幅スペクトル
	angdft = np.angle(S)        # 位相角
	specSum = np.apply_along_axis(np.sum, 1, spe)
	specRate = spe / specSum.reshape((fnum, 1)) * 100   # 振幅比率

	return [S, spe, specRate, angdft, freqBin]



# スペクトル重心を計算する関数
## 入力 パワースペクトル，周波数ビン，サンプリング周波数
## 出力 スペクトル重心
def Centroid(powSpectrum, freqBin, fs, filename):
	u"""スペクトル重心を算出する
    入力
    powSpectrum: パワースペクトル[フレーム数, フレーム長]
    freqBin: 周波数ビン
    fs: サンプリング周波数
    出力
    centroid: スペクトル重心[フレーム数]
    """
	cent_sum = 0 # 和を格納する変数
	cent_ave = 0 # スペクトル重心の平均を格納する変数

	xSize = powSpectrum.shape
	freqBin = freqBin * (10 ** (-3))
	centroid = np.zeros(xSize[0])
	sum_x = np.zeros(xSize[0])

	for i in range(xSize[0]):
		sum_x[i] = np.sum(powSpectrum[i, 0:np.round(xSize[1] / 2)])
		centroid[i] = (np.dot(powSpectrum[i, 0:np.round(xSize[1] / 2)],
							  freqBin[0:np.round(xSize[1]) / 2]) / sum_x[i])

	centroid = np.nan_to_num(centroid) # 何をしているか分からない

	cent_ave = np.average(centroid) # 各楽曲におけるスペクトル重心の平均を出力

	# print "*******************:"
	# print centroid
	# print len(centroid)

	# print filename
	# print "********************"
	# print "スペクトル重心の平均"
	# print cent_ave
	# print "\n"

	return cent_ave



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



# MFCC値をプロットする関数
## 入力: フレーム化した楽曲
## 出力: 楽曲ごとのMFCC値の平均
def Mfcc_last(frames):

	len_frames = len(frames)

	# フレーム化処理したものを出力
	## print frames
	# print "******************************"
	# print "MFCC詳細"

	# "******"
	# print len(frames)
	# "******"
	# count = 0
	mfcc_sum = 0

	### 特徴量を求める操作はフレームごとに行う。ループするたびに変数の中身が現在のフレームの結果で書き換えられている
	for frame in frames:
		spectrum = frame.spectrum() # スペクトル(虚数も入ってます)
		spectrum_abs = np.abs(spectrum) # 振幅スペクトルが欲しいならNumPyのabsを使う
		mfcc = spectrum.mfcc2(numFilters=13) # MFCC(12次元+パワー)

		# # フレームごとのMFCCを出力(12次元)
		# print mfcc
		# print "\n"

		mfcc_sum = mfcc_sum + mfcc # 平均を得るため和をとる

		## 02.wav音源ではフレーム1603以降は無音になっているため出力はなし。
		## サビ区間を切り取って来て平均を求める。

		# count += 1;
		# if(count == 1602): # 02.wavの場合
		# 	break;

	# print count
	# print len(frames)
	# sys.exit()
	mfcc_ave = mfcc_sum / len_frames # フレームごとを総和したMFCCの平均を求める

	return mfcc_ave



# MFCC値を抽出し，パワーを取り除く
## 入力: フレーム化した楽曲
## 出力: 楽曲ごとのMFCC値の平均
def Mfcc(frames):

	len_frames = len(frames)
	# print "フレーム数: " + str(len_frames)

	# print "フレーム数: " + str(len_frames) # 確認用
	interval = int(len_frames / 5) # 1楽曲を5区間に分けるため
	rest = len_frames - (interval * 5) # 割り切れなかった場合は最後の区間で調節
	# print "余ったフレーム数: " + str(rest) # 確認用

	mfcc_sum = [0,0,0,0,0,0,0,0,0,0,0,0,0] # 1次元目はパワーなので13次元用意
	mfcc_ave = [0,0,0,0,0,0,0,0,0,0,0,0,0]
	mfcc_ave_all = [] # 楽曲ごとのMFCC(5区間)を保存
	count = 0 # 5区間に分けるためにフレームを数える
	count_inter = 1 # 区間を数える

	### 特徴量を求める操作はフレームごとに行う。ループするたびに変数の中身が現在のフレームの結果で書き換えられている
	### 5区間に分けて特徴量を抽出
	for frame in frames:
		spectrum = frame.spectrum() # スペクトル(虚数も入ってます)
		spectrum_abs = np.abs(spectrum) # 振幅スペクトルが欲しいならNumPyのabsを使う
		mfcc = spectrum.mfcc2(numFilters=13) # MFCC(12次元+パワー)

		for i in range(len(mfcc)):
			mfcc_sum[i] = mfcc_sum[i] + mfcc[i] # 平均を得るため和をとる

		count += 1

		# intervalまで来たら平均を求める
		if count == interval:
			# print count #確認用
			for i in range(len(mfcc_sum)):
				mfcc_ave[i] = mfcc_sum[i] / interval # 各フレームを総和したMFCCの平均を求める
			# print mfcc_ave # 確認用

			mfcc_ave = Pop(mfcc_ave) # 1次元目のパワーを削除
			# print mfcc_ave # 確認用

			mfcc_ave_all.append(mfcc_ave) # 各区間のMFCCの平均をリストに追加していく

			# 各値を初期化
			mfcc_sum = [0,0,0,0,0,0,0,0,0,0,0,0,0] # 1次元目はパワーなので13次元
			mfcc_ave = [0,0,0,0,0,0,0,0,0,0,0,0,0]
			count = 0

			count_inter += 1 # 区間を数える
			if count_inter == 5:
				interval = interval + rest # 最後の区間でフレーム数を調節するため
				# print "最後の区間のフレーム数: " + str(interval) # 確認用

	return mfcc_ave_all


# クロマベクトル値をプロットする関数
## 入力: フレーム化した楽曲
## 出力: 楽曲ごとのクロマ値の平均
def Chroma(frames):

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



# スペクトル重心をpymirによって求める関数
## 入力: フレーム化した楽曲
## 出力: 楽曲ごとのスペクトル重心の平均
def Centroid_pymir(frames):

	len_frames = len(frames)
	# print "フレーム数: " + str(len_frames) # 確認用
	interval = int(len_frames / 5) # 1楽曲を5区間に分けるため
	rest = len_frames - (interval * 5) # 割り切れなかった場合は最後の区間で調節
	# print "余ったフレーム数: " + str(rest) # 確認用

	cent_p_sum = 0
	cent_p_ave = 0
	cent_p_ave_all = [] # 楽曲ごとのスペクトル重心(5区間)を保存
	count = 0 # 5区間に分けるためにフレームを数える
	count_inter = 1 # 区間を数える

	### 5区間に分けて特徴量を抽出
	for frame in frames:
		spectrum = frame.spectrum() # スペクトル(虚数も入ってます)
		# spectrum_abs = np.abs(spectrum) # 振幅スペクトルが欲しいならNumPyのabsを使う
		centroid_p = spectrum.centroid() # スペクトル重心

		cent_p_sum = cent_p_sum + centroid_p # 平均を得るため和をとる

		count += 1

		# intervalまで来たら平均を求める
		if count == interval:
			# print count # 確認用
			cent_p_ave = cent_p_sum / len_frames # フレームごとを総和したクロマベクトルの平均を求める

			cent_p_ave_all.append(cent_p_ave) # 各区間ごとのスペクトル重心の平均をリストに追加していく

			# 各値を初期化
			cent_p_sum = 0
			cent_p_ave = 0
			count = 0

			count_inter += 1 # 区間を数える
			if count_inter == 5:
				interval = interval + rest # 最後の区間でフレーム数を調節するため
				# print "最後の区間のフレーム数: " + str(interval) # 確認用

	return cent_p_ave_all




	# cent_p_sum = [0]
	# cent_p_ave = [0]
    #
	# # print frames
	# # print "\n"
    #
	# for frame in frames:
	# 	spectrum = frame.spectrum() # スペクトル(虚数も入ってます)
	# 	# spectrum_abs = np.abs(spectrum) # 振幅スペクトルが欲しいならNumPyのabsを使う
	# 	centroid_p = spectrum.centroid() # スペクトル重心
	# 	# print centroid_p
	# 	# print centroid_p
	# 	# print "\n"
	# 	# print "***********************"
    #
	# 	cent_p_sum[0] = cent_p_sum[0] + centroid_p # 平均を得るため和をとる
    #
	# # print "************************"
	# # print list_cent_p_sum
	# # print "************************"
	# # print "********"
	# # print cent_p_sum
	# # print len_frames
	# cent_p_ave[0] = cent_p_sum[0] / len_frames # フレームごとを総和したクロマベクトルの平均を求める
    #
	# # print "pymirによるスペクトル重心"
	# # print cent_p_ave
    #
	# return cent_p_ave



# MFCCの平均を出力する関数
## 入力: 特徴量(MFCCの平均)，ファイル名
## 出力:
def Out_Mfcc_last(feature_m, filename):

	# print filename + ":"
	# print "********************"
	# print "MFCCの平均"
	# print feature_m
	# print "\n"

	feature_m_csv = [0] # ファイル名とmfcc特徴量を同じ行に書き込むため
	feature_m_csv[0] = filename

	for f in feature_m:
		feature_m_csv.append(f) # 特徴量をリストに追加していく

	""" 上書きするために最初のファイル名を指定する """""
	if filename == "01_01.wav":
		fw = open("/home/matsui-pc/matsui/experiment_music/mfcc/mfcc.csv" ,"w") # 新しく書き込む
	else:
		fw = open("/home/matsui-pc/matsui/experiment_music/mfcc/mfcc.csv" ,"a") # 追加で書き込む

	csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
	csvWriter.writerow(feature_m_csv) # ファイル名と特徴量をcsvファイルへ書き込む

	'txtファイルに書き込む場合'
	# fw.write(str(filename))
	# fw.write("\n********************\n")
	# fw.write("MFCCの平均\n")
	# fw.write(str(feature_m))
	# fw.write("\n\n\n")

	fw.close()

	# pl.plot(feature_m)
	# pl.xlabel("dimension") # 次元
	# pl.ylabel("Power") # MFCC値
	# pl.show() # 表示



# 各楽曲の各区間ごとのMFCCの平均を出力する関数
## 入力: 特徴量(MFCCの平均(12次元✕5区間))，ファイル名
## 出力:
def Out_Mfcc(feature_m, filename):

	# print filename + ":"
	# print "********************"
	# print "MFCCの平均"
	# print feature_m
	# print "\n"

	for i in range(len(feature_m)):
		feature_m_csv = [0] # ファイル名とmfcc特徴量を同じ行に書き込むため
		if i == 0:
			feature_m_csv[0] = filename # 1区間目の0番目にファイル名を入れる
		else:
			feature_m_csv[0] = " " # 2区間目以降の0番目には何も入れない

		for f in feature_m[i]:
			feature_m_csv.append(f) # 特徴量をリストに追加していく

		fw = open("/home/matsui-pc/matsui/experiment_music/mfcc/mfcc.csv" ,"a") # 書き込んでいく

		csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
		csvWriter.writerow(feature_m_csv) # ファイル名と特徴量をcsvファイルへ書き込む

	# csvWriter.writerow("\n") # 1楽曲ごとに改行を入れる → リストにする際エラーが出てしまうため省く

	fw.close()




#
# # クロマベクトルの平均を出力する関数
# ## 入力: 特徴量(クロマの平均)，ファイル名
# ## 出力:
# def Out_Chroma(feature_c, filename):
#
# 	print filename + ":"
# 	print "********************"
# 	print "クロマの平均"
# 	print feature_c
# 	print "\n"
#
# 	feature_c_csv = [0] # ファイル名とクロマ特徴量を同じ行に書き込むため
# 	feature_c_csv[0] = filename
#
# 	for f in feature_c:
# 		feature_c_csv.append(f) # 特徴量をリストに追加していく
#
# 	""" 上書きするために最初のファイル名を指定する """""
# 	if filename == "01_01.wav":
# 		fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma1.csv" ,"w") # 新しく書き込む
# 	else:
# 		fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma1.csv" ,"a") # 追加で書き込む
#
# 	csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
# 	csvWriter.writerow(feature_c_csv) # ファイル名と特徴量をcsvファイルへ書き込む
#
# 	'txtファイルに書き込む場合'
# 	# fw.write(str(filename))
# 	# fw.write("\n********************\n")
# 	# fw.write("クロマの平均\n")
# 	# fw.write(str(feature_c))
# 	# fw.write("\n\n\n")
#
# 	fw.close()
#
# 	### グラフ表示
# 	# labelx = [1,2,3,4,5,6,7,8,9,10,11,12] # グラフ表示のx軸
# 	# # pl.plot(feature_c) # 折れ線グラフ
# 	# pl.bar(labelx, feature_c, color='g', alpha=0.5, align="center") # 中央寄せ
# 	# # pl.subplots_adjust(wspace=0.3) # x軸の間隔
# 	# pl.xlabel("dimension") # 次元
# 	# pl.ylabel("Power") # クロマ値
# 	# pl.show() # 表示



# スペクトル重心を出力する関数
## 入力: 特徴量(スペクトル重心)，ファイル名
## 出力:
def Out_Centroid(feature_cent, filename):

	# print filename + ":"
	# print "****************************************************"
	# print "スペクトル重心"
	# print feature_cent
	# print "\n"

	feature_cent_csv = [0] # ファイル名とクロマ特徴量を同じ行に書き込むため
	feature_cent_csv[0] = filename

	for f in feature_cent:
		feature_cent_csv.append(f) # 特徴量をリストに追加していく

	""" 上書きするために最初のファイル名を指定する """""
	if filename == "01_01.wav":
		fw = open("/home/matsui-pc/matsui/experiment_music/centroid/centroid.csv" ,"w") # 新しく書き込む
	else:
		fw = open("/home/matsui-pc/matsui/experiment_music/centroid/centroid.csv" ,"a") # 追加で書き込む

	csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
	csvWriter.writerow(feature_cent_csv) # ファイル名と特徴量をcsvファイルへ書き込む

	fw.close()


# 音響特徴量を出力する関数
## 入力: 音響特徴量，ファイル名
## 出力: 音響特徴量（MFCC12次元 + クロマ12次元 + (スペクトル重心1次元) = 24(25)次元）
def Out_MusicFeature(features, filename):

	# print filename + ":"
	# print "****************************************************"
	# print "音響特徴量の出力(ディクショナリ)"
	# print features
	# print "\n"

	for i in range(len(features)): # 5
		musicfeatures_csv = [0] # ファイル名と同じ行に書き込むため
		if i == 0:
			musicfeatures_csv[0] = filename # 1区間目の0番目にファイル名を入れる
		else:
			musicfeatures_csv[0] = " " # 2区間目以降の0番目には何も入れない

		for j in range(len(features[0])): # 12
			musicfeatures_csv.append(features[i][j])

		fw = open("/home/matsui-pc/matsui/experiment_music/musicfeature/musicfeatures.csv" ,"a") # 書き込む

		csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
		csvWriter.writerow(musicfeatures_csv) # ファイル名と特徴量をcsvファイルへ書き込む

	fw.close()

    #
	# musicfeature_csv = [0] # ファイル名と音響特徴量を同じ行に書き込むため
	# musicfeature_csv[0] = filename
    #
	# for f in features:
	# 	musicfeature_csv.append(f) # 特徴量をリストに追加していく
    #
	# """ 上書きするために最初のファイル名を指定する """""
	# if filename == "01_01.wav":
	# 	fw = open("/home/matsui-pc/matsui/experiment_music/musicfeature/musicfeature.csv" ,"w") # 新しく書き込む
	# else:
	# 	fw = open("/home/matsui-pc/matsui/experiment_music/musicfeature/musicfeature.csv" ,"a") # 追加で書き込む
    #
	# csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
	# csvWriter.writerow(musicfeature_csv) # ファイル名と特徴量をcsvファイルへ書き込む
    #
	# fw.close()



# 楽曲ごとに特徴量をまとめる関数
## 入力: MFCC,クロマベクトルによる特徴量(それぞれ12次元)
## 出力: 1つにまとまった特徴量(24次元)
'スペクトル重心を利用する場合'
def Unity_Feature_last(feature_m, feature_c, feature_cent):

	list_feature = [] # まとめるためのリスト
	for i in range(len(feature_m)):
		list_feature.append(feature_m[i])

	for i in range(len(feature_c)):
		list_feature.append(feature_c[i])

	feature_cent = list(feature_cent)
	list_feature.append(feature_cent[0])

	# print "****************************"
	# print list_feature
	# print "*****************************"

	return list_feature


# 楽曲ごとに特徴量(5区間)をまとめる関数
## 入力: MFCC,クロマベクトルによる特徴量(それぞれ12次元)
## 出力: 1つにまとまった特徴量(24次元)
'スペクトル重心を利用する場合'
def Unity_Feature(features_m, features_c, feature_cent):

	list_feature = [] # 各区間の特徴量をまとめるリスト
	list_features = [] # 各楽曲(5区間)の特徴量をまとめるリスト

	for i in range(len(features_m)): # 5
		for j in range(len(features_m[i])): # 12
			list_feature.append(features_m[i][j])
		for k in range(len(features_c[i])): # 12
			list_feature.append(features_c[i][k])

		feature_cent = list(feature_cent)
		list_feature.append(feature_cent[i])
		# print "list_featureの数: " + str(len(list_feature)) # 確認用

		list_features.append(list_feature)
		list_feature = [] # 初期化

	# print "****************************"
	# print list_feature
	# print "*****************************"

	return list_features



'スペクトル重心を利用しない場合'
# def Unity_Feature(feature_m, feature_c):
#
# 	list_feature = [] # まとめるためのリスト
# 	for i in range(len(feature_m)):
# 		list_feature.append(feature_m[i])
#
# 	for i in range(len(feature_c)):
# 		list_feature.append(feature_c[i])
#
# 	# print "****************************"
# 	# print list_feature
# 	# print "*****************************"
#
#
# 	return list_feature


'クロマベクトルなし スペクトル重心ありの時'
def Unity_Feature_Nochroma(feature_m,feature_cent):

	list_feature = [] # まとめるためのリスト
	for i in range(len(feature_m)):
		list_feature.append(feature_m[i])

	feature_cent = list(feature_cent)
	list_feature.append(feature_cent[0])

	# print "****************************"
	# print list_feature
	# print "*****************************"

	return list_feature


'クロマベクトルのみ'
def Unity_Feature_Onlychroma(feature_c):

	list_feature = [] # まとめるためのリスト
	for i in range(len(feature_c)):
		list_feature.append(feature_c[i])

	return list_feature



# 1楽曲ごと特徴量の同じ次元で正規化を行うための関数
## 入力: 特徴量(2次元リスト)
## 出力: 正規化した特徴量
def Pre_Normalization(features):

	list_normalize = []
	k = 0 # 正規化した特徴量を元の値に上書きするときに使用する変数
	# print features # 確認
	# print "*********************"
	# print len(features[0])
	# print len(features)

	for i in xrange(len(features[0])):

		for j in xrange(len(features)):
			list_normalize.append(features[j][i]) # 正規化する特徴量だけ抽出

			if j+1 == 11 or j+1 == 19 or j+1 == 28 or j+1 == 34 or j+1 == 46 or j+1 == 56 or j+1 == 66 or j+1 == 75 or j+1 == 85 or j+1 == 96: ## ちゃんとしたやり方に変える
				# if j+1 == 11 or j+1 == 19:
					# print list_normalize
					# print "\n"
				list_normalize = v_t.Normalization(list_normalize) # 正規化を行い，値を上書きする
				# if j+1 == 11 or j+1 == 19:
					# print list_normalize
					# print "\n"

				for l in xrange(len(list_normalize)):
					if k == 0:
						features[k+l][i] = list_normalize[l] # 抽出した箇所の値を上書きする
					else:
						features[k+1+l][i] = list_normalize[l] # 抽出した箇所の値を上書きする また，楽曲の位置を調整
				# if j+1 == 11 or j+1 == 19:
					# print features
					# print "\n"
				list_normalize = []
				k = j # 前の値を保存
				# print "####################"

		# print "*****************************"
		k = 0 # 1楽曲終了したら初期化





##################### 類似度を算出する関数 ##########################

# 類似度を求める関数(cos尺度)
## 入力: 音響特徴量，ファイル名のリスト，何番目のファイル
## 出力: 楽曲間の類似度
def Mcos_scale_last(features, filenames, testnumber):

	vectorA = 0
	vectorB = 0
	vector = 0
	cos = 0
	n = False

	list_mcos_s_t_csv = [0] * (len(list_filename_sound) + 1) # 楽曲数+1 だけ確保
	list_mcos_s_t_csv[0] = filenames[testnumber] # 表の行番号を格納

	### cos尺度の計算
	for i in range(len(features)):

		list_mcos_s_csv = [0,0,0] # cos尺度をcsvファイルにするための内部リスト(test曲，比較曲，cos尺度)

		if n == False:
			### ベクトルAの大きさ(分母)
			for size in features[filenames[testnumber]]:
				vectorA += size * size
			vectorA = math.sqrt(vectorA)
			n = True

		### testnumberと同じ場合 → cos尺度は出力しないため --- を代入
		if i == testnumber:
			list_mcos_s_t_csv[(testnumber + 1)] = " "

		if not i == testnumber:
			### ベクトルBの大きさ(分母)
			vectorB = 0 # 初期化
			for size in features[filenames[i]]:
				vectorB += size * size
			vectorB = math.sqrt(vectorB)

			### ベクトルAとBの内積(分子)
			vector = 0 # 初期化
			for j in range(len(features[filenames[testnumber]])):
				# h = math.sqrt(features[filenames[testnumber]][j] * features[filenames[testnumber]][j])
				# s = math.sqrt(features[filenames[i]][j] * features[filenames[i]][j])
				vector += features[filenames[testnumber]][j] * features[filenames[i]][j]
			# vector += h * s

			### cos尺度の計算結果
			cos = 0 # 初期化
			cos = vector / (vectorA * vectorB)

			name = filenames[testnumber] + "+" + filenames[i]

			dic_mcos[name] = cos

			# print filenames[testnumber] + " と " + filenames[i] + " とのcos尺度: ",
			# print cos

			### 簡易的に楽曲間のcos尺度をcsvファイルに書き込むための準備
			list_mcos_s_csv[0] = filenames[testnumber]
			list_mcos_s_csv[1] = filenames[i]
			list_mcos_s_csv[2] = cos
			list_mcos_scale_csv.append(list_mcos_s_csv) # 2次元のリスト（配列）にする

			### 楽曲間のcos尺度を表のようにしてcsv形式に書き込むための準備
			list_mcos_s_t_csv[i+1] = cos

	list_mcos_scale_table_csv.append(list_mcos_s_t_csv) # 2次元のリスト（配列）にする
	# print list_mcos_scale_table_csv

	# print "\n"

	return dic_mcos



# 類似度を求める関数(cos尺度)
## 入力: 音響特徴量，ファイル名のリスト，何番目のファイル
## 出力: 楽曲間の類似度
def Mcos_scale(features, filenames, testnumber):

	vectorA = 0
	vectorB = 0
	vector = 0
	cos = 0
	n = False
	name_flag = False

	list_mcos_s_t_csv = [0] * (len(list_filename_sound) + 1) # 楽曲数+1 だけ確保
	list_mcos_s_t_csv[0] = filenames[testnumber] # 表の行番号を格納

	### cos尺度の計算
	for i in range(len(list_filename_sound)): # 96

		list_mcos_s_csv = [0,0,0,0,0,0,0,0] # cos尺度をcsvファイルにするための内部リスト(test曲，比較曲，cos尺度✕5，cos尺度の平均)

		### testnumberと同じ場合 → cos尺度は出力しないため 空白 を挿入
		if i == testnumber:
			list_mcos_s_t_csv[(testnumber + 1)] = " "

		for k in range(len(features[filenames[0]])): # 5
			if n == False:
				### ベクトルAの大きさ(分母)
				for number in range(len(features[filenames[testnumber]][0])): # 25
					# print features[filenames[testnumber]][k][number] # 確認用
					vectorA += features[filenames[testnumber]][k][number] * features[filenames[testnumber]][k][number]
				vectorA = math.sqrt(vectorA)
				n = True
				# print "n = True"
				# print "\n"


			if not i == testnumber:
				### ベクトルBの大きさ(分母)
				vectorB = 0 # 初期化
				for number in range(len(features[filenames[i]][0])): # 25
					# print "ベクトルBの大きさ"
					# print features[filenames[i]][k][number] # 確認用
					vectorB += features[filenames[i]][k][number] * features[filenames[i]][k][number]
				vectorB = math.sqrt(vectorB)

				### ベクトルAとBの内積(分子)
				vector = 0 # 初期化
				for j in range(len(features[filenames[testnumber]][0])): # 25
					# h = math.sqrt(features[filenames[testnumber]][j] * features[filenames[testnumber]][j])
					# s = math.sqrt(features[filenames[i]][j] * features[filenames[i]][j])
					# print "内積計算する値確認 test i"
					# print features[filenames[testnumber]][k][j]
					# print features[filenames[i]][k][j]
					# print "\n"
					vector += features[filenames[testnumber]][k][j] * features[filenames[i]][k][j]
					# vector += h * s

				### cos尺度の計算結果
				cos = 0 # 初期化
				cos = vector / (vectorA * vectorB)

				if k == 0:
					global name
					name = filenames[testnumber] + "+" + filenames[i]
					dic_mcos[name] = []
					name_flag = True
				dic_mcos[name].append(cos) # 各区間におけるcos尺度を追加していく
				n = False
				# print "n = False"
				# print "\n"

		if name_flag == True:
			average = 0
			average = sum(dic_mcos[name]) / len(dic_mcos[name]) # 5つのcos尺度の平均を出力
			print filenames[testnumber] + " と " + filenames[i] + " とのcos尺度: ",
			print average
			name_flag = False


			### 簡易的に楽曲間のcos尺度をcsvファイルに書き込むための準備
			list_mcos_s_csv[0] = filenames[testnumber]
			list_mcos_s_csv[1] = filenames[i]
			list_mcos_s_csv[2] = dic_mcos[name][0]
			list_mcos_s_csv[3] = dic_mcos[name][1]
			list_mcos_s_csv[4] = dic_mcos[name][2]
			list_mcos_s_csv[5] = dic_mcos[name][3]
			list_mcos_s_csv[6] = dic_mcos[name][4]
			list_mcos_s_csv[7] = average

			list_mcos_scale_csv.append(list_mcos_s_csv) # 2次元のリスト（配列）にする

			### 楽曲間のcos尺度を表のようにしてcsv形式に書き込むための準備
			list_mcos_s_t_csv[i+1] = average

	list_mcos_scale_table_csv.append(list_mcos_s_t_csv) # 2次元のリスト（配列）にする
	# print list_mcos_scale_table_csv

	# print "\n"

	return dic_mcos




# 類似度を求める関数(cos尺度)
## 入力: 歌詞特徴量
## 出力: 楽曲間の類似度
def Lcos_scale(features, filenames, testnumber):

	vectorA = 0
	vectorB = 0
	vector = 0
	cos = 0
	n = False # ベクトルAを一度だけ求めるようにする変数

	### cos尺度の計算
	for i in range(len(features)):

		if n == False:
			### ベクトルAの大きさ(分母)
			for word, size in features[filenames[testnumber]].items():
				vectorA += size * size
			vectorA = math.sqrt(vectorA)
			n = True

		if not i == testnumber:
			### ベクトルBの大きさ(分母)
			vectorB = 0 # 初期化
			for word, size in features[filenames[i]].items():
				vectorB += size * size
			vectorB = math.sqrt(vectorB)

			### ベクトルAとBの内積(分子)
			vector = 0 # 初期化
			for word, size in features[filenames[testnumber]].items():
				if word in features[filenames[i]]:
					vector += features[filenames[testnumber]][word] * features[filenames[i]][word]

			### cos尺度の計算結果
			cos = 0 # 初期化
			cos = vector / (vectorA * vectorB)

			name = filenames[testnumber] + "+" + filenames[i]

			dic_lcos[name] = cos
			# print filenames[testnumber] + " と " + filenames[i] + " とのcos尺度: ",
			# print cos

	# print "\n"

	return dic_lcos



### MFCC1次元目を削除するための関数
##
##
def Pop_last(features, filenames):
	features = list(features) # 配列からリストに変換
	p = [0,0,0,0,0,0,0,0,0,0,0,0,0] # 空リストを生成

	for i in range(len(features)):
		p[i] = (features[i])

	# print p
	p.pop(0) # 0次元目（パワー）を削除

	# print "*********************"
	# print p
	# print "\n"

	return p



### MFCC1次元目を削除するための関数
##
##
def Pop(features):
	features = list(features) # 配列からリストに変換
	p = [0,0,0,0,0,0,0,0,0,0,0,0,0] # 空リストを生成 12次元

	for i in range(len(features)):
		p[i] = (features[i])

	# print p
	p.pop(0) # 0次元目（パワー）を削除

	# print "*********************"
	# print p
	# print "\n"

	return p


### 前回のPop MFCCとクロマを合わせてから削除していた
# def Pop(features, filenames):
#
# 	for i in range(len(filenames)):
# 		popfeatures = list(features[filenames[i]])
# 		# print popfeatures[0]
# 		popfeatures.pop(0)
# 		# print popfeatures[0]
#
# 		dic_popmfeatures[filenames[i]] = popfeatures
# 		print popfeatures
# 		print "\n"
#
# 	## for i in range(len(dic_popmfeature)):
# 	## 	print dic_popmfeature[filenames[i]]
#
# 	return dic_popmfeatures



# 音響類似度と歌詞類似度から楽曲類似度を求める関数
# def Unity(mfeature, lfeature, mfilename, lfilename):

# 	for a in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
# 		b = 1.0 - a

# 		print "******************************************"
# 		print "音響類似度",
# 		print a,
# 		print "と",
# 		print "歌詞類似度",
# 		print b

# 		if len(mfilename) == len(lfilename):
# 			length = len(mfilename)
# 			for i in range(0,length):

# 				for j in range(i, length):
# 					if not i == j:
# 						name_m = mfilename[i] + "+" + mfilename[j]
# 						name_l = lfilename[i] + "+" + lfilename[j]
# 						name = str(i+1) + "+" + str(j+1)

# 						SIM[name] = a * mfeature[name_m] + b * lfeature[name_l]

# 						print name,
# 						print SIM[name]
# 				print "\t"



# cos尺度の結果をcsvファイルに書き込むための関数(cos尺度用)
## 入力: 2次元のリスト（入れ子状態）, パス
## 出力: なし
def Write_csv(lists,name):

	"""適宜保存場所を変更すること"""""
	fw = open("/home/matsui-pc/matsui/" + name ,"w") # 新しく書き込む

	csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
	csvWriter.writerows(lists) # ファイル名と特徴量をcsvファイルへ書き込む(2次元のため writerows を利用)

	fw.close()


# クロマベクトルをcsvファイルから取得する関数 → フレーム長がクロマのみ別だから
## 入力: クロマベクトルが保存されたcsvファイルの絶対パス
## 出力:
def Get_Chroma_Csv(path, filename):

	fc = open(path, "rb")
	dataReader = csv.reader(fc)
	list1 = []
	chroma_ave = [] # 各楽曲ごとのクロマベクトル（5区間）を保存 12 * 5
	chroma_ave_all = [] # 楽曲ごとのクロマのリストが入ったリスト 12 * 5 * 96
	count = 0
	for row in dataReader:
		for i, data in enumerate(row):
			if i != 0:
				list1.append(float(data))
				# print list1
		# print list1
		chroma_ave.append(list1)
		list1 = []
		# print str(filename[count]) + "取得"
		count += 1
		if count != 0 and count % 5 == 0:
			chroma_ave_all.append(chroma_ave)
			chroma_ave = [] # 初期化

	# print "*********:"
	# print chroma_ave_all[0][4] # 確認用

	return chroma_ave_all


# 各楽曲の各区間ごとのクロマベクトルの平均を出力する関数
## 入力: 特徴量(クロマの平均(12次元✕5区間))，ファイル名
## 出力:
def Out_Chroma(feature_c, filename):

	# print filename + ":"
	# print "********************"
	# print "クロマの平均"
	# print feature_c
	# print "\n"

	for i in range(len(feature_c)):
		feature_c_csv = [0] # ファイル名とクロマ特徴量を同じ行に書き込むため
		if i == 0:
			feature_c_csv[0] = filename # 1区間目の0番目にファイル名を入れる
		else:
			feature_c_csv[0] = " " # 2区間目以降の0番目には何も入れない

		for f in feature_c[i]:
			feature_c_csv.append(f)

		fw = open("/home/matsui-pc/matsui/experiment_music/chroma/chroma_test.csv" ,"a") # 正しく取得できているか確認

		csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
		csvWriter.writerow(feature_c_csv) # ファイル名と特徴量をcsvファイルへ書き込む

	# csvWriter.writerow("\n") # 1楽曲ごとに改行を入れる → リストにする際エラーが出てしまうため省く

	fw.close()



if __name__ == '__main__':

	list_filename_sound = [] # 楽曲のファイル名を格納するリスト
	# list_filename_lyrics1 = [] # 歌詞のファイル名を格納するリスト
	list_frames = [] # フレーム化した音源を格納するリスト
	list_mfcc_ave = [] # MFCCの平均を格納するリスト
	list_chroma_ave = [] # クロマベクトルの平均を格納するリスト
	list_cent_ave = [] # スペクトル重心の平均を格納するリスト
	dic_mfeature = {} # 楽曲ごとの特徴量を格納するディクショナリ
	dic_mcos = {}
	list_mcos_scale_csv = [] # 音響特徴量によるcos尺度をcsvに書き込むためのリスト
	list_mcos_scale_table_csv = [] # 音響特徴量によるcos尺度を表のようにしてcsvに書き込むためのリスト
	list_filecount = [] # 表のようにcsvに書き込む際の列番号を格納するリスト

	list_mfcc_ave_all = [] # MFCCを全て保存するリスト
	list_chroma_ave_all = [] # 取得したクロマベクトルを全て保存するリスト
	list_cent_p_ave_all = [] # スペクトル重心を楽曲(5区間)ごとにリストで保存するリスト


	# dic_all_idf = {} #
	# list_tf = [] #
	# list_all_TFIDF = [] #
	# dic_lcos = {} #
	# dic_lfeature = {} #

	dic_popmfeature = {}
	dic_popmfeatures = {}

	SIM = {}

	F_LENGTH = 50 # フレーム長
	F_SHIFT = 25 # フレームシフト
	fs = 44100 # サンプリング周波数

	###################
	## 音響特徴ベクトルを得る
	###################

	print "〜楽曲のファイル名を取得〜"
	print "\n"
	list_filename_sound = Get_File_Contents("/home/matsui-pc/matsui/sound/newsound_section01~10") # ファイル名をリスト型で取得

	print "〜特徴量抽出準備〜"
	print "\n"
	### 特徴量抽出に必要な変数の計算
	flength, fshift, freqbin = Prepare(fs, F_LENGTH, F_SHIFT)

	"""森長先輩のプログラムを利用する場合"""
	'スペクトル重心を利用する場合'
	# print "〜スペクトル重心による特徴量を計算中〜"
	# print "\n"
	# ### スペクトル重心を求める
	# for i in range(len(list_filename_sound)):
	# 	list_cent_ave.append(Get_Centroid(list_filename_sound[i], fs, flength, fshift, freqbin))
	# # print list_cent_ave
	# list_cent_ave = list(list_cent_ave)

	print "〜楽曲ごとにフレーム化を行う〜"
	print "\n"
	### 楽曲ごとにフレーム化を行いリストに追加していく
	for i in range(len(list_filename_sound)):
		print str(list_filename_sound[i]) + "読み込み"
		list_frames.append(Get_Frames(list_filename_sound[i], flength, fshift))

	print "〜MFCCによる特徴量を計算中〜"
	print "\n"

	### MFCCにより特徴量(平均)抽出
	for i in range(len(list_frames)):
		list_mfcc_ave_all.append(Mfcc(list_frames[i])) # → list_mfcc_ave_all
		# print "****************"
		# print list_mfcc_ave[i]

	# print list_mfcc_ave_all
	# print len(list_mfcc_ave_all)
	# print len(list_mfcc_ave_all[0])
	# print len(list_mfcc_ave_all[0][0])

	### 平均0分散1に正規化(各楽曲の各区間において)
	for i in range(len(list_mfcc_ave_all)):
		for j in range(len(list_mfcc_ave_all[0])):
			list_mfcc_ave_all[i][j] = v_t.Normalization(list_mfcc_ave_all[i][j])

	### 特徴量(各区間のMFCCの平均)の出力
	for i in range(len(list_mfcc_ave_all)):
		Out_Mfcc(list_mfcc_ave_all[i], list_filename_sound[i])



	# sys.exit()

	# ### MFCCによる特徴量の0次元目（パワー）を削除
	# # ### 平均0，分散1に正規化
	# for i in range(len(list_mfcc_ave)):
	# 	# print list_mfcc_ave[i]
	# 	list_mfcc_ave[i] = Pop(list_mfcc_ave[i], list_filename_sound[i])
	# 	# print list_mfcc_ave[i]
    #
	# 	list_mfcc_ave[i] = v_t.Normalization(list_mfcc_ave[i])
    #
	# 	# print "###################################"
	# 	# print list_mfcc_ave[i]
	# 	# print "\n"
    #
	# ### 各楽曲の特徴量を次元ごとに平均0分散1に正規化
	# # Pre_Normalization(list_mfcc_ave)
    #
	# ### 特徴量(MFCCの平均)出力
	# for i in range(len(list_mfcc_ave)):
	# 	Out_Mfcc(list_mfcc_ave[i], list_filename_sound[i])

	print "〜スペクトル重心を計算中〜"
	print "\n"

	### スペクトル重心をpymirの関数によって求める
	for i in xrange(len(list_frames)):
		list_cent_p_ave_all.append(Centroid_pymir(list_frames[i]))

	### 平均0分散1に正規化
	for i in range(len(list_cent_p_ave_all)):
		list_cent_p_ave_all[i] = v_t.Normalization(list_cent_p_ave_all[i])

	### 特徴量(スペクトル重心)出力
	for i in range(len(list_cent_p_ave_all)):
		Out_Centroid(list_cent_p_ave_all[i], list_filename_sound[i])



	# print 'クロマベクトル抽出のためにフレーム長・フレームシフトを変更'
	# print "〜特徴量抽出準備〜"
	# print "\n"
	# ### 特徴量抽出に必要な変数の計算
	# flength, fshift, freqbin = Prepare(fs, F_LENGTH_CHROMA, F_SHIFT_CHROMA)
    #
	# print "〜楽曲ごとにフレーム化を行う〜"
	# print "\n"
	# ### 楽曲ごとにフレーム化を行いリストに追加していく
	# for i in range(len(list_filename_sound)):
	# 	print str(list_filename_sound[i]) + "読み込み"
	# 	list_frames.append(Get_Frames(list_filename_sound[i], flength, fshift))
    #
	# print "〜クロマベクトルによる特徴量を計算中〜"
	# print "\n"
    #
	# ### クロマベクトルにより特徴量(平均)抽出
	# for i in range(len(list_frames)):
	# 	list_chroma_ave.append(Chroma(list_frames[i]))
    #
	# ### 平均0分散1に正規化
	# for i in range(len(list_chroma_ave)):
	# # 	# print "元の値"
	# # 	# print list_chroma_ave[i]
	# 	list_chroma_ave[i] = v_t.Normalization(list_chroma_ave[i])
	# # 	# print "正規化"
	# # 	# print list_chroma_ave[i]
    #
	# # ### 各楽曲の特徴量を次元ごとに平均0分散1に正規化 → できているか怪しい(11/13)
	# # Pre_Normalization(list_chroma_ave)
    #
	# ### 特徴量(クロマベクトルの平均)出力
	# for i in range(len(list_chroma_ave)):
	# 	Out_Chroma(list_chroma_ave[i], list_filename_sound[i])


	print 'クロマベクトルをcsvファイルから取得'
	print "\n"
	list_chroma_ave_all = Get_Chroma_Csv("/home/matsui-pc/matsui/experiment_music/chroma/chroma_1115frame500_section.csv", list_filename_sound)
	# print list_chroma_ave_all # 確認用

	### 特徴量（各区間のクロマベクトルの平均）の出力
	for i in range(len(list_chroma_ave_all)):
		Out_Chroma(list_chroma_ave_all[i], list_filename_sound[i])


	### 楽曲ごとに特徴量をまとめる
	for i in range(len(list_mfcc_ave_all)):
		dic_mfeature[list_filename_sound[i]] = Unity_Feature(list_mfcc_ave_all[i], list_chroma_ave_all[i], list_cent_p_ave_all[i])





	# ### 楽曲ごとに特徴量をまとめる
	# for i in range(len(list_filename_sound)):
	# 	'スペクトル重心を利用する場合'
	# 	dic_mfeature[list_filename_sound[i]] = Unity_Feature(list_mfcc_ave[i], list_chroma_ave[i], list_cent_ave[i])
	# 	'スペクトル重心を利用しない場合'
	# 	# dic_mfeature[list_filename_sound[i]] = Unity_Feature(list_mfcc_ave[i], list_chroma_ave[i])
	# 	'クロマなし スペクトル重心あり Unity_Feature_Nochroma'
	# 	# dic_mfeature[list_filename_sound[i]] = Unity_Feature_Nochroma(list_mfcc_ave[i], list_cent_ave[i])
	# 	'クロマのみ'
	# 	# dic_mfeature[list_filename_sound[i]] = Unity_Feature_Onlychroma(list_chroma_ave[i])


	### 音響特徴量の出力
	for i in range(len(list_filename_sound)):
		Out_MusicFeature(dic_mfeature[list_filename_sound[i]], list_filename_sound[i])
	# dic_popmfeature = Pop(dic_mfeature, list_filename_sound)

	### 表のようにしてcsvファイルに書き込む際の列番号を代入
	for i in range(len(list_filename_sound) + 1):
		if i == 0:
			list_filecount.append(" ")
		else:
			list_filecount.append(list_filename_sound[i-1])
	list_mcos_scale_table_csv.append(list_filecount)

	### 音響特徴量による楽曲間のcos尺度を計算して出力
	for i in range(len(list_filename_sound)):
		dic_mcos = Mcos_scale(dic_mfeature, list_filename_sound, i)

	### 計算したcos尺度を簡易的にcsvファイルに書き込む
	Write_csv(list_mcos_scale_csv, "experiment_music/mcos_scale/mcos_scale.csv")

	### 計算したcos尺度を表のようにしてcsvファイルに書き込む
	Write_csv(list_mcos_scale_table_csv, "experiment_music/mcos_scale/mcos_scale_table.csv")



	# for i in range(len(filenamelist)):
		# dic_lcos = Lcos_scale(dic_lfeature, filenamelist, i)

	# Unity(dic_mcos, dic_lcos, list_filename_sound, filenamelist)


	## print list_filename_sound


	# 2つ目

	# # ファイル名が正しく取得できているか確認
	# for i in range(len(list_filename_sound)):
	# 	print list_filename_sound[i]
	# 	print "\n"


	# get_frame = get_frames("01sabi.wav")
	# mfcc(get_frame)
