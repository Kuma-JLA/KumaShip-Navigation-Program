import csv
import pprint
import threading
import time
from math import *
import sys 
import pings
import board

while True:

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

#ナンバー読み取り
        with open('/dev/shm/number.txt',encoding='utf-8') as f:
            number=f.readline() # 改行も含めて１行読込
            number=number.rstrip() # 右側の改行文字を削除

#目標座標読み取り
        with open('/dev/shm/target.csv') as f:
            reader = csv.reader(f)
            l = [row for row in reader]
            targetlat = (l[int(number)][0])
            targetlon = (l[int(number)][1])
            threshold = (l[int(number)][2])

#計算
        ELLIPSOID_GRS80 = 1 # GRS80
        ELLIPSOID_WGS84 = 2 # WGS84
        GEODETIC_DATUM = {
            ELLIPSOID_GRS80: [
                6378137.0,         # [GRS80]長軸半径
                1 / 298.257222101, # [GRS80]扁平率
            ],
            ELLIPSOID_WGS84: [
                6378137.0,         # [WGS84]長軸半径
                1 / 298.257223563, # [WGS84]扁平率
            ],
        }
        ITERATION_LIMIT = 1000
        '''
        Vincenty法(逆解法)
        2地点の座標(緯度経度)から、距離と方位角を計算する
        :param lat1: 始点の緯度
        :param lon1: 始点の経度
        :param lat2: 終点の緯度
        :param lon2: 終点の経度
        :param ellipsoid: 楕円体
        :return: 距離と方位角
        '''
        def vincenty_inverse(lat1, lon1, lat2, lon2, ellipsoid=None):
            if isclose(lat1, lat2) and isclose(lon1, lon2):
                return {
                    'distance': 0.0,
                    'azimuth1': 0.0,
                    'azimuth2': 0.0,
                }
            a, ƒ = GEODETIC_DATUM.get(ellipsoid, GEODETIC_DATUM.get(ELLIPSOID_GRS80))
            b = (1 - ƒ) * a
            φ1 = radians(lat1)
            φ2 = radians(lat2)
            λ1 = radians(lon1)
            λ2 = radians(lon2)
            U1 = atan((1 - ƒ) * tan(φ1))
            U2 = atan((1 - ƒ) * tan(φ2))
            sinU1 = sin(U1)
            sinU2 = sin(U2)
            cosU1 = cos(U1)
            cosU2 = cos(U2)
            L = λ2 - λ1
            λ = L
            for i in range(ITERATION_LIMIT):
                sinλ = sin(λ)
                cosλ = cos(λ)
                sinσ = sqrt((cosU2 * sinλ) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosλ) ** 2)
                cosσ = sinU1 * sinU2 + cosU1 * cosU2 * cosλ
                σ = atan2(sinσ, cosσ)
                sinα = cosU1 * cosU2 * sinλ / sinσ
                cos2α = 1 - sinα ** 2
                cos2σm = cosσ - 2 * sinU1 * sinU2 / cos2α
                C = ƒ / 16 * cos2α * (4 + ƒ * (4 - 3 * cos2α))
                λʹ = λ
                λ = L + (1 - C) * ƒ * sinα * (σ + C * sinσ * (cos2σm + C * cosσ * (-1 + 2 * cos2σm ** 2)))
                if abs(λ - λʹ) <= 1e-12:
                    break
            else:
                return None
            u2 = cos2α * (a ** 2 - b ** 2) / (b ** 2)
            A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
            B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
            Δσ = B * sinσ * (cos2σm + B / 4 * (cosσ * (-1 + 2 * cos2σm ** 2) - B / 6 * cos2σm * (-3 + 4 * sinσ ** 2) * (-3 + 4 * cos2σm ** 2)))
            s = b * A * (σ - Δσ)
            α1 = atan2(cosU2 * sinλ, cosU1 * sinU2 - sinU1 * cosU2 * cosλ)
            α2 = atan2(cosU1 * sinλ, -sinU1 * cosU2 + cosU1 * sinU2 * cosλ) + pi
            if α1 < 0:
                α1 = α1 + pi * 2
            return {
                'distance': s,           # 距離
                'azimuth1': degrees(α1), # 方位角(始点→終点)
                'azimuth2': degrees(α2), # 方位角(終点→始点)
            }
                            
        lat1 = float(nowlat)
        lon1 = float(nowlon)
        lat2 = float(targetlat)
        lon2 = float(targetlon)

        result = vincenty_inverse(lat1, lon1, lat2, lon2, 1)

#各種判定        
        #方位判定
        x = (round(result['azimuth1'],1) - head)
        
        #低電圧の場合
        if (12 > V):
            ecs = 1500
            servo = 1500
            pingres = 'none'
        
        #低電圧でない場合
        else:
            
            #距離500m以上
            if (500<round(result['distance'])):
                ecs = 1550
                pingres = 'none'
                if (-345 < x <= -180):
                    servo = 1000
                elif (15 < x < 180):
                    servo = 1000
                elif (-180 < x < -15):
                    servo = 2000
                elif (180 <= x < 345):
                    servo = 2000
                else:
                    servo = 1500
        
            #距離threshold~200m
            elif (200<round(result['distance'])<threshold):
                ecs = 1550
                pingres = 'none'
                if (-350 < x <= -180):
                    servo = 1000
                elif (10 < x < 180):
                    servo = 1000
                elif (-180 < x < -10):
                    servo = 2000
                elif (180 <= x < 350):
                    servo = 2000
                else:
                    servo = 1500
        
            #距離threshold以下(到着判定)
            else:
                ecs = 1500
                servo = 1500
            
            
                #ネットワーク判定
                p = pings.Ping() # Pingオブジェクト作成
                res = p.ping("www.yahoo.co.jp")  # yahoo.co.jpへPing

                #接続OK
                if res.is_reached():
                    pingres = 'OK'
                    #目標を1進める
                    writenumber = (int(number)+1)
                    with open('/home/pi/Ship/number.txt', mode="w", encoding='utf-8') as f:
                        f.write(str(writenumber))
            
                # 接続NG
                else:
                    pingres = 'NG'
                    #目標を1戻す
                    writenumber = (int(number)-1)
                    with open('/home/pi/Ship/number.txt', mode="w", encoding='utf-8') as f:
                        f.write(str(writenumber))

#測定値CSV書き出し
            with open('/dev/shm/navigation.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow([ecs, servo, round(result['azimuth1'],1), round(result['distance'])])
