# Ship-Navigation
東高科学部が制作中のドローン船用プログラム。

利用にあたり、以下のPythonモジュールのインストールが必要。<br>
smbus/pigpio/pings/adafruit_ina260<br>
→以下のコマンドを打ち込んでください。<br>
sudo apt-get install python3-smbus<br>
sudo apt install pigpio<br>
sudo pip3 install pings<br>
sudo pip3 install adafruit-circuitpython-ina260<br>
<br>
Piが起動するたび、以下の操作が必要。<br>
sudo pigpiod<br>
