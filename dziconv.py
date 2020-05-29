#!/usr/local/bin/python3

# coding: utf-8

# ==========================================================
# dziconv
# 入力画像群から Deep Zoom 形式画像ファイル(DZI) を生成する
# ==========================================================
# 2020-05-25 Ver.0.1 Initial Version.
# ==========================================================

# * 20200525 メモ suzuki
# 画像処理モジュールとして Pillow のインストールが必要
# >pip install Pillow （管理者モードで実行）
# pathlib を使うので python 3.4 以上が必要

# 入力: csvファイル（画像の配置情報）
# 1行目:
# 識別子,DZI画像幅,DZI画像高さ,背景色R,背景色G,背景色B
# 2行目以降:
# 画像位置X,画像位置Y,画像幅,画像高,ファイルパス

# 出力: DZI 画像ファイル(単一画像形式)
# 識別子 -+- dzc_output.xml (画像情報ファイル)
#         +- dzc_output_files (ピラミッド画像ディレクトリ) -+- 0 --- 0_0.jpg
#                                                           +- ...
#                                                           +- n -+- 0_0.jpg
#                                                                 ...
#                                                                 +- i_j.jpg
#                                                                 ...

# モジュールの輸入
import os
import sys
import math
from PIL import Image
import pathlib

# 定数
tile_size = 512 # 出力タイル画像の１辺
overlap_size = 1 # オーバーラップサイズ
jpg_quality = 100 # 出力JPGの品質
cache_size_MB = 512 # 入力画像のキャッシュサイズ（MB単位）

# 入出力データファイルの情報
input_dir = ''
input_file = 'index.csv'
output_dir = ''

