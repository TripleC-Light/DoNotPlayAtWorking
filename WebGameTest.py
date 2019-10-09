# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import webbrowser
import os
import time
import random
import threading
import tornado.websocket
from Object import Object
import json
import myFunction as myFunc

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

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
        global gObjList
        global gPilotListInJSON
        global gMapSize
        global gMsgCtrl

        _setInitPositionFail = [-1, -1]
        _tmp = CMDfromWEB.split('@')
        _cmd = _tmp[0]
        _returnInfo = ''
        if _cmd == 'createPilot':
            _data = _tmp[1]
            _positionMode = _data
            _pilot = Object()
            _pilot.id = myFunc.getUniqueID()
            _pilot.name = str(_pilot.id)
            _XY = setInitPosition(_positionMode, gMapSize, _pilot)
            if _XY != _setInitPositionFail:
                _pilot.X = _XY[0]
                _pilot.Y = _XY[1]
                _pilot.tX = _XY[0]
                _pilot.tY = _XY[1]
                _pilot.timeOut = round(time.time(), 3)
                _pilot.W = random.randint(20, 150)
                _pilot.H = _pilot.W
                gObjList[_pilot.id] = _pilot
                gMsgCtrl.add('系統公告', '玩家 ' + _pilot.name + '進入遊戲')
                _pilotInJSON = _pilot.__dict__
                _returnInfo = 'newPilot@' + json.dumps(_pilotInJSON)

        elif _cmd == 'getNewData':
            _data = _tmp[1]
            _id = _data
            if _id in gObjList:
                gObjList[_id].timeOut = round(time.time(), 3)
            gPilotListInJSON['serverTime'] = time.time()
            _returnInfo = 'NewData@' + json.dumps(gPilotListInJSON)

        elif _cmd == 'move':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _XY = _tmp[1]
            _XY = _XY.split(',')
            gObjList[_id].tX = int(_XY[0])
            gObjList[_id].tY = int(_XY[1])

        elif _cmd == 'attack':
            _id = _tmp[1]
            gObjList[_id].attack = time.time()

        elif _cmd == 'createEnemy':
            _setInitPositionFail = [-1, -1]
            for _i in range(100):
                print('createEnemy' + str(_i))
                enemy = Object()
                enemy.id = myFunc.getUniqueID()
                enemy.name = enemy.id
                _XY = setInitPosition('auto', gMapSize, enemy)
                if _XY != _setInitPositionFail:
                    enemy.type = 'enemy'
                    enemy.pic = 'zombie'
                    enemy.SP = 30
                    enemy.X = _XY[0]
                    enemy.Y = _XY[1]
                    # enemy.tX = _XY[0]
                    # enemy.tY = _XY[1]
                    enemy.tX = random.randint(70, 1000)
                    enemy.tY = random.randint(70, 600)
                    enemy.timeOut = round(time.time(), 3)
                    enemy.W = random.randint(7, 7)
                    enemy.H = enemy.W
                    gObjList[enemy.id] = enemy

        elif _cmd == 'sendMsg':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _msg = _tmp[1]
            _msg = gMsgCtrl.filter(_msg)
            gObjList[_id].msgTimeCount = 5
            gObjList[_id].msg = _msg
            gMsgCtrl.add(gObjList[_id].name, _msg)

        elif _cmd == 'getMsg':
            _returnInfo = gMsgCtrl.returnToWeb()

        elif _cmd == 'setMap':
            _reserveList = {}
            for _mapObj in gObjList:
                if gObjList[_mapObj].type != 'mapObj':
                    _reserveList[_mapObj] = _mapObj
            gObjList = _reserveList.copy()

            _data = _tmp[1]
            _mapRegion = _data
            _mapObjInJSON = {}
            _mapObjList = []
            _mapObjID = 0
            filename = './static/map/setting/' + _mapRegion + '.map'
            with open(filename, 'r', encoding='utf-8') as fRead:
                for line in fRead:
                    line = line.strip()
                    line = line.split(':')
                    _type = line[0]

                    if _type == 'region':
                        _mapObjInJSON['region'] = line[1]
                    elif _type == 'size':
                        _description = line[1].split(',')
                        gMapSize = [int(_description[0]), int(_description[1])]
                        _mapObjInJSON['size'] = gMapSize
                    elif _type == 'background':
                        _mapObjInJSON['background'] = './static/map/background/' + line[1]
                    elif _type == 'mapObj':
                        _obj = Object()
                        _description = line[1].split(',')
                        _pic = _description[0]
                        _X = int(_description[1])
                        _Y = int(_description[2])
                        _obj.type = 'mapObj'
                        _obj.id = myFunc.getUniqueID()
                        _obj.name = str(_obj.id)
                        _obj.X = _X
                        _obj.Y = _Y
                        _obj.tX = _X
                        _obj.tY = _Y
                        if _pic == 'bud':
                            _obj.HP = 1000
                            _obj.W = 70
                            _obj.H = 70
                            _obj.pic = './static/map/obj/' + _pic + '.png'
                        gObjList[_obj.id] = _obj
                        _mapObjList.append(_obj.__dict__)
                        _mapObjID += 1
            _mapObjInJSON['ObjList'] = _mapObjList
            _objToJSON = json.dumps(_mapObjInJSON)
            _returnInfo = 'setMap@' + _objToJSON

        self.write_message(_returnInfo)

