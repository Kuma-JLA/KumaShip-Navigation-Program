# Ship-Navigation
東高科学部が制作中のドローン船用プログラム。

## 各ファイルの役割
base.py          ...測位から計算、各モーターの制御まで行うPythonプログラム。これを実行する。内部は1秒ごと無限ループされる。
micropyGPS.py    ...GPSモジュールを利用するためのパッケージ。
target.csv       ...ターゲット座標と許容誤差値がCSV形式で格納されています。
number.txt       ...base.pyがtarget.csvから取り出すターゲット座標の行番号を指定します。

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

    sudo apt-get install -y network-manager network-manager-gnome
    sudo apt-get remove -y dhcpcd5
    sudo  nano /etc/network/interfaces
    #全行コメントアウト
    reboot
    sudo nano /etc/NetworkManager/system-connections/rokemoba
    
/etc/NetworkManager/system-connections/rokemoba に各内容は以下の通り

        [connection]
        id=rokemoba
        type=gsm
        autoconnect=true

        [ppp]
        refuse-eap=true
        refuse-mschap=true
        refuse-mschapv2=true

        [ipv6]
        method=auto
        
        [ipv4]
        method=auto
        
        [serial]
        baud=460800
        
        [gsm]
        number=*99***1#
        username=roke@moba
        password=rokemoba
        apn=4gn.jp
    
## 起動毎に必要なコマンド
Piが起動するたび、以下の操作が必要。自動化するのがおススメ。

    sudo pigpiod
    sudo 格納フォルダ/base.py