# 入力画像
output_identifier = ''
dzi_size = (0, 0) # W, H
background_color = (0, 0, 0) # R, G, B
class input_data_record:
    def __init__(self, x = 0, y = 0, w = 0, h = 0, f = ''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.f = f
    #fed
#ssalc
input_data = []

# ファイルの読み込み
def read_index_csv(fn):
    global output_identifier, dzi_size, background_color 
    with open(fn, 'r', encoding='utf-8') as f:
        l = f.readline()
        if (len(l) > 0):
            t = l.strip().split(',')
            if (len(t) >= 6):
                output_identifier = t[0]
                dzi_size = (int(t[1]), int(t[2]))
                background_color = (int(t[3]), int(t[4]), int(t[5]))
            else:
                print('illegal input data: line 1.')
                exit()
            #fi
        #fi
        i = 1
        for l in f:
            t = l.strip().split(',')
            if (len(t) >= 5):
                input_data.append(input_data_record(int(t[0]),int(t[1]),int(t[2]),int(t[3]),t[4]))
            else:
                print('illegal input data: line %d.' % i)
            #fi
            i = i + 1
        #rof
    #htiw
#fed

# レベル情報の定義
class level_info_record:
    def __init__(self, w = 0, h = 0, m = 0, n = 0):
        self.w = w
        self.h = h
        self.m = m
        self.n = n
    #fed
#ssalc
level_info = []
level_max = 0 # 最大レベル

# レベル情報の計算
def make_level_info():
    global level_max
    w = dzi_size[0]
    h = dzi_size[1]
    while True:
        m = math.ceil(w / tile_size)
        n = math.ceil(h / tile_size)
        level_info.insert(0, level_info_record(w, h, m, n))
        if ((w == 1) and (h == 1)): break
        w = int(((w + 1) / 2) if ((w % 2) == 1) else (w / 2))
        h = int(((h + 1) / 2) if ((h % 2) == 1) else (h / 2))
    #elihw
    level_max = len(level_info) - 1
#fed

# 出力ディレクトリの作成
def make_output_dirs():
    p = os.path.join(output_dir, output_identifier)
    if (not os.path.exists(p)): os.mkdir(p)
    pp = os.path.join(p, 'dzc_output_files')
    if (not os.path.exists(pp)): os.mkdir(pp)
    for i in range(0, len(level_info)): 
        ppp = os.path.join(pp, str(i))
        if (not os.path.exists(ppp)): os.mkdir(ppp)
    #rof
#fed

# 画像情報ファイルの出力
def write_output_xml():
    with open(os.path.join(output_dir, output_identifier, 'dzc_output.xml'), 'w', encoding='utf_8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<Image TileSize="%d" Overlap="%d" Format="jpg" ServerFormat="Default" xmlns="http://schemas.microsoft.com/deepzoom/2009">\n' % (tile_size, overlap_size))
        f.write('<Size Width="%d" Height="%d"/>\n' % dzi_size)
        f.write('</Image>\n')
    #htiw
#fed

# 入力画像がどのタイルに属するか調べる
tile_images = None
level_max_m = 0
level_max_n = 0
def check_tile_images():
    global tile_images, level_max_m, level_max_n
    level_max_m = level_info[level_max].m
    level_max_n = level_info[level_max].n
    # print(level_max, level_max_m, level_max_n)
    tile_images = [[[] for j in range(level_max_n)] for i in range(level_max_m)] # ２次元配列
    for k in range(len(input_data)):
        r = input_data[k]
        imin = math.floor(r.x / tile_size)
        jmin = math.floor(r.y / tile_size)
        imax = math.floor((r.x + r.w - 1) / tile_size)
        jmax = math.floor((r.y + r.h - 1) / tile_size)
        for i in range(imin, imax+1):
            for j in range(jmin, jmax+1):
                # print(i,j,imin,imax,jmin,jmax)
                tile_images[i][j].append(r)
            #rof
        #rof
    #rof
#fed

# point 型
class point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    #fed
    def xy(self): # (x, y) を返す (Image 関数用)
        return (self.x, self.y)
    #fed
#ssalc
# rect 型
class rect:
    def __init__(self, x = 0, y = 0, w = 0, h = 0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    #fed
    def area(self): # (x1, y1, x2 + 1, y2 + 1) を返す (Image 関数用)
        return (self.x, self.y, self.x + self.w, self.y + self.h)
    #fed
    def xy(self): # (x, y) を返す (Image 関数用)
        return (self.x, self.y)
    #fed
#ssalc

# レベルｌの画像におけるタイル(i,j)の画像エリアを求める
# f=Falseのときは画像エリア番号の指定に従って画像エリアを返す
# f=Trueのときはオーバーラップを含めた画像全体を返す
# 画像エリア番号(p, q) (p,q∈{-1,0,+1}）は以下の領域を指す．
#  (-1, -1)|( 0,-1)| (+1,-1)
# ---------+-------+---------
#  (-1,  0)|( 0, 0)| (+1, 0)
# ---------+-------+---------
#  (-1, +1)|( 0,+1)| (+1,+1)
# (0,0)は画像の正味の部分 それ以外はオーバーラップ部分
# 有効なエリア (rect_w, rect_h > 0) を返せたら (rect_x, rect_y, rect_w, rect_h) を，さもなくば None を返す．
def get_level_l_tileimage_rect(l, i, j, p, q, f = False):
    level_l_m = level_info[l].m
    level_l_n = level_info[l].n
    level_l_w = level_info[l].w
    level_l_h = level_info[l].h
    rect_x = -1
    rect_y = -1
    rect_w = 0
    rect_h = 0
    if ((0 <= i) and (i < level_l_m) and (0 <= j) and (j < level_l_n)):
        overlap_l = 0 if (i == 0) else overlap_size
        overlap_r = 0 if (i == level_l_m - 1) else overlap_size
        overlap_u = 0 if (j == 0) else overlap_size
        overlap_d = 0 if (j == level_l_n - 1) else overlap_size
        w = (level_l_w - tile_size * i) if (i == level_l_m - 1) else tile_size
        h = (level_l_h - tile_size * j) if (j == level_l_n - 1) else tile_size
        if (f):
            rect_x = 0
            rect_y = 0
            rect_w = overlap_l + w + overlap_r
            rect_h = overlap_u + h + overlap_d
        elif ((-1 <= p) and (p <= 1) and (-1 <= q) and (q <= 1)):
            if (p == -1):
                rect_x = 0
                rect_w = overlap_l
            elif (p == 0):
                rect_x = overlap_l
                rect_w = w
            elif (p == 1):
                rect_x = overlap_l + w
                rect_w = overlap_r
            #fi
            if (q == -1):
                rect_y = 0
                rect_h = overlap_u
            elif (q == 0):
                rect_y = overlap_u
                rect_h = h
            elif (q == 1):
                rect_y = overlap_u + h
                rect_h = overlap_d
            #fi
        else:
            print('get_level_l_tileimage_rect(%d, %d, %d, <%d, %d>, %s) -> ' % (l, i, j, p, q, str(f)))
            exit()
        #fi
    #fi
    #print('get_level_l_tileimage_rect(%d, %d, %d, %d, %d, %s) -> ' % (l, i, j, p, q, str(f))),
    #print(rect_x, rect_y, rect_w, rect_h)
    return rect(rect_x, rect_y, rect_w, rect_h) if (rect_w > 0 and rect_h > 0) else None
#fed

# レベルlの画像におけるタイル(i,j)のオーバラップコピー用の画像エリアを返す
# 画像エリア番号(p, q) (p,q∈{-1,0,+1}）は以下の領域を指す．
# ただし(0, 0) は無意味
#  (-1, -1)|       | (+1,-1)
# ---------+-------+---------
#          |       | 
# ---------+-------+---------
#  (-1, +1)|       | (+1,+1)
#
#           ( 0,-1)
# ---------+-------+---------
#  
# ---------+-------+---------
#           ( 0,+1)
#
#          |       | 
#          +       +
#  (-1,  0)|       | (+1, 0)
#          +       +
#          |       | 
#
# 有効なエリア (rect_w, rect_h > 0) を返せたら (rect_x, rect_y, rect_w, rect_h) を，さもなくば None を返す．
def get_level_l_overlapimage_rect(l, i, j, p, q):
    level_l_m = level_info[l].m
    level_l_n = level_info[l].n
    level_l_w = level_info[l].w
    level_l_h = level_info[l].h
    rect_w = 0
    rect_h = 0
    if ((-1 <= p) and (p <= 1) and (-1 <= q) and (q <= 1) and not ((p == 0) and (q == 0))):
        if ((0 <= i + p) and (i + p < level_l_m) and (0 <= j + q) and (j + q < level_l_n)):
            overlap_l = 0 if (i == 0) else overlap_size
            overlap_u = 0 if (j == 0) else overlap_size
            w = (level_l_w - tile_size * i) if (i == level_l_m) else tile_size
            h = (level_l_h - tile_size * j) if (i == level_l_n) else tile_size
            if (p == -1):
                rect_x = overlap_l
                rect_w = overlap_size
            elif (p == 0):
                rect_x = overlap_l
                rect_w = w
            elif (p == 1):
                rect_x = overlap_l + w - overlap_size
                rect_w = overlap_size
            #fi
            if (q == -1):
                rect_y = overlap_u
                rect_h = overlap_size
            elif (q == 0):
                rect_y = overlap_u
                rect_h = h
            elif (q == 1):
                rect_y = overlap_u + h - overlap_size
                rect_h = overlap_size
            #fi
        #fi
    #fi
    return rect(rect_x, rect_y, rect_w, rect_h) if ((rect_w > 0) and (rect_h > 0)) else None
#fed

# 入力画像のキャッシュ（キュー構造）
class image_cache_record:
    def __init__(self, f, p = None):
        self.f = f
        self.p = p
        self.memsize = p.width * p.height * 3 if (p is not None) else 0
    #fed
#ssalc
class image_cache: #
    def __init__(self, m = cache_size_MB * 1024 * 1024):
        self.memmax = m
        self.memsize = 0
        self.c = []
    #fed
    def read_image(self, f):
        j = -1
        for i in range(0, len(self.c)):
            if (self.c[i].f == f): 
                j = i
                break
            #fi
        #rof
        if ((0 <= j) and (j < len(self.c))): # 見つかった
            return self.c[j].p # 画像を返す
        else: # 見つからない
            ff = os.path.join(input_dir, f)
            if (os.path.isfile(ff)):
                r = image_cache_record(f, Image.open(ff)) # 画像を読み込む
            else:
                print('%s: file not found' % f)
                exit()
            #fi
            # キャッシュ画像が多すぎたら減らす：末尾を削除
            while ((len(self.c) > 0) and (self.memsize + r.memsize > self.memmax)):
                self.memsize -= self.c[-1].memsize
                del self.c[-1]
            #elihw
            self.c.insert(0, r) # 画像をキャッシュの先頭に追加
            self.memsize += r.memsize
            return r.p
        #fi
    #fed
#ssalc
icache = None

# 入力画像からの最大レベル(level_max)画像の読み込み
# 画像pに書き込む
# 画像pの画像サイズは一辺Blocksize + OverlapSize * 2の正方形
# 読み込んだ画像はpの画像エリア番号(0,0)の範囲に書き込まれる
def read_level_max_image(i, j, p):
    # pの書き込み範囲を求める
    prect = get_level_l_tileimage_rect(level_max, i, j, 0, 0)
    if (prect is not None):
        # タイル画像の範囲 [tx1, tx2) x [ty1, ty2)
        tx1 = i * tile_size
        ty1 = j * tile_size
        tx2 = tx1 + prect.w
        ty2 = ty1 + prect.h
        l = tile_images[i][j]
        n = len(l)
        for k in range(0, n):
            # 読み込み画像の範囲  [ix1, ix2) x [iy1, iy2)
            ix1 = l[k].x
            iy1 = l[k].y
            ix2 = ix1 + l[k].w
            iy2 = iy1 + l[k].h
            # ブロック画像と読み込み画像の共通範囲  [ox1, ox2) x [oy1, oy2)
            ox1 = max(tx1, ix1)
            ox2 = min(tx2, ix2)
            oy1 = max(ty1, iy1)
            oy2 = min(ty2, iy2)
            # 共通範囲の幅と高さ
            ow = ox2 - ox1
            oh = oy2 - oy1
            # タイル画像上のローカル座標
            oltx1 = ox1 - tx1;
            olty1 = oy1 - ty1;
            # 読み込み画像のローカル座標
            olix1 = ox1 - ix1;
            oliy1 = oy1 - iy1;
            # 画像を読み込んで張り付ける
            #print('(%d,%d) %d: tile(%d,%d)-(%d,%d)[%dx%d], in(%d,%d)-(%d,%d)[%dx%d], out(%d,%d)-(%d,%d)[%dx%d], local_tile(%d,%d), local_in(%d, %d)' % (i, j, k, tx1, ty1, tx2, ty2, prect.w, prect.h, ix1, iy1, ix2, iy2, l[k].w, l[k].h, ox1, oy1, ox2, oy2, ow, oh, oltx1, olty1, olix1, oliy1))
            # in_img = icache.read_image(l[k].f)
            # in_img_crop = in_img.crop((olix1, oliy1, olix1 + ow, oliy1 + oh))
            # if (i == 10 and j == 0 and k == 0): in_img_crop.save(os.path.join(os.getcwd(),'x.jpg'))
            # print('in_img[%dx%d], in_img_crop[%dx%d]' % (in_img.size[0],in_img.size[1],in_img_crop.size[0],in_img_crop.size[1]))
            # p.paste(in_img_crop, (prect.x + oltx1, prect.y + olty1))
            p.paste(icache.read_image(l[k].f).crop((olix1, oliy1, olix1 + ow, oliy1 + oh)), (prect.x + oltx1, prect.y + olty1))
        #rof
    else:
        print('read_image: prect is None')
        exit()
    #fi
#fed

# レベルlの画像の読み込み(0<=l<=LavelMax-1)
# レベルl+1の画像を４つ読み込んで合成して縮小する
# 画像pに書き込む
# 画像pの画像サイズは一辺Blocksize + OverlapSize * 2の正方形
# 読み込んだ画像はpの(OverlapSize, Overlapsize) - (OverlapSize + BlockSize - 1, OverlapSize + BlockSize - 1)
# の範囲に書き込まれる
def read_level_l_image(l, i, j, p):
    if ((0 <= l) and (l <= level_max - 1)):
        # レベルl+1の縦横ブロック数
        m = level_info[l + 1].m
        n = level_info[l + 1].n
        # レベルi+1の先頭読み込みブロック
        ii = i * 2
        jj = j * 2
        # 4枚の画像を読み込む
        # 縦横ブロック数が足りない場合もある
        in_dir = os.path.join(output_dir, output_identifier, 'dzc_output_files', str(l + 1))
        q00 = Image.open(os.path.join(in_dir, ('%d_%d.jpg' % (ii,     jj    ))))
        q01 = Image.open(os.path.join(in_dir, ('%d_%d.jpg' % (ii,     jj + 1)))) if (jj + 1 < n) else None
        q10 = Image.open(os.path.join(in_dir, ('%d_%d.jpg' % (ii + 1, jj    )))) if (ii + 1 < m) else None
        q11 = Image.open(os.path.join(in_dir, ('%d_%d.jpg' % (ii + 1, jj + 1)))) if ((ii + 1 < m) and (jj + 1 < n)) else None
        # オーバーラップ分を除いた画像の真のサイズ
        q00r = get_level_l_tileimage_rect(l + 1, ii, jj, 0, 0)
        ppw = q00r.w
        pph = q00r.h
        pp00p = point(0, 0)
        if (q01 is not None):
            q01r = get_level_l_tileimage_rect(l + 1, ii, jj + 1, 0, 0)
            pp01p = point(0, q00r.h)
            pph += q01r.h
        #fi
        if (q10 is not None):
            q10r = get_level_l_tileimage_rect(l + 1, ii + 1, jj, 0, 0)
            pp10p = point(q00r.w, 0)
            ppw += q10r.w
        #fi
        if (q11 is not None):
            q11r = get_level_l_tileimage_rect(l + 1, ii + 1, jj + 1, 0, 0)
            pp11p = point(q00r.w, q00r.h)
        #fi
        # 画像を貼り合わせる画像メモリppを用意する
        # 縦横ブロック数が足りない場合もある
        # ppw, pphの補正：奇数なら１加える
        if ((ppw % 2) == 1): ppw += 1 #fi
        if ((pph % 2) == 1): pph += 1 #fi
        # print('read_level_l_image(%d, %d, %d, p)' % (l, i, j))
        # print(q00r.x, q00r.y, q00r.w, q00r.h)
        # print(ppw, pph)
        pp = Image.new('RGB', (ppw, pph), background_color)
        pp.paste(q00.crop(q00r.area()), pp00p.xy())
        if (q01 is not None): pp.paste(q01.crop(q01r.area()), pp01p.xy()) #fi
        if (q10 is not None): pp.paste(q10.crop(q10r.area()), pp10p.xy()) #fi
        if (q11 is not None): pp.paste(q11.crop(q11r.area()), pp11p.xy()) #fi
        # 大きさを1/2にしてpに張り付ける
        pw = int(ppw / 2)
        ph = int(pph / 2)
        pr = get_level_l_tileimage_rect(l, i, j, 0, 0)
        p.paste(pp.resize((pw, ph), Image.BICUBIC), pr.xy())
    else:
        print('read_level_l_image: illegal level %d' % l)
        exit()
    #fi
#fed

class image_buf_record:
    def __init__(self):
        self.reset()
    #fed
    def reset(self):
        self.set_unused()
        self.img = Image.new('RGB', ((tile_size + overlap_size * 2), (tile_size + overlap_size * 2)), background_color)
    #fed
    def set_index(self, i, j):
        self.i = i
        self.j = j
    #fed
    def set_unused(self):
        self.i = -1
        self.j = -1
    #fed
    def is_unused(self):
        return ((self.i < 0) or (self.j < 0))
    #fed
    def write_to_file(self, l, out_dir):
        if (not self.is_unused()):
            dr = get_level_l_tileimage_rect(l, self.i, self.j, 0, 0, True)
            self.img.crop(dr.area()).save(os.path.join(out_dir, ('%d_%d.jpg' % (self.i, self.j))))
            self.reset()
        #fi
    #fed
#ssalc

def make_level_images():
    check_tile_images()
    for l in range(level_max, -1, -1):
        out_dir = os.path.join(output_dir, output_identifier, 'dzc_output_files', str(l))
        level_l_m = level_info[l].m
        level_l_n = level_info[l].n
        level_l_w = level_info[l].w
        level_l_h = level_info[l].h
        print('Level%d: %dx%d: %dx%d' % (l, level_l_w, level_l_h, level_l_m, level_l_n))
        image_buf = [ image_buf_record() for i in range(2 * level_l_n + 3) ]
        ibindex = lambda i: ((i + 2 * level_l_n + 3) % (2 * level_l_n + 3))
        si = 0 # (p, q) = (0, 0) とするバッファのインデックス
        for i in range(0, level_l_m):
            print((' %d' % i), end='')
            sys.stdout.flush()
            for j in range(0, level_l_n):
                image_buf[si].set_index(i, j)
                if (l == level_max):
                    read_level_max_image(i, j, image_buf[si].img)
                else:
                    read_level_l_image(l, i, j, image_buf[si].img)
                #fi
                # オーバーラップイメージの書き込み
                # (p,q) = (-1,-1)
                sr = get_level_l_overlapimage_rect(l, i, j, -1, -1)
                dr = get_level_l_tileimage_rect(l, i - 1, j - 1, 1, 1)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si - (level_l_n + 1))
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = (-1, 0)
                sr = get_level_l_overlapimage_rect(l, i, j, -1, 0)
                dr = get_level_l_tileimage_rect(l, i - 1, j, 1, 0)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si - level_l_n)
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = (-1, +1)
                sr = get_level_l_overlapimage_rect(l, i, j, -1, 1)
                dr = get_level_l_tileimage_rect(l, i - 1, j + 1, 1, -1)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si - (level_l_n - 1))
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = ( 0,-1)
                sr = get_level_l_overlapimage_rect(l, i, j, 0, -1)
                dr = get_level_l_tileimage_rect(l, i, j - 1, 0, 1)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si - 1)
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = ( 0,+1)
                sr = get_level_l_overlapimage_rect(l, i, j, 0, 1)
                dr = get_level_l_tileimage_rect(l, i, j + 1, 0, -1)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si + 1)
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = (+1,-1)
                sr = get_level_l_overlapimage_rect(l, i, j, 1, -1)
                dr = get_level_l_tileimage_rect(l, i + 1, j - 1, -1, 1)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si + (level_l_n - 1))
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = (+1, 0)
                sr = get_level_l_overlapimage_rect(l, i, j, 1, 0)
                dr = get_level_l_tileimage_rect(l, i + 1, j, -1, 0)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si + level_l_n)
                    #print(l, i, j, 1, 0, si, di, len(image_buf)),
                    #print(sr.area()),
                    #print(dr.area())
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # (p,q) = (+1,+1)
                sr = get_level_l_overlapimage_rect(l, i, j, 1, 1)
                dr = get_level_l_tileimage_rect(l, i + 1, j + 1, -1, -1)
                if ((sr is not None) and (dr is not None)):
                    di = ibindex(si + (level_l_n + 1))
                    image_buf[di].img.paste(image_buf[si].img.crop(sr.area()), dr.xy())
                #fi
                # オーバラップ領域までの処理が終わったバッファをファイルに書き出す
                di = ibindex(si - (level_l_n + 1))
                ii = image_buf[di].i;
                jj = image_buf[di].j;
                if (((ii == i - 1) and (jj == j - 1)) or ((ii == i - 2) and (jj == level_l_n - 1))):
                    image_buf[di].write_to_file(l, out_dir)
                #fi
                si = ibindex(si + 1)
            #rof
        #rof
        # バッファに残っている画像をすべて書き出す．
        for i in range(si - (level_l_n + 1), si): image_buf[ibindex(i)].write_to_file(l, out_dir) #rof
        print('')
    #rof