def setInitPosition(positionMode, mapSize, obj):
    _collisionState = (True, 0)
    _tryCount = 0
    _XY = []
    while _collisionState[0]:
        if positionMode == 'auto':
            _XY = [0, 0]
            _XY[0] = random.randint((obj.W/2), mapSize[0]-(obj.W/2))
            _XY[1] = random.randint((obj.H/2), mapSize[1]-(obj.H/2))
        else:
            _initPoint = positionMode.split(',')
            _XY = [int(_initPoint[0]), int(_initPoint[1])]

        obj.X = _XY[0]
        obj.Y = _XY[1]
        obj.tX = _XY[0]
        obj.tY = _XY[1]

        if positionMode == 'auto':
            _collisionState = myFunc.rectCollision(obj, gObjList)
            _tryCount += 1
            if _tryCount > 1000:
                _XY = [-100, -100]
                print('Already try 1000 times to find a position but the map has no position to put Pilot')
                return [-1, -1]
        else:
            _collisionState = (False, 0)
    print('Try select a new position in ' + str(_tryCount) + ' times')
    return _XY

def updateAll():
    global gTimeCounter
    global gFrameTime
    global gPilotListInJSON
    global gMsgCtrl
    global gObjList

    _msgUpdateTime = 1  # second
    _attackTime = 0.1   # second
    _offlineTime = 5    # second
    while 1:
        _startTime = time.time()
        gTimeCounter += 1
        if (gTimeCounter * gFrameTime) > _msgUpdateTime:
            gTimeCounter = 0
            for _pilot in list(gObjList.keys()):
                if gObjList[_pilot].type == 'pilot':
                    if gObjList[_pilot].msgTimeCount > 0:
                        gObjList[_pilot].msgTimeCount -= 1
                        if gObjList[_pilot].msgTimeCount == 0:
                            gObjList[_pilot].msg = ''

                if gObjList[_pilot].type == 'enemy':
                    _targetPilot = gObjList[_pilot]
                    while _targetPilot.type != 'pilot':
                        _targetPilot = gObjList[random.choice(list(gObjList.keys()))]
                    gObjList[_pilot].tX = _targetPilot.X
                    gObjList[_pilot].tY = _targetPilot.Y

        for _pilot in list(gObjList.keys()):
            if gObjList[_pilot].type == 'pilot' or gObjList[_pilot].type == 'enemy':
                gObjList[_pilot].HIT = False

        _pilotList = []
        for _pilot in list(gObjList.keys()):
            if gObjList[_pilot].type == 'pilot' or gObjList[_pilot].type == 'enemy':
                updatePosition(gObjList[_pilot])
                if (gObjList[_pilot].attack != 0) and ((time.time()-gObjList[_pilot].attack) > _attackTime):
                    gObjList[_pilot].attack = 0

                if gObjList[_pilot].attack != 0:
                    _weapen = Object()
                    _weapen.id = gObjList[_pilot].id
                    _weapen.W = gObjList[_pilot].W/2
                    _weapen.H = gObjList[_pilot].H
                    if gObjList[_pilot].dir == 'right':
                        _weapen.X = gObjList[_pilot].X + gObjList[_pilot].W/2 + _weapen.W/2
                        _weapen.Y = gObjList[_pilot].Y
                    else:
                        _weapen.X = gObjList[_pilot].X - gObjList[_pilot].W/2 - _weapen.W/2
                        _weapen.Y = gObjList[_pilot].Y
                    _weapenCollision = myFunc.rectCollision(_weapen, gObjList)
                    if _weapenCollision[0]:
                        gObjList[_pilot].attack = 0
                        for _beHitPilot in gObjList:
                            if gObjList[_beHitPilot].id == _weapenCollision[1]:
                                print('Be HIT: ' + str(_weapenCollision[1]))
                                gObjList[_beHitPilot].HIT = True
                                _damage = gObjList[_pilot].AT - gObjList[_beHitPilot].DEF
                                if _damage > 0:
                                    gObjList[_beHitPilot].HP -= _damage
                                    if gObjList[_beHitPilot].HP <= 0:
                                        gObjList[_beHitPilot].timeOut = 1
                                break

                if (time.time() - gObjList[_pilot].timeOut) > _offlineTime:
                    if gObjList[_pilot].type == 'pilot' or gObjList[_pilot].type == 'enemy':
                        if gObjList[_pilot].timeOut == 0:
                            gMsgCtrl.add('系統公告', str(gObjList[_pilot].name) + ' 離開遊戲')
                            del gObjList[_pilot]
                            print('delete: ' + str(_pilot))
                        else:
                            gObjList[_pilot].timeOut = 0

        for _pilot in list(gObjList.keys()):
            if gObjList[_pilot].type == 'pilot' or gObjList[_pilot].type == 'enemy':
                if gObjList[_pilot].type == 'enemy' and gObjList[_pilot].timeOut != 0:
                    gObjList[_pilot].timeOut = round(time.time(), 3)
                _pilotList.append(gObjList[_pilot].__dict__)

        gPilotListInJSON['list'] = _pilotList

        _exeTime = time.time()-_startTime
        # print(round((_exeTime*1000), 2))
        time.sleep(gFrameTime)

