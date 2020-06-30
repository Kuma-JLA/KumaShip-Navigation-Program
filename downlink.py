# coding: UTF-8

import csv
import urllib.request
import urllib.parse

posturl ='http://********/downlink.php'   #データ送信先

with open('/dev/shm/data.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
    time = (l[0][0])
    nowlat = (l[0][1])
    nowlon = (l[0][2])
    nowalt = (l[0][3])
    head = (l[0][4])
    gpshead = (l[0][5])
    tarazm = (l[0][6])
    tardis = (l[0][7])
    speedkm = (l[0][8])
    speedkn = (l[0][9])
    number = (l[0][10])
    V = (l[0][11])
    A = (l[0][12])
    W = (l[0][13])

#beacon送信判定
#beacon=beacon+1
#if (beacon == 60):
#beacon = 0
# 送信パラメーター
data = {
    'time':time,
    'lat':nowlat,
    'lon':nowlon,
    'alt':nowalt,
    'head':head,
    'gpshead':gpshead,
    'tarazm':tarazm,
    'tardis':tardis,
    'speedkm':speedkm,
    'speedkn':speedkn,
    'number':number,
    'V':V,
    'A':A,
    'W':W
    }
# 送信パラメーターのurlエンコード実行
# Python2のときはurllib.urlencode
postdata = urllib.parse.urlencode(data)
# 送信データはbyte配列に変換
postbyte = postdata.encode('utf-8')
# postリクエストを実行
# Python2のときは urllib.urlopen
response = urllib.request.urlopen(posturl, postbyte)
# read()で応答を取得
# 取得できるのはbyte配列なので、decodeで文字列に変換
#body = response.read().decode('utf-8')
#print(body)
