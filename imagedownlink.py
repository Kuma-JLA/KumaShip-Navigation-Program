import cv2
from ftplib import FTP

#OpenCV
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # カメラ画像の横幅を1280に設定
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # カメラ画像の縦幅を720に設定
_, frame = camera.read()
cv2.imwrite("/dev/shm/newimage.jpg", frame)

#FTP
Host_address = "********"
User_id = "********"
Password = "********"
Port = 21
ftp = FTP(Host_address, User_id, Password, Port)

ftp.delete("./images/latestimage.jpg")
ftp.rename("./images/newimage.jpg","./images/latestimage.jpg")

f = open("/dev/shm/newimage.jpg", 'rb')
ftp.storbinary("STOR ./images/newimage.jpg", f)

