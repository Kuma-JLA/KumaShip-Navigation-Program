# -*- coding: utf-8 -*-

import csv
import urllib.request
import urllib.parse

posturl ='http://**********/realtimelink.php'   #データ送信先

#センサーデータ読み取り
with open('/dev/shm/sensordata.csv') as f:
  reader = csv.reader(f)
  l = [row for row in reader]
  time = (l[0][0])
  nowlat = (l[0][1])
  nowlon = (l[0][2])
  nowalt = (l[0][3])
  head = (l[0][4])
  gpshead = (l[0][5])
  speedkm = (l[0][6])
  speedkn = (l[0][7])
  V = (l[0][8])
  A = (l[0][9])
  W = (l[0][10])
  
#ナビゲーションデータ読み取り
with open('/dev/shm/navigation.csv') as f:
  reader = csv.reader(f)
  l = [row for row in reader]
  ecs = (l[0][0])
  servo = (l[0][1])
  tarazm = (l[0][2])
  tardis = (l[0][3])
  
#ナンバー読み取り
  with open('/dev/shm/number.txt',encoding='utf-8') as f:
    number=f.readline() # 改行も含めて１行読込
    number=number.rstrip() # 右側の改行文字を削除

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
    'ecs':ecs,
    'servo':servo,
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
