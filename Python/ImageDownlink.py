import datetime
import cv2

#時刻取得
nowtime = datetime.datetime.now()
nowtime_string = nowtime.strftime('%Y-%m-%d %H:%M:%S')

#写真撮影
mjpgstreamer = "localhost/?action=stream"
camera = cv2.VideoCapture(URL)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # カメラ画像の横幅を1280に設定
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # カメラ画像の縦幅を720に設定
_, frame = camera.read()
camera.release()

#日時合成
cv2.putText(frame,nowtime_string,(25,50),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(232, 167, 145), 10)
cv2.putText(frame,nowtime_string,(25,50),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(70, 158, 162), 2)
cv2.imwrite("/dev/shm/oi_newimage.jpg", frame)
