# 사용 라이브러리
from firebase_admin import credentials
from firebase_admin import db
from pygame.examples.sound import mixer
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import time
import os
import firebase_admin

time.localtime(time.time())

cred = credentials.Certificate('C:/Users/gyu/Downloads/test-11-11-firebase-adminsdk-6fvmc-56dedea152.json')
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://test-11-11.firebaseio.com/'
})



# cap = cv2.VideoCapture('videos/04.mp4')  # 비디오를 입력받는다
cap = cv2.VideoCapture(0)
facenet = cv2.dnn.readNet('models/deploy.prototxt',
                          'models/res10_300x300_ssd_iter_140000.caffemodel')  # 얼굴영역을 탐지하는 모델을 facenet변수에 저장
model = load_model('models/mask_detector.model')  # 마스크를 인식하는 모델을 model변수에 저장
SOUND_PATH = os.getcwd() + "\\sounds\\bee.wav"
mixer.init()
sound = mixer.Sound(SOUND_PATH)
oldX = 0
count = 0
color = (0,0,255)

db_in = 0
db_out = 0

trigger = 0

mask_count = 0

number = 0

first = 0

count = 1


while True:
    ret, img = cap.read()  # 동영상에서 한프레임을 받아온다
    img = cv2.flip(img, 2)
    if ret == False:
        break

    h, w, c = img.shape  # 높이 넓이 채널을 저장

    blob = cv2.dnn.blobFromImage(img, size=(300, 300), mean=(104., 177., 123.))

    # 얼굴 영역 탐지 모델로 추론하기
    facenet.setInput(blob)  # 추론한결과를 setinput으로 지정한다
    dets = facenet.forward()  # dets 에 추론한결과를 저장한다
    #print(dets.shape)
    #print(dets.shape[2])

    for i in range(dets.shape[2]):
        confidence = dets[0, 0, i, 2]

        if confidence < 0.4:  # 정확도가 0.8보다 낮으면 얼굴이 아닌걸로 추론하기
            continue

        x1 = int(dets[0, 0, i, 3] * w)
        y1 = int(dets[0, 0, i, 4] * h)  # x1, y1, x2,y2로 얼굴영역 찾기
        x2 = int(dets[0, 0, i, 5] * w)
        y2 = int(dets[0, 0, i, 6] * h)

        centerX = x1 + int((x2 - x1) / 2)

        if first > 265 and first < 340:
            first = centerX
            continue

        if trigger == 1:
            print("감사합니다.")
            time.sleep(1)
            trigger = 0
            first = 0
            continue

        centerY = y1 + int((y2 - y1) / 2)

        face = img[y1:y2, x1:x2]  # 찾은 영역을 face에 저장한다
        try:
            face_input = cv2.resize(face, dsize=(224, 224))
        except Exception as e:
            print(str(e))
        face_input = cv2.cvtColor(face_input, cv2.COLOR_BGR2RGB)
        face_input = preprocess_input(face_input)
        face_input = np.expand_dims(face_input, axis=0)

        if first == 0:
            first = centerX
            oldX = centerX

        distensX = oldX - centerX
        oldX = centerX
        color = (0, 255, 255)

        mmdd = time.strftime('%m-%d', time.localtime(time.time()))

        yymmdd = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        hms = time.strftime('%H-%M-%S', time.localtime(time.time()))

        dir = db.reference(mmdd + '/case' + str(count))

        if centerX > 265 and centerX < 340 and centerY > 194 and centerY < 285:
            color = (255, 255, 255)
            mask, nomask = model.predict(face_input).squeeze()  # model.predict에 face를 넣어서 추론하고  mask, nomask 변수에 저장 한다
            if abs(mask_count) < 15:
                if mask > nomask:
                    mask_count += 1
                else:
                    mask_count -= 1
                color = (0,255,0)
                print(mask_count)
            elif mask_count > 0:
                print("마스크 착용 감사합니다.")
                db_in += 1
                mask_count = 0
                trigger = 1
                dir = db.reference(mmdd + '/' + str(count) + '-person')
                dir.update({'Day': yymmdd})
                dir.update({'Time': hms})
                dir.update({'Mask': 'O'})
                dir.update({'Temp': '36.7'})
                count += 1

            elif mask_count < 0:
                print("마스크를 착용해주세요.")

                sound.play()
                db_out += 1
                mask_count = 0
                trigger = 1
                dir = db.reference(mmdd + '/' + str(count) + '-person')
                dir.update({'Day': yymmdd})
                dir.update({'Time': hms})
                dir.update({'Mask': 'X'})
                dir.update({'Temp': '36.7'})
                count += 1

        else:
            mask_count = 0

        #if abs(distensX) < 1:
        #    count += 1
        #    if count < 10000000:
        #        print("확인")
        #else:
        #    count = 0


        #if mask > nomask:
        #    color = (0, 255, 0)  # 마스크를 쓴 확률이 마스크를 쓰지않는 확률보다 놓으면 초록색으로 표시
        #else:
        #    color = (0, 0, 255)  # 마스크를 쓰지않은 확률이 마스크를 쓴 확률보다 놓으면 빨간색으로 표시
        #    sound.play()
        cv2.circle(img, (centerX, centerY), 7, color,5)
        # 사각형 그리기
        #cv2.rectangle(img, pt1=(x1, y1), pt2=(x2, y2), thickness=2,
        #             color=color)  # 얼굴영역을 찾은후에 thickness로 선두께를 정하고 color는 위에 설정한 색을 가져온다
    cv2.rectangle(img,(265, 194), (339, 285), color)
    text = "db_in"
    cv2.putText(img, 'Mask : {}'.format(db_in), (0, 220), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255))
    cv2.putText(img, 'No Mask : {}'.format(db_out), (0, 250), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255))


    cv2.imshow('result', img)  # result창에 동영상 재생한다

    if cv2.waitKey(1) == ord('q'):  # q를 눌러 종료한다
        break
