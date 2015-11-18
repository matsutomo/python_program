# -*- coding: utf-8 -*-
""" パスを3つ指定 """

from __future__ import unicode_literals
import re
import unicodedata

import plsa_tf


# 文字列をunicodeにして処理を施す関数へ投げる関数
## 入力: 解析対象ファイル（文字列）
## 出力: 処理済みの解析対象ファイル（文字列）
def Code(sentence):

    """パスを指定"""""
    f1 = open("/home/matsui-pc/matsui/lyrics_normalize/" + sentence , "r")
    data = f1.read()

    data = data.decode('utf-8') # 文字列からUnicode型に変換
    data = (Normalize_neologd(data)).encode('utf-8') # 処理を施し，Unicode型から文字列に変換．その文字列を返す

    # 処理済みのテキストを新たなテキストファイルとして書き込む
    f = open("/home/matsui-pc/matsui/lyrics_normalize/" + sentence,"w")
    f.write(data)



def Unicode_normalize(cls, s):
    pt = re.compile('([{}]+)'.format(cls))

    def norm(c):
        return unicodedata.normalize('NFKC', c) if pt.match(c) else c

    s = ''.join(norm(x) for x in re.split(pt, s))
    return s

def Remove_extra_spaces(s):
    s = re.sub('[ 　]+', ' ', s)
    blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                      '\u3040-\u309F',  # HIRAGANA
                      '\u30A0-\u30FF',  # KATAKANA
                      '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                      '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
                      ))
    basic_latin = '\u0000-\u007F'

    def Remove_space_between(cls1, cls2, s):
        p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
        while p.search(s):
            s = p.sub(r'\1\2', s)
        return s

    s = Remove_space_between(blocks, blocks, s)
    s = Remove_space_between(blocks, basic_latin, s)
    s = Remove_space_between(basic_latin, blocks, s)
    return s


# 処理を施す関数（全角記号を半角記号にするなどの処理）
## 入力: 解析対象のテキスト（Unicode型）
## 出力: 処理済みの解析対象のテキスト（Unicode型）
def Normalize_neologd(s):
    s = s.strip()
    s = Unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)

    def Maketrans(f, t):
        return {ord(x): ord(y) for x, y in zip(f, t)}

    s = s.translate(
        Maketrans('!"#$%&\'()*０−９]Ａ+,-./:;<=>?@[\\]^_`{|}~｡､･[]',
                  '！”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))
    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
    s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
    s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
    s = Remove_extra_spaces(s)
    s = Unicode_normalize('！”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」', s)  # keep ＝,・,「,」←keepしない(10/28)
    return s


if __name__ == "__main__":
    assert "0" == Normalize_neologd("０")
    assert "1" == Normalize_neologd("１")
    assert "ハンカク" == Normalize_neologd("ﾊﾝｶｸ")
    assert "o-o" == Normalize_neologd("o₋o")
    assert "majikaー" == Normalize_neologd("majika━")
    assert "わい" == Normalize_neologd("わ〰い")
    assert "スーパー" == Normalize_neologd("スーパーーーー")
    assert "!#" == Normalize_neologd("!#")
    assert "ゼンカクスペース" == Normalize_neologd("ゼンカク　スペース")
    assert "おお" == Normalize_neologd("お             お")
    assert "おお" == Normalize_neologd("      おお")
    assert "おお" == Normalize_neologd("おお      ")
    assert "検索エンジン自作入門を買いました!!!" == \
        Normalize_neologd("検索 エンジン 自作 入門 を 買い ました!!!")
    assert "アルゴリズムC" == Normalize_neologd("アルゴリズム C")
    assert "PRML副読本" == Normalize_neologd("　　　ＰＲＭＬ　　副　読　本　　　")
    assert "Coding the Matrix" == Normalize_neologd("Coding the Matrix")
    # assert "南アルプスの天然水Sparking Lemonレモン一絞り" == \
    #     Normalize_neologd("南アルプスの　天然水　Ｓｐａｒｋｉｎｇ　Ｌｅｍｏｎ　レモン一絞り")
    # assert "南アルプスの天然水- Sparking*Lemon+レモン一絞り" == \
    #     Normalize_neologd("南アルプスの　天然水-　Ｓｐａｒｋｉｎｇ*　Ｌｅｍｏｎ+　レモン一絞り")


    """変更しないように以下をコメント文にしている"""
    # ### 文書の名前リストを返す
    # filenamelist, filelist = plsa_tf.Get_file_contents("/home/matsui-pc/matsui/lyrics_normalize")
    #
    # ### 解析対象テキストに処理を施す
    # for i in range(len(filenamelist)):
    #   Code((filenamelist[i]))


    # ary = []
    # ary.append("３点１１０円？？")
    # print ary[0].encode("utf_8")
    # print "\n"
    # # f_w = open("/home/matsui-pc/matsui/sample.txt", "w")
    # # f_w.write(ary[0])
    # # f_w.close()

    # f_r = open("/home/matsui-pc/matsui/sample.txt", "r")
    # data = f_r.read()

    # ary.append(Code(data))
    # f_r.close()

    # f_r = open("/home/matsui-pc/matsui/sample1.txt", "r")
    # data = f_r.read()
    # print data

    # print ary[0].encode("utf_8")
    # print ary[1]