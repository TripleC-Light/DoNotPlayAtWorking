# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import os
import time
import threading
import tornado.websocket
import json
import myFunction as myFunc
from ObjCtrl import ObjCtrl
from Script import Script

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html', msg='')

    def post(self):
        userID = self.get_argument('userID')
        passWord = self.get_argument('password')
        dbCtrl = myFunc.DatabaseCtrl()
        user = dbCtrl.loginCheck(userID, passWord)
        if user:
            userKey = user['key']
            self.render('index.html', userKey=userKey)
        else:
            self.render('login.html', msg='loginFail')

class SignUpHandler(tornado.web.RequestHandler):
    def get(self):
        allPilot = myFunc.getAllPilot()
        self.render('signup.html', msg='', allPilot=allPilot)

    def post(self):
        webLink = 'signup.html'
        allPilot = myFunc.getAllPilot()
        signupData = {}
        signupData['userID'] = self.get_argument('userID')
        signupData['password'] = self.get_argument('password')
        signupData['name'] = self.get_argument('name')
        signupData['pilot'] = self.get_argument('checkPilot')

        if len(signupData['userID']) > 20:
            msg = 'userIDtooLong'

        elif len(signupData['name']) > 10:
            msg = 'nametooLong'

        elif myFunc.haveIllegalChar(signupData['name']):
            msg = 'illegalName'

        else:
            dbCtrl = myFunc.DatabaseCtrl()
            if dbCtrl.checkIDexist(signupData['userID']):
                msg = 'IDexist'
            else:
                dbCtrl.addData(signupData)
                msg = 'signupOK'
                webLink = 'login.html'

        self.render(webLink, msg=msg, allPilot=allPilot)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):     # 允許跨來源資源共用
        return True

    def allow_draft76(self):            # for iOS 5.0 Safari
        return True

    def open(self):
        print("new client opened")

    def on_close(self):
        print("Client leave")

    def on_message(self, CMDfromWEB):
        global gFrameTime
        global gObjList
        global gPilotListInJSON
        global gMapSize
        global gMsgCtrl
        global gObjCtrl
        global gMapCtrl

        tmp = CMDfromWEB.split('@')
        CMD = tmp[0]
        returnInfo = ''
        if CMD == 'createPilot':
            pilot = gObjCtrl.createCharacter('pilot')
            if pilot:
                gObjList[pilot.id] = pilot
                gMsgCtrl.add('系統公告', '玩家 ' + pilot.name + '進入遊戲')
                pilotInJSON = pilot.__dict__
                returnInfo = 'newPilot@' + json.dumps(pilotInJSON)

        elif CMD == 'pilotLoging':
            userKey = tmp[1]
            dbCtrl = myFunc.DatabaseCtrl()
            nowUser = dbCtrl.getUser(userKey)
            pilot = gObjCtrl.createCharacter('pilot')
            if pilot:
                pilot.id = nowUser['id']
                pilot.name = nowUser['name']
                pilot.pic = nowUser['pilot']
                gObjList[pilot.id] = pilot
                gMsgCtrl.add('系統公告', '玩家 ' + pilot.name + '進入遊戲')
                pilotInJSON = pilot.__dict__
                returnInfo = 'newPilot@' + json.dumps(pilotInJSON)

        elif CMD == 'reBorn':
            id_ = tmp[1]
            gObjList[id_].HP = gObjList[id_].HPmax

        elif CMD == 'getNewData':
            id_ = tmp[1]
            if id_ in gObjList:
                gObjList[id_].timeOut = round(time.time(), 3)
            gPilotListInJSON['serverTime'] = time.time()
            returnInfo = 'NewData@' + json.dumps(gPilotListInJSON)

        elif CMD == 'move':
            data = tmp[1].split(';')
            id_ = data[0]
            XY = data[1]
            XY = XY.split(',')
            gObjList[id_].tX = int(XY[0])
            gObjList[id_].tY = int(XY[1])

        elif CMD == 'attack':
            id_ = tmp[1]
            gObjList[id_].attack = time.time()

        elif CMD == 'createEnemy':
            for _ in range(5):
                enemy = gObjCtrl.createCharacter('zombie')
                gObjList[enemy.id] = enemy

        elif CMD == 'createItem':
            gObjCtrl.mapSize = gMapSize
            for _ in range(3):
                item_ = gObjCtrl.createItem('fullHP')
                gObjList[item_.id] = item_

        elif CMD == 'sendMsg':
            data = tmp[1].split(';')
            id_ = data[0]
            msg = data[1]
            msg = gMsgCtrl.filter(msg)
            gObjList[id_].msgTimeCount = time.time()
            gObjList[id_].msg = msg
            gMsgCtrl.add(gObjList[id_].name, msg)

        elif CMD == 'getMsg':
            returnInfo = gMsgCtrl.returnToWeb()

        elif CMD == 'updateMap':
            returnInfo = gMapCtrl.returnToWeb()

        elif CMD == 'setMap':
            reserveList = {}
            for mapObj in gObjList:
                if gObjList[mapObj].type != 'mapObj':
                    reserveList[mapObj] = gObjList[mapObj]
            gObjList = reserveList.copy()

            mapRegion = tmp[1]
            # mapRegion = data
            # mapObjInJSON = {}
            # mapObjList = []
            gMapCtrl.mapRegion = mapRegion
            mapObjInJSON =
            # filename = './static/map/setting/' + mapRegion + '.map'
            # with open(filename, 'r', encoding='utf-8') as fRead:
            #     for line in fRead:
            #         line = line.strip()
            #         line = line.split(':')
            #         type_ = line[0]
            #         if type_ == 'region':
            #             mapObjInJSON['region'] = line[1]
            #         elif type_ == 'size':
            #             description = line[1].split(',')
            #             gMapSize = [int(description[0]), int(description[1])]
            #             mapObjInJSON['size'] = gMapSize
            #         elif type_ == 'background':
            #             mapObjInJSON['background'] = './static/map/background/' + line[1]
            #         elif type_ == 'mapObj':
            #             description = line[1].split(',')
            #             _obj = gObjCtrl.createMapItem(description)
            #             gObjList[_obj.id] = _obj
            #             mapObjList.append(_obj.__dict__)

            mapObjInJSON['ObjList'] = mapObjList
            objToJSON = json.dumps(mapObjInJSON)
            returnInfo = 'setMap@' + objToJSON

        self.write_message(returnInfo)

