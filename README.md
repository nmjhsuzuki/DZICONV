# [DZICONV](https://github.com/nmjhsuzuki/DZICONV)

# 特徴 (Features)

　[DZICONV](https://github.com/nmjhsuzuki/DZICONV)は，入力画像群からDeep Zoom 形式画像(DZI)ファイルに変換します．Python3 で書かれています．

　[DZICONV](https://github.com/nmjhsuzuki/DZICONV) is a Deep Zoom Image (DZI) file converter. It is written in Python3.

# デモンストレーション (Demonstration)

　Newcastle という名前の Deep Zoom 画像を作成してみます．12枚のスナップ写真を並べたものです．サンプルデータが input\Newcastle フォルダ下に入っています．index.csv は以下の内容になっています．  
　1行目は，IDに続いて，生成するDZI画像のサイズ（幅，高さ），背景色(R,G,B)を与えます．（この例では（背景色が正しく指定できることを示すため）背景はグレイ(128,128,128)にしてありますが，ふつうは黒(0,0,0)でしょう．）  
　2行目以降に，入力画像を出力画像に貼り付ける位置(X,Y)と各画像のサイズ(W,H)，画像へのパス（相対パスの場合はindex.csvのあるフォルダからの相対パス）を与えます．ここでは12個の画像を横４列縦３行に並べています．  
　※Unix/Linux系OSでは，パス区切り文字を / に置換してください．

```CSV
Newcastle,21600,10800,128,128,128
108,72,5184,3456,.\images\IMG_7090.JPG
5508,72,5184,3456,.\images\IMG_7224.JPG
10908,72,5184,3456,.\images\IMG_7267.JPG
16308,72,5184,3456,.\images\IMG_7270.JPG
108,3672,5184,3456,.\images\IMG_7276.JPG
5508,3672,5184,3456,.\images\IMG_7283.JPG
10908,3672,5184,3456,.\images\IMG_7284.JPG
16308,3672,5184,3456,.\images\IMG_7294.JPG
108,7272,5184,3456,.\images\IMG_7301.JPG
5508,7272,5184,3456,.\images\IMG_7302.JPG
10908,7272,5184,3456,.\images\IMG_7314.JPG
16308,7272,5184,3456,.\images\IMG_7605.JPG
```

たとえば，Windows 10 PC 上で，git clone して DZI 画像を作ってみましょう．（省略しますが Unix/Linux系OS 上でも（パス区切り文字を除いて）コマンドは同じです．ただし index.csv 内のパス区切り文字の変更をお忘れなく．）

```Batchfile
D:\>git clone https://github.com/nmjhsuzuki/DZICONV.git
...
D:\>python dziconv.py .\input\Newcastle\index.csv .\output
***** Deep Zoom Format Image Converter *****
===== Parameters =====
Input File Path:D:\DZICONV\input\Newcastle
Input File Name:index.csv
Output File Path:D:\DZICONV\output
tile_size:512
OverlapSize:1
JPEGQuality:100
CacheSize(MB):512
======================
===== Input File Infomation =====
Output File ID:Newcastle
Image Size:21600x10800
Background Color: (128,128,128)
#data:12
================================
===== DeepZoom Levels =====
  0:     1x     1, (   1x   1)
  1:     2x     1, (   1x   1)
  2:     3x     2, (   1x   1)
  3:     6x     3, (   1x   1)
  4:    11x     6, (   1x   1)
  5:    22x    11, (   1x   1)
  6:    43x    22, (   1x   1)
  7:    85x    43, (   1x   1)
  8:   169x    85, (   1x   1)
  9:   338x   169, (   1x   1)
 10:   675x   338, (   2x   1)
 11:  1350x   675, (   3x   2)
 12:  2700x  1350, (   6x   3)
 13:  5400x  2700, (  11x   6)
 14: 10800x  5400, (  22x  11)
 15: 21600x 10800, (  43x  22)
===========================
===== Conversion in progress =====
Level15: 21600x10800: 43x22
 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42
Level14: 10800x5400: 22x11
 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21
Level13: 5400x2700: 11x6
 0 1 2 3 4 5 6 7 8 9 10
Level12: 2700x1350: 6x3
 0 1 2 3 4 5
Level11: 1350x675: 3x2
 0 1 2
Level10: 675x338: 2x1
 0 1
Level9: 338x169: 1x1
 0
Level8: 169x85: 1x1
 0
Level7: 85x43: 1x1
 0
Level6: 43x22: 1x1
 0
Level5: 22x11: 1x1
 0
Level4: 11x6: 1x1
 0
Level3: 6x3: 1x1
 0
Level2: 3x2: 1x1
 0
Level1: 2x1: 1x1
 0
Level0: 1x1: 1x1
 0
============ Finished ============
```

　output\Newcastle 以下に DZI 形式画像が出来ています．dzc_output.xml には画像の情報が入っています．

```xml
<?xml version="1.0" encoding="utf-8"?>
<Image TileSize="512" Overlap="1" Format="jpg" ServerFormat="Default" xmlns="http://schemas.microsoft.com/deepzoom/2009">
<Size Width="21600" Height="10800"/>
</Image>
```

　dzc_output_files\ フォルダ以下には，階層化されたタイル画像群が格納されています．

　[DZI-IIIF](https://github.com/nmjhsuzuki/DZI-IIIF)が導入されていれば，Webブラウザで画像を呼び出して表示できます．やり方は DZI-IIIF の readme.MD をご覧ください．

# 背景 (Background)

　[IIIF (International Image Interoperability Framework)](https://iiif.io) は，画像へのアクセスを標準化し相互運用性を確保するための国際的なコミュニティ活動です([Wikipedia](https://ja.wikipedia.org/wiki/International_Image_Interoperability_Framework)より)．  
　[Deep Zoom](https://en.wikipedia.org/wiki/Deep_Zoom) は，Microsoft が開発した，任意の大きさの画像を取り扱える画像技術の一つです．現在では，[Openseadragon](https://openseadragon.github.io) を用いて，PC・タブレット・スマートフォン等の Web ブラウザ上に画像を表示することができます．  
　私が勤める[国立歴史民俗博物館（歴博）](https://www.rekihaku.ac.jp) では，屏風や絵巻などの一辺が数万～数十万画素に及ぶ画像を，どこでも任意の倍率で表示する超大画像ビューワを2000年に開発し，常設展示・企画展示等で来館者の利用に供してきました．2016年ごろから Opensedragon を用いたビューワへ移行し，画像の保持形式として Deep Zoom 形式を用いています．独自開発ブラウザにおける超高精細画像フォーマット(NMJH形式)の資料画像が資産として多数存在していますので，ここから Deep Zoom image (DZI) 形式へ変換する画像コンバータを C# で開発し，使用していました．  
　今回，[DZI-IIIF](https://github.com/nmjhsuzuki/DZI-IIIF)の公開に合わせて，汎用的に使えるコンバータとして，Python に移植しました．これによりOSを超えた可搬性を持たせることができました．  
　Python による Deep Zoom 画像生成スプリクトは，[openzoom/deepzoom.py](https://github.com/openzoom/deepzoom.py) などすでに存在しますが，本スクリプトは，複数枚の画像を組み合わせて，１辺が数万～数十万画素に達するような超大画像を制作したいときなどに便利です．（よく用いられるPyramid TIFFではひとつのファイルのサイズとして大きくなりすぎると考えられるため．）

# 必要な環境 (Requirement)

　Python3 が必要です．Pillow も必要なので pip install Pillow しておいてください．また，pathlib モジュールを使っており，Python 3.4 以上が必要です．  

　Windows10 Professional 64bit（バージョン1909）上で，以下の環境でテストしています．

* Python 3.8.3 (64bit版)
* Pillow 7.1.2

　さくらのレンタルサーバースタンダード(FreeBSD 9.1-RELEASE-p24 amd64)上で，以下の環境でテストしています．

* Python 3.5.9
* Pillow 7.1.2

# インストール(Installation)

　[デモンストレーション](#デモンストレーション-demonstration)をご覧ください．

# その他 (Note)

　最初のバージョンを 2020年6月1日に公開しました．  

# 作者情報 (Author)

* 鈴木卓治 (SUZUKI, Takuzi)
* 国立歴史民俗博物館 (National Museum of Japanese History, Chiba, JAPAN)
* Email: suzuki@rekihaku.ac.jp
* Twitter: @digirekiten （デジタルで楽しむ歴史資料 https://twitter.com/digirekiten ）

# ライセンス (License)

　"DZICONV"は[MIT license](https://en.wikipedia.org/wiki/MIT_License)に従います．

　"DZICONV" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).

