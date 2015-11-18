# -*- coding: utf-8 -*-

'実行するときは，mainprogramの文書の名前リストを返すときのパス'
'plsa_tfでのTFを求める関数でのパスの指定を忘れないように！！（plsa_tf.pyで指定）'
'トピック数はplsa.pyで変更'
'トピック数を変更したらplsa.pyのWrite_Csv関数のtopicnameを変更すること！！'

"歌詞データを与えてTF（出現回数）を計算しPLSAを動かすプログラム"


import sys
import codecs
import csv

import config
import plsa_tf
import plsa
import sort
import music

# import normalize_neologd



if __name__ == '__main__':

	# 日本語を含む文字列を標準入出力とやり取りする場合に書く
	# UTF-8の文字列を標準出力に出力したり，標準入力から入力したりできるようになる
	sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
	sys.stdin = codecs.getreader('utf_8')(sys.stdin)

	# print sys.getdefaultencoding() # デフォルトの文字エンコーディングの確認

	reload(sys)
	sys.setdefaultencoding('utf_8') # デフォルトのエンコーディングを変更


	# config.list_tf = [] # tf値を保存するリスト
	# config.list_alltf = [] # 各文書の全単語に対するtf値を保存するリスト
	# config.dic_allword = {} # PLSAで用いるために全単語を格納するディクショナリ

	#######################
	## 歌詞特徴ベクトルを得る
	#######################



	### 文書の名前リストを返す
	filenamelist, filelist = plsa_tf.Get_file_contents("/home/matsui-pc/matsui/lyrics_normalize/01~20")
	# filenamelist, filelist = plsa_tf.Get_file_contents("/home/matsui-pc/matsui/review/test2_normalize")

	# ### 解析対象のテキストに処理を施す
	# for i in range(len(filenamelist)):



	### tfというリストに各文書のtf値(ディクショナリ)を保存していく
	for filename in filenamelist:
		config.list_tf.append(plsa_tf.Calc_tf(filename))


	### TFを出力
	####### for i in range(len(config.list_tf)):
		####### print "********** 文書%d **********" %(i+1)
		####### print filenamelist[i]
		####### for j, k in config.list_tf[i].items():
		#######	print j,k
		####### print "\n"


	####### print "**************************** All_word 実行 ***********************************"
	# この時，渡した先の dic_aw が更新されると config.dic_allword も更新される
	plsa_tf.All_word(config.list_tf) # 全単語が保存されたディクショナリを生成する
	####### print "**************************** All_word 終了 ***********************************"


	####### print ""
	for i in xrange(len(config.list_tf)):
		####### print "************************",
		####### print filenamelist[i],
		####### print "************************"

		# if not i == 0:
		# 	print "************************** 初期化 **************************"
		# 	for word in config.dic_allword:
		# 		if not config.dic_allword[word] == 0:
		# 			config.dic_allword[word] = 0

		# 確認用
		# for j, k in config.dic_allword.items():
		# 	print j, k
		# print len(config.dic_allword)
		

		####### print "********************* All_tf 実行 ***************************************"
		config.list_alltf.append(plsa_tf.All_tf(config.list_tf[i])) # リストに追加していく
		####### print "********************* All_tf 終了 ***************************************"

	####### print len(config.dic_allword)
	####### print "リストの中身を確認  ", 
	####### print len(config.list_alltf)

	# 全単語に対する各文書のtf値が入ったリストの中身を確認
	for alltf in config.list_alltf:
		####### print "************************* 文書", 
		####### print i,
		####### print "******************************"

		list_singletf = [] # tf値を文書ごとにまとめるためのリスト

		# fw = open("./experiment/tf" + str(i) + ".txt" ,"w") # 文書ごとのtf値を保存 （あとでリストに入れるため）

		l = 0 # 総単語数を数えるための変数
		for j,k in alltf.items():
			l += 1

			# 最後の値の後に 「,」 を入れない
			####### sys.stdout.write(str(k))
			####### if l < len(config.list_alltf[i]):
				####### sys.stdout.write(",")

			# # tf値を書き込むが，最後の値の後に「,」を入れない
			# fw.write(str(k))
			# if l < len(config.list_alltf[i]):
			# 	fw.write(",")

			list_singletf.append(str(k)) # tf値をひとつずつ文字列としてリストに入れる
		
		####### print "\n"
		
		# fw.close()

		list_singletf = map(int, list_singletf) # 各要素が文字列だったものを数値に変換することによって，見た目上一つの要素とみなせるものになる

		###### print list_singletf
		###### print "\n"

		config.list_alltf_result.append(list_singletf)

	####### print "\n"

	# 確認用
	# for alltf in config.list_alltf_result:
	# 	print alltf

	# 確認用
	# for i, j in config.dic_allword.items():
	# 	print i, j

	# 単語を特定するために単語に番号を振る
	l = 0
	for word in config.dic_allword:
		config.dic_number_word[l] = word
		l += 1

	# 文書番号を特定するために文書に番号を振る
	l = 0
	for name in filenamelist:
		config.dic_filename[l] = name
		l += 1

	###### for j, k in config.dic_number_word.items():
		###### print j, k

	print "PLSA準備完了"

	'PLSAのプログラムに投げる' # 手動で入れなくても済むようになった．しかしこの結果であるP(w|z)をソートしたいため，それをまた自動でソートするプログラムを組まなければならない
	n = config.list_alltf_result # 各文書における総単語のtf値が入ったリストを代入

	"実行したら保存したファイル名を変えること"
	fw = open("/home/matsui-pc/matsui/experiment/plsa_n.csv" ,"wa") # 始めは新しく作りその後は追加で書き込んでいく
	csvWriter = csv.writer(fw) # csvファイルに書き込むための準備
	for i in range(len(n)):
		csvWriter.writerow(n[i]) # ファイル名と特徴量をcsvファイルへ書き込む
	fw.close()

	# print len(n[0])
	## 確認用
	# for i in range(len(n)):
	# 	print n[i]
	# print len(n[0])

	p = plsa.plsa(n) # plsa.py の関数plsaに投げる

	print "PLSA計算中"
	p.train() # EMステップを繰り返す

	print "\n"
	# print "*********** 最終的な出力 ************"

	print "P(z) = ",
	print p.pz # P(z)
	print "P(d|z) = ",
	print p.pz_d # P(d|z)
	print "P(w|z) = ",
	print p.pz_w # P(w|z)
	print "P(z|d,w)",
	print p.pdw_z # P(z|d,w)

	### csvファイルに書き込む
	plsa.Write_Csv(p.pz, config.dic_filename, "P(z)", 1)
	plsa.Write_Csv(p.pz_d, config.dic_filename, "P(d|z)", 2)
	plsa.Write_Csv(p.pz_w, config.dic_filename, "P(w|z)", 2)
	plsa.Write_Csv(p.pdw_z, config.dic_filename, "P(z|d,w)", 3)

	### 潜在トピック比を計算しcsvファイルに書き込む
	config.list_pd_z = plsa.Calc_pd_z(p.pz, p.pz_d)

	print "*********************"
	print config.list_pd_z
	print "*********************"

	dic_pd_z = {}
	x = 0
	for name in filenamelist:
		dic_pd_z[name] = config.list_pd_z[x]
		x += 1
	print "##################"
	print dic_pd_z
	print "###################"

	### 表のようにしてcsvファイルに書き込む際の列番号を代入
	for i in xrange(len(filenamelist) + 1):
		if i == 0:
			config.list_filecount.append(" ")
		else:
			config.list_filecount.append(filenamelist[i-1])
	config.list_cos_scale_table_csv.append(config.list_filecount)

	### 潜在トピック比による各楽曲のcos類似度を出力
	for i in xrange(len(filenamelist)):
		plsa.Cos_Scale(dic_pd_z, filenamelist, i)

	### 計算したcos尺度を簡易的にcsvファイルに書き込む
	plsa.Write_Csv_Cos(config.list_cos_scale_csv, "experiment/cos_scale/cos_scale.csv")

	### 計算したcos尺度を表のようにしてcsvファイルに書き込む
	plsa.Write_Csv_Cos(config.list_cos_scale_table_csv, "experiment/cos_scale/cos_scale_table.csv")


	####### print "\n"
	
	print "ソート中"
	sort.sort(p.pz_w, 0) # P(w|z)をソートして各トピックの出現確率の高い単語を出力
	print "********************************************************"
	sort.sort(p.pz_d, 1) # P(d|z)をソートして各トピックの出現確率の高い文書を出力

	## ソート後のP(w|z)を表示してもソートする前と同じだが，結果はきちんと表示されているためOKとしている
	# print "P(w|z) = ",
	# print p.pz_w # P(w|z)


	# うまく動かない．csvファイルにしたほうがよいかも
	# # tf値を文書ごとにまとめる
	# list_tftf = [0] * 10
	# for i in range(0,2):
	# 	f = open("/home/matsui-pc/matsui/experiment/tf" + str(i) + ".txt" , "r" )
	# 	data = f.read()
	# 	print data
	# 	list_tftf[i] = data
	# 	# list_tftf.append(data)
	# 	# list_tftf = map(int, list_tftf)
	# 	f.close()

	# print list_tftf
	# 