def updatePosition(pilot):
    global gFrameTime
    global gPilotStep
    global gObjList

    _P1 = [pilot.X, pilot.Y]
    _P2 = [pilot.tX, pilot.tY]
    _dX = _P1[0] - _P2[0]
    _dY = _P1[1] - _P2[1]
    if myFunc.distance(_P1, _P2) < 1:
        return True
    else:
        gPilotStep = pilot.SP * gFrameTime
        _step = gPilotStep
        _d = round(myFunc.distance(_P1, _P2))
        _howManyTimesToGo = round(_d / _step)
        if _howManyTimesToGo == 0:
            pilot.X = pilot.tX
            pilot.Y = pilot.tY
        else:
            if pilot.tX > pilot.X:
                pilot.dir = 'right'
            elif pilot.tX < pilot.X:
                pilot.dir = 'left'
            pilot.X = round(pilot.X - (_dX / _howManyTimesToGo))
            if myFunc.rectCollision(pilot, gObjList)[0]:
                pilot.X = round(pilot.X + (_dX / _howManyTimesToGo))
                pilot.tX = pilot.X
                pilot.tY = pilot.Y
            pilot.Y = round(pilot.Y - (_dY / _howManyTimesToGo))
            if myFunc.rectCollision(pilot, gObjList)[0]:
                pilot.Y = round(pilot.Y + (_dY / _howManyTimesToGo))
                pilot.tX = pilot.X
                pilot.tY = pilot.Y
        return False

if __name__ == "__main__":
    global gObjList
    global gPilotList
    global gPilotListInJSON
    global gTimeCounter
    global gFrameTime           # Frame per second
    global gPilotVilocity       # pixel / s
    global gPilotStep           # Pixel per frame
    global gMsgCtrl

    try:
        gObjList = {}
        gTimeCounter = 0
        gFrameTime = 0.05
        gPilotVilocity = 350
        gPilotStep = gPilotVilocity * gFrameTime
        gPilotList = []
        gPilotListInJSON = {}
        gMsgCtrl = myFunc.MsgCtrl()


        # 建立執行緒並執行
        t = threading.Thread(target=updateAll)
        t.start()

        handlers = [[r'/index', IndexHandler],
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
