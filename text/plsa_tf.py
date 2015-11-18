# -*- coding: utf-8 -*-

import os
import re
import sys

import MeCab

import config

##################### 歌詞特徴量を求めるための関数 ##########################


# ファイル名をリストに追加する関数(歌詞用)
## 入力: パス名
## 出力: リスト化したファイル名, リスト化した歌詞
def Get_file_contents(path):
	filelist = []
	filenamelist = os.listdir(path)
	filenamelist.sort()

	####### t = 0

	for name in filenamelist:
		f = open(path + "/" + name, "r")
		data = f.read()
		filelist.append(data)
		f.close()

	return filenamelist, filelist


# 楽曲ごとのTF（出現回数）を求める関数
## 入力: ファイル名
## 出力: TF
def Calc_tf(sentence):

	f1 = open("/home/matsui-pc/matsui/lyrics_normalize/01~20/" + sentence , "r")
	# f1 = open("test2_normalize/" + sentence , "r")

	data = f1.read()

	f1.close()

	# mecab = MeCab.Tagger("--node-format=%m\s%f[0]\\n --eos-format='' ")
	mecab = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd/ --node-format=%m\s%f[0]\\n --eos-format='' ")


	result = mecab.parse(data)

	# encoded_data = data.encode('utf-8') # MeCab前にエンコードする
	# encoded_result = mecab.parse(encoded_data)
	# result = encoded_result.decode('utf-8') # MeCab後にデコード

	split = result.split() # 空白をなくす

	list1 = []

	# 確認用
	# for i in range(len(split)):
	# 	print split[i]

	word = split[0::2] # 偶数だけを取り出す 0番目 単語
	part = split[1::2] # 奇数だけを取り出す 1番目 品詞

	# 確認用
	# for i in range(len(word)):
	# 	print word[i]
	# print part[0]

	### 名詞を取り出す
	for i in xrange(len(part)):
		searchOb = re.search("名詞", part[i])
		if searchOb:
			list1.append(word[i]) # word[i]をlist1に追加する

	### 形容詞を取り出す
	for i in xrange(len(part)):
		searchOb = re.search("形容詞", part[i])
		if searchOb:
			list1.append(word[i]) # word[i]をlist1に追加する

	### 動詞を取り出す
	for i in xrange(len(part)):
		searchOb = re.search("動詞", part[i])
		if searchOb:
			list1.append(word[i]) # word[i]をlist1に追加する

	# ### 正規表現により先頭が数字の場合は削除する
	# for i in list1:
	# 	matchOb = re.match("\d", i)
	# 	if matchOb:
	# 		print "削除単語 = ",
	# 		print i
	# 		list1.remove(i)

	# ### 正規表現により括弧は削除する
	# for i in list1:
	# 	searchOb = re.search("\(+", i)
	# 	if searchOb:
	# 		list1.remove(i)

	# print "a = ",
	# print a
	# print "##########################################################"

	tf = {}

	### list1の単語を順番に調べて，tfというディクショナリ	に入ってなかったら保存
	### あとはカウントしていく
	for word in list1:
		if word not in tf:
			tf[word] = 0
		tf[word] += 1

	a = 0
	### 正規表現により一文字のものは削除する
	for j, k in tf.items():
		if len(j) == 3:
			####### print j
			tf.pop(j)
			a += 1

	### 正規表現により先頭が英数字の場合は削除する
	for j, k in tf.items():
		matchOb = re.match("[a-zA-Z0-9]", j)
		if matchOb:
			######## print "削除単語 = ",
			######## print j
			tf.pop(j)

	######## print "a = ",
	######## print a
	######## print "##########################################################"


	return tf

	### PLSAに投げるために出現回数を知りたいので正規化は行わない
	# normalize_tf = {}
	# ### 単語をキーとして正規化した値を保存 ####
	# for k, l in tf.items():
	# 	normalize_tf[k] = 1.0 * l / len(list1)

	# return normalize_tf


# PLSAで用いるために，全単語を保存したディクショナリを生成する関数
## 入力: 各文書のtf値が入ったリスト
## 出力: 全単語が保存されたディクショナリ
def All_word(sentences):

	dic_aw = {}
	dic_aw = config.dic_allword

	# 各文書の単語が config.dic_allword に入っていなければ保存していく
	for i in xrange(len(sentences)):
		for word in sentences[i]:
			if word not in dic_aw:
				dic_aw[word] = 0 # 各単語の値は0にしておく
		# print ""


# PLSAで用いるために，各文書の全単語に対するtf値を保存する関数
## 入力: 各文書
## 出力: 全単語に対するtf値が保存されたディクショナリ
def All_tf(sentence):

	dic_aw = {}
	for word in config.dic_allword:
		if word not in dic_aw:
			dic_aw[word] = 0

	####### print "**************************************** config.dic_allword ****************************************"
	####### for j, k in config.dic_allword.items():
		####### print j, k
	####### print len(config.dic_allword)

	####### print "**************************************** dic_aw ****************************************************"
	####### for j, k in dic_aw.items():
		####### print j, k
	####### print len(dic_aw)

	####### a = 0

	####### print "*************************************************************"
	####### for j, k in sentence.items():
		####### print j, k
	####### print len(sentence)
	####### print "**********************************************************"


	for word in sentence:
		####### print word, dic_aw[word], sentence[word]
		if word in dic_aw:
			dic_aw[word] = sentence[word] # 各文書中の単語のtf値を代入
		####### else:
			####### print word # 単語の漏れがないか確認
		####### print word, dic_aw[word], sentence[word]
		####### print "***"
		####### a += 1 # 確認用

	####### print a # 確認用

	####### print "\n"

	####### for j, k in dic_aw.items():
		####### print j, k

	####### print "\n"

	return dic_aw


