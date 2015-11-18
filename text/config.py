# -*- coding: utf-8 -*-

list_tf = [] # tf値を保存するリスト
list_alltf = [] # 各文書の全単語に対するtf値を保存するリスト
list_alltf_result = [] # 各文書の単語ごとの最終的なtf値の結果を保存するリスト

dic_allword = {} # PLSAで用いるために全単語を格納するディクショナリ

dic_number_word = {} # 単語に番号を振るためのディクショナリ

dic_filename = {} # ソート後にファイル名を表示するために使うディクショナリ(要らないかもしれないが単語を出力するときと同じプログラムを用いるため)

list_musicsize = [11, 19, 28, 34, 46, 56, 66, 75, 86, 96] # 正規化を行う際に1楽曲にどれだけ区間楽曲があるか数を記憶しておくリスト（最初から定義しておく）

list_pd_z = [] # 潜在トピック比P(z|d)を格納するためのリスト

dic_cos = {}
list_cos_scale_csv = []
list_cos_scale_table_csv = []
list_filecount = []