#fed

# --- 主処理 ---

print('***** Deep Zoom Image File Converter *****')
if (len(sys.argv) < 3):
    print('Usage: dziconv InputFile(index.csv) OutputPath [tile_size=%d [OverlapSize=%d [JPEGQuality=%d [CacheSize(MB)=%d]]]].' % (tile_size, overlap_size, jpg_quality, cache_size_MB))
    exit()
#fi
# 第１引数の処理
p = pathlib.Path(sys.argv[1])
if (not p.is_absolute()): p = p.resolve() #fi
input_dir, input_file = os.path.split(str(p))
# 第２引数の処理
p = pathlib.Path(sys.argv[2])
if (not p.is_absolute()): p = p.resolve() #fi
output_dir = str(p)
# 第３引数の処理
if (len(sys.argv) >= 4): tile_size = int(sys.argv[3]) #fi
# 第４引数の処理
if (len(sys.argv) >= 5): overlap_size = int(sys.argv[4]) #fi
# 第５引数の処理
if (len(sys.argv) >= 6): jpg_quality = int(sys.argv[5]) #fi
# 第６引数の処理
if (len(sys.argv) >= 7): cache_size_MB = int(sys.argv[6]) #fi
# パラメタ情報の表示
print('===== Parameters =====')
print('Input File Path:%s' % input_dir)
print('Input File Name:%s' % input_file)
print('Output File Path:%s' % output_dir)
print('tile_size:%d' % tile_size)
print('OverlapSize:%d' % overlap_size)
print('JPEGQuality:%d' % jpg_quality)
print('CacheSize(MB):%d' % cache_size_MB)
print('======================');
# 画像情報ファイルを読み込む
read_index_csv(os.path.join(input_dir, input_file))
# ファイル情報の表示
print('===== Input File Infomation =====')
print('Output File ID:%s' % output_identifier)
print('Image Size:%dx%d' % dzi_size)
print('Background Color: (%d,%d,%d)' % background_color)
print('#data:%d' % len(input_data))
print('================================')
# レベル情報の作成
make_level_info()
print('===== DeepZoom Levels =====')
for i in range(0, len(level_info)):
    l =level_info[i]
    print('%3d:%6dx%6d, (%4dx%4d)' % (i, l.w, l.h, l.m, l.n))
#rof
print('===========================')
# 変換処理開始
print('===== Conversion in progress =====');
icache = image_cache(cache_size_MB * 1024 * 1024)
make_output_dirs()
write_output_xml()
make_level_images()
print('============ Finished ============')

# おわり