def loopAll():
    global gMapSize
    global gFrameTime
    global gPilotListInJSON
    global gMsgCtrl
    global gObjList
    global gObjCtrl
    global gScript

    timeCtrl = myFunc.TimeCtrl()
    gObjCtrl.attackTime = 0.1   # second
    gObjCtrl.offlineTime = 5    # second
    gObjCtrl.frameTime = gFrameTime

    while 1:
        timeCtrl.sysTime = time.time()
        FPS = timeCtrl.showFPS()
        gObjCtrl.mapSize = gMapSize
        gObjCtrl.sysTime = timeCtrl.sysTime
        gObjCtrl.objList = gObjList
        gObjCtrl.clearBeHIT()
        gScript.msgCtrl = gMsgCtrl
        pilotList = []
        for id_ in list(gObjList.keys()):
            deleteState = False
            pilot = gObjList[id_]
            if pilot.type != 'mapObj':
                gObjCtrl.updatePosition(pilot)
                gObjCtrl.clearAttack(pilot)

                if pilot.attack != 0:
                    gObjCtrl.createWeapen(pilot)
                    gObjCtrl.attackJudge(pilot)

                if gObjCtrl.timeOut(pilot):
                    if pilot.type != 'item':
                        gMsgCtrl.add('系統公告', str(pilot.name) + ' 離開遊戲')
                    deleteState = True
                    print('delete: ' + str(id_))

                if gObjCtrl.HPtoZero(pilot):
                    if pilot.type == 'enemy':
                        print('Game Over: ' + str(pilot.id))
                        deleteState = True
                    elif pilot.type == 'item' and pilot.pic == 'button':
                        print('Button be push')
                        deleteState = True
                    else:
                        gMsgCtrl.add('系統公告', str(pilot.name) + ' HP歸零')

                if deleteState:
                    del gObjList[id_]

        if timeCtrl.oneSecondTimeOut():
            for id_ in list(gObjList.keys()):
                pilot = gObjList[id_]
                gObjCtrl.msgTimeOutCheck(pilot)
                gObjCtrl.enemyAutoCtrl(pilot)
                gObjCtrl.enemyTimeReflash(pilot)
                gObjCtrl.itemTimeReflash(pilot)

            gScript.region = '0-0'
            gScript.mapSize = gMapSize
            gScript.objCtrl = gObjCtrl
            gScript.mapCtrl = gMapCtrl
            gScript.run(gObjList)

        for id_ in list(gObjList.keys()):
            pilot = gObjList[id_]
            if pilot.type != 'mapObj':
                pilotList.append(pilot.__dict__)

        gPilotListInJSON['list'] = pilotList
        gPilotListInJSON['FPS'] = FPS
        time.sleep(gFrameTime)

if __name__ == "__main__":
    global gObjList
    global gPilotListInJSON
    global gFrameTime           # Frame per second
    global gMsgCtrl
    global gMapSize
    global gObjCtrl
    global gScript
    global gMapCtrl

    try:
        gObjList = {}
        gFrameTime = 0.05
        gPilotListInJSON = {}
        gMsgCtrl = myFunc.MsgCtrl()
        gMapSize = []
        gObjCtrl = ObjCtrl()
        gScript = Script()
        gMapCtrl = myFunc.MapCtrl()

        # 建立執行緒並執行
        t = threading.Thread(target=loopAll)
        t.start()

        handlers = [[r'/signup', SignUpHandler],
                    [r'/index', IndexHandler],
                    [r'/ws', WebSocketHandler],
                    [r'/favicon.ico', tornado.web.StaticFileHandler, {'path': './static/favicon.ico'}]]

        webApp = tornado.web.Application(
            handlers,
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True
        )
        webApp.listen(8888)
        url = 'http://localhost:8888/index'
        # webbrowser.open(url=url, new=0)
        print('Server open in: ' + url)
        tornado.ioloop.IOLoop.instance().start()

    except KeyboardInterrupt:
        print('再見！')
