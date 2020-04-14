# Navigation-Program
東高科学部が制作中のドローン船用プログラム。

## 各ファイルの役割
base.py<br>
測位から計算、各モーターの制御まで行うPythonプログラム。これを実行する。内部は1秒ごと無限ループされる。<br><br>
micropyGPS.py<br>
GPSモジュールを利用するためのパッケージ。<br><br>
target.csv<br>
ターゲット座標と許容誤差値がCSV形式で格納されています。<br><br>
number.txt<br>
base.pyがtarget.csvから取り出すターゲット座標の行番号を指定します。

## 準備

### 利用にあたり、以下のPythonモジュールのインストールが必要。<br>
smbus/pigpio/pings/adafruit_ina260<br>
→以下のコマンドを打ち込んでください。<br>

    sudo apt-get install python3-smbus
    sudo apt install pigpio
    sudo pip3 install pings
    sudo pip3 install adafruit-circuitpython-ina260
    
### モバイル回線のセットアップ
利用にあたり、L-03F＋ロケットモバイルによるモバイル回線を利用している。
開発するうえではWi-FiやEthernetでも問題ない。システムを完全に再現するには以下の通り。

    sudo apt-get install wvdial
    sudo modprobe usbserial vendor=0x1004 product=0x6366
    sudo  nano /etc/network/interfaces
    sudo nano /etc/wvdial.conf
    
/etc/wvdial.conf に記述する内容は以下の通り
    
    [Dialer Defaults]
    Phone = *99***1#
    APN = 4gn.jp
    Username = roke@moba
    Password = rokemoba
    New PPPD = yes
    Stupid Mode = yes
    Init1 = ATZ
    Init2 = AT+CGDCONT=1,"IP","4gn.jp"
    Init3 = ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0
    Dial Attemps = 3
    Modem Type = Analog Modem
    Modem = /dev/ttyUSB1
    Dial Command = ATD
    Baud = 460800
    ISDN = 0
    Carrier Check = no
    Auto DNS = 1
    Check Def Route = 1

    
## 起動毎に必要なコマンド
Piが起動するたび、以下の操作が必要。自動化するのがおススメ。

    sudo pigpiod
    sudo 格納フォルダ/base.py
