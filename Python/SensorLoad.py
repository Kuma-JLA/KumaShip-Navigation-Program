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
        
        
#測定値CSV書き出し
        with open('/dev/shm/sensordata.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow([(str(date) + ' ' + str(nowtime)), nowlat, nowlon, nowalt, head, gpshead, speedkm, speedkn, V, A, W])
