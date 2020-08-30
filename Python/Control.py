# -*- coding: utf-8 -*-

import csv
import sys 
import pigpio

#ECSリセット
pi0 =pigpio.pi()
pi0.set_servo_pulsewidth(19, 1500)
time.sleep(5)
pi0.stop()

while True:

#ナビゲーションデータ読み取り
  with open('/dev/shm/navigation.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
    ecs = (l[0][0])
    servo = (l[0][1])

#舵制御
      pi1 =pigpio.pi()
      pi1.set_servo_pulsewidth(18, servo) 
      pi1.stop()
        
#スラスタ制御
      pi2 =pigpio.pi()
      pi2.set_servo_pulsewidth(19, ecs) 
      pi2.stop()
        
  time.sleep(1)
