import csv
import pprint
import serial
import micropyGPS
import threading
import time
from math import *
import smbus
import sys 
import pigpio
import pings
import board
import adafruit_ina260


#電圧電流センサセット
i2cine = board.I2C()
ina260 = adafruit_ina260.INA260(i2cine)


#ECSリセット
pi0 =pigpio.pi()
pi0.set_servo_pulsewidth(19, 1500)
time.sleep(5)
pi0.stop()



#GPS測位
gps = micropyGPS.MicropyGPS(9, 'dd') # MicroGPSオブジェクトを生成する。
                                     # 引数はタイムゾーンの時差と出力フォーマット

def rungps(): # GPSモジュールを読み、GPSオブジェクトを更新する
    s = serial.Serial('/dev/serial0', 9600, timeout=10)
    s.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる
    while True:
        sentence = s.readline().decode('utf-8') # GPSデーターを読み、文字列に変換する
        if sentence[0] != '$': # 先頭が'$'でなければ捨てる
            continue
        for x in sentence: # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
            gps.update(x)

gpsthread = threading.Thread(target=rungps, args=()) # 上の関数を実行するスレッドを生成
gpsthread.daemon = True
gpsthread.start() # スレッドを起動

while True:
    if gps.clean_sentences > 20: # ちゃんとしたデーターがある程度たまったら出力する
        h = (gps.timestamp[0] if gps.timestamp[0] < 24 else gps.timestamp[0] - 24)
        nowtime=('%2d:%02d:%04.1f' % (h, gps.timestamp[1], gps.timestamp[2]))
        nowlat=('%2.8f' % (gps.latitude[0]))
        nowlon=('%2.8f' % (gps.longitude[0]))
        nowalt=('%f' % gps.altitude)



#CMPS12取得
        i2ccmps = smbus.SMBus(1)
        address = 0x60
        rawheadHighByte = i2ccmps.read_byte_data(address,0x02)
        rawheadLowByte = i2ccmps.read_byte_data(address,0x03)
        rawhead = (rawheadHighByte <<8) + rawheadLowByte
        head = rawhead/10



#電圧電流取得
        V = ina260.voltage
        A = ina260.current/1000
        W = V*A
        Wa = ina260.power/1000
        



#ナンバー読み取り
        with open('/home/pi/Ship/number.txt',encoding='utf-8') as f:
            number=f.readline() # 改行も含めて１行読込
            number=number.rstrip() # 右側の改行文字を削除




#目標座標読み取り
        with open('/home/pi/Ship/target.csv') as f:
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
        if (13 > V):
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
            




            
#舵制御
        pi1 =pigpio.pi()
        pi1.set_servo_pulsewidth(18, servo) 
        pi1.stop()
        
#スラスタ制御
        pi2 =pigpio.pi()
        pi2.set_servo_pulsewidth(19, ecs) 
        pi2.stop()
        

        print()
        print()
        print('time:',nowtime)
        print('number:',number)
        print('tarlat:',targetlat)
        print('tarlon:',targetlon)
        print('nowlat:',nowlat)
        print('nowlon:',nowlon)
        print('nowalt:',nowalt)
        print('nowhead:',head)
        print('方位角(始点→終点)：%s' % round(result['azimuth1'],1))
#        print('方位角(終点→始点)：%s' % result['azimuth2'])
        print('距離：%s(m)' % round(result['distance']))
        print(servo)
        print(ecs)
        print(pingres)
        print('%.2f' % (V), "V")
        print('%.2f' % (A), "A")
        print('%.2f' % (W), "W")

    time.sleep(1)