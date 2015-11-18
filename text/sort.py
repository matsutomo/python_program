# -*- coding: utf-8 -*-

import re

import config


# PLSAの結果をソートしてトピックからの単語を出力する関数
## 入力: PLSAの結果であるP(w|z)またはP(d|z)，単語(0)か文書(1)かを判別する変数
## 出力: 今のところはソートした結果
def sort(list_plsa, type):


	# print list_plsa
	## 一行（各文書）ごとにソートして出力する
	for i in xrange(len(list_plsa)):
		j = 0
		dic_plsa = {}

		list_sort = list_plsa[i]
		# print list_sort # 確認用

		## 順番に番号を振ってディクショナリに保存していく 例："1" = 0.0, "2" = 0.00224 ...
		for value in list_sort:
			dic_plsa[j] = value
			j += 1

		# ## 中身の表示
		# print "**********中身の表示**********"
		# for k, l in dic_plsa.items():
		# 	print k, l
		# print "\n"
		plsa_sort = sorted(dic_plsa.items(), key = lambda x:x[1], reverse = True) # 値の降順でソート

		## ソートした結果を表示
		print str(i+1) + "番目",
		print plsa_sort
		print "\n"

		# q = 0
		# for k in plsa_sort:
		# 	print k
		# 	q += 1
		# 	if q == 5:
		# 		break
		
		# config.dic_number_word
		
		number = re.finditer("\([\d]+," , str(plsa_sort)) # 文字列として，単語と関連付けのある数字を周辺をすべて取り出す


		## 上位5単語ずつ取り出す
		
		list_appear = [] # トピックごとに出現確率の高い単語を格納するためのリスト
		k = 0 # 上位○単語までを出力するための変数

		for match in number:
			
			k += 1

			number_word =  match.group() # 当てはまった文字列が格納
			# print number_word # 確認用
			number_word = int(number_word.strip("\(,")) # 先頭と末尾にある指定の文字を消して数値に変換
			# print number_word # 確認用

			####### print config.dic_number_word[number_word] # 単語を出力

			# 各トピックごとに出現確率の上位○単語をテキストファイルに書き込む
			if type == 0:
				list_appear.append(config.dic_number_word[number_word]) # 上位○単語までをリストに追加していく

				if k >= 20:
					f = open("/home/matsui-pc/matsui/experiment/Appearword/topic" + str(i) + ".txt" ,"w")
					for l in xrange(len(list_appear)):
						f.write(str(list_appear[l])),
						f.write(",")
					f.close()
					break

			# 各トピックごとに出現確率の上位○文書をテキストファイルに書き込む
			if type == 1:
				list_appear.append(config.dic_filename[number_word]) # 上位○単語までをリストに追加していく

				if k >= 10:
					f = open("/home/matsui-pc/matsui/experiment/Appeardocument/topic" + str(i) + ".txt" ,"w")
					for l in xrange(len(list_appear)):
						f.write(str(list_appear[l])),
						f.write(",")
					f.close()
					break

					####### print "*************************************************"