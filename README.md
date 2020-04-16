# Navigation-Program
東高科学部が制作中のドローン船用プログラム。<br>
利用する機材は以下のページを参照。<br>
https://elchika.com/article/4e090ab9-2014-4ae3-a375-c264532f4a75/<br>

## 各ファイルの役割
base.py<br>
測位から計算、各モーターの制御まで行うPythonプログラム。これを実行する。内部は1秒ごと無限ループされる。<br><br>
micropyGPS.py<br>
GPSモジュールを利用するためのパッケージ。<br><br>
target.csv<br>
ターゲット座標と許容誤差値がCSV形式で格納されています。<br><br>
number.txt<br>
base.pyがtarget.csvから取り出すターゲット座標の行番号を指定します。<br><br>
start.sh<br>
wvdial,pigpio,base.pyを起動します。「自動起動の設定」に従って起動時に実行されるようにしてください。<br>
必要に応じて内容を変更してください。<br><br>

## 準備

### 利用にあたり、以下のPythonモジュールのインストールが必要。<br>
smbus/pigpio/pings/adafruit_ina260<br>
→以下のコマンドを打ち込んでください。<br>

    sudo apt install pigpio
    sudo apt-get install python3-smbus
    sudo apt-get -y install python3-pip
    sudo pip3 install pigpio
    sudo pip3 install pings
    sudo pip3 install adafruit-circuitpython-ina260
    
    
### base.pyの内容に編集が必要。<br>
下記4行について、clone先フォルダを絶対パスで指定すること。

    sudo nano (clone先フォルダ)/KumaShip-Navigation-Program/base.py
    
    #77行目
    with open('(clone先フォルダ)/KumaShip-Navigation-Program/number.txt',encoding='utf-8') as f:
    #85行目
    with open('(clone先フォルダ)/KumaShip-Navigation-Program/target.csv') as f:
    #240行目
    with open('(clone先フォルダ)/KumaShip-Navigation-Program/number.txt', mode="w", encoding='utf-8') as f:
    #248行目
    with open('(clone先フォルダ)/KumaShip-Navigation-Program/number.txt', mode="w", encoding='utf-8') as f:
    
    
### start.shの内容に編集が必要。<br>
下記について、clone先フォルダを絶対パスで指定すること。

    sudo nano (clone先フォルダ)/KumaShip-Navigation-Program/start.sh
    
    #8行目
    sudo python3 (clone先フォルダ)/KumaShip-Navigation-Program/base.py
    
    
### adafruit_ina260モジュールの内容に編集が必要。<br>

    sudo nano /usr/local/lib/python3.7/dist-packages/adafruit_ina260.py
    
    #INA260モジュールのI2Cアドレスを指定する。
    def __init__(self, i2c_bus, address=0x40):   
    ↓
    def __init__(self, i2c_bus, address=0x6d):  
    
### モバイル回線のセットアップ
利用にあたり、L-03F＋ロケットモバイルによるモバイル回線を利用している。
開発するうえではWi-FiやEthernetでも問題ない。システムを完全に再現するには以下の通り。
(参考記事: https://qiita.com/jiisenonba/items/5f4ecbb58d80f4a69cdc )

    sudo apt-get install wvdial
    sudo modprobe usbserial vendor=0x1004 product=0x6366
    sudo  nano /etc/network/interfaces
    #内容は下を参照のこと
    sudo nano /etc/wvdial.conf
    #内容は下を参照のこと
    sudo nano /etc/udev/rules.d/99-ltemodem.rules
    #内容は下を参照のこと
    
    
/etc/network/interfaces に記述する内容は以下の通り

    iface rokemoba inet wvdial
    
/etc/wvdial.conf に記述する内容は以下の通り<br>
あらかじめ記述されている内容はすべて削除する。
    
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
    
/etc/udev/rules.d/99-ltemodem.rules に記述する内容は以下の通り

    ATTRS{idVendor}=="1004", ATTRS{idProduct}=="6366", RUN+="/sbin/modprobe usbserial vendor=0x1004 product=0x6366"
    KERNEL=="ttyUSB*", ATTRS{../idVendor}=="1004", ATTRS{../idProduct}=="6366", ATTRS{bNumEndpoints}=="03", ATTRS{bInterfaceNumber}=="01", SYMLINK+="modem"

    
## 自動起動の設定
Piが起動するたびにstart.shを実行するよう設定する。

    sudo nano /etc/rc.local
    
"exit 0"の前に以下の通り追記。clone先フォルダは絶対パスで指定する。

    sudo bash (clone先フォルダ)/KumaShip-Navigation-Program/start.sh
