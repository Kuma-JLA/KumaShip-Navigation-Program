#!/bin/bash
#安定まで20秒待機します
sleep 20
sudo ifup rokemoba
sudo pigpiod
#GPS測位までさらに10秒待機します
sleep 10
sudo python3 (clone先フォルダ)/KumaShip-Navigation-Program/base.py
