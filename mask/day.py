import time
from random import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

count = 1
mi = ''

cred = credentials.Certificate('C:/Users/gyu/Downloads/test-11-11-firebase-adminsdk-6fvmc-56dedea152.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://test-11-11.firebaseio.com/'
})


while count != 7:
    mmdd = time.strftime('%m-%d', time.localtime(time.time()))

    yymmdd = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    hms = time.strftime('%H-%M-%S', time.localtime(time.time()))

    if count == 2:
        mi = '미'
    elif count == 4:
        mi = ''
    dir = db.reference(mmdd + '/case' + str(count))
    dir.update({'날짜': yymmdd})
    dir.update({'시간': hms})
    dir.update({'마스크': mi+'착용'})
    dir.update({'온도': '36.7'})

    count += 1

    time.sleep(2)
