# Ship-Navigation
東高科学部が制作中のドローン船用プログラム。

利用にあたり、以下のPythonモジュールのインストールが必要。
smbus/pigpio/pings/adafruit_ina260
→以下のコマンドを打ち込んでください。
sudo apt-get install python3-smbus
sudo apt install pigpio
sudo pip3 install pings
sudo pip3 install adafruit-circuitpython-ina260

Piが起動するたび、以下の操作が必要。
sudo pigpiod
