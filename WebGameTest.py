# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import webbrowser
import os
import time
import random
import threading
import math
import tornado.websocket
from Object import Object
import json
import myFunction as myFunc

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    global gObjList

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
                _pilot.targetX = _XY[0]
                _pilot.targetY = _XY[1]
                _pilot.connectTimeOut = time.time()
                _pilot.width = random.randint(20, 150)
                _pilot.height = _pilot.width
                gObjList.append(_pilot)
                gMsgCtrl.add('系統公告', '新玩家 ' + _pilot.name + '進入遊戲')
                _pilotInJSON = _pilot.__dict__
                _returnInfo = 'newPilot@' + json.dumps(_pilotInJSON)

        elif _cmd == 'getNewData':
            _data = _tmp[1]
            _id = _data
            for _pilot in gObjList:
                if str(_pilot.id) == _id:
                    _pilot.connectTimeOut = time.time()
                    break
            gPilotListInJSON.update({'serverTime': time.time()})
            _returnInfo = 'NewData@' + json.dumps(gPilotListInJSON)

        elif _cmd == 'move':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _XY = _tmp[1]
            _XY = _XY.split(',')
            for _pilot in gObjList:
                if str(_pilot.id) == _id:
                    _pilot.targetX = int(_XY[0])
                    _pilot.targetY = int(_XY[1])
                    break

        elif _cmd == 'attack':
            _id = _tmp[1]
            for _pilot in gObjList:
                if str(_pilot.id) == _id:
                    _pilot.attack = time.time()
                    break

        elif _cmd == 'createEnemy':
            _setInitPositionFail = [-1, -1]
            for _i in range(3):
                print('createEnemy' + str(_i))
                enemy = Object()
                enemy.id = myFunc.getUniqueID()
                enemy.name = enemy.id
                _XY = setInitPosition('auto', gMapSize, enemy)
                if _XY != _setInitPositionFail:
                    enemy.type = 'enemy'
                    enemy.pic = 'zombie'
                    enemy.speed = 50
                    enemy.X = _XY[0]
                    enemy.Y = _XY[1]
                    # enemy.targetX = _XY[0]
                    # enemy.targetY = _XY[1]
                    enemy.targetX = random.randint(70, 1000)
                    enemy.targetY = random.randint(70, 600)
                    enemy.connectTimeOut = time.time()
                    enemy.width = random.randint(70, 70)
                    enemy.height = enemy.width
                    gObjList.append(enemy)

        elif _cmd == 'sendMsg':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _msg = _tmp[1]
            _msg = gMsgCtrl.filter(_msg)
            for _pilot in gObjList:
                if str(_pilot.id) == _id:
                    _pilot.msgTimeCount = 5
                    _pilot.msg = _msg
                    gMsgCtrl.add(_pilot.name, _msg)
                    break

        elif _cmd == 'getMsg':
            _returnInfo = gMsgCtrl.returnToWeb()

        elif _cmd == 'setMap':
            _reserveList = []
            for _mapObj in gObjList:
                if _mapObj.type != 'mapObj':
                    _reserveList.append(_mapObj)
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
                        _mapObjInJSON.update({'region': line[1]})
                    elif _type == 'size':
                        _description = line[1].split(',')
                        gMapSize = [int(_description[0]), int(_description[1])]
                        _mapObjInJSON.update({'size': gMapSize})
                    elif _type == 'background':
                        _mapObjInJSON.update({'background': './static/map/background/' + line[1]})
                    elif _type == 'mapObj':
                        _obj = Object()
                        _description = line[1].split(',')
                        _pic = _description[0]
                        _X = int(_description[1])
                        _Y = int(_description[2])
                        _obj.type = 'mapObj'
                        _obj.id = _mapObjID
                        _obj.name = str(_obj.id)
                        _obj.X = _X
                        _obj.Y = _Y
                        _obj.targetX = _X
                        _obj.targetY = _Y
                        if _pic == 'bud':
                            _obj.HP = 1000
                            _obj.width = 70
                            _obj.height = 70
                            _obj.pic = './static/map/obj/' + _pic + '.png'
                        gObjList.append(_obj)
                        _mapObjList.append(_obj.__dict__)
                        _mapObjID += 1
            _mapObjInJSON.update({'ObjList': _mapObjList})
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
            _XY[0] = random.randint((obj.width/2), mapSize[0]-(obj.width/2))
            _XY[1] = random.randint((obj.height/2), mapSize[1]-(obj.height/2))
        else:
            _initPoint = positionMode.split(',')
            _XY = [int(_initPoint[0]), int(_initPoint[1])]
        obj.X = _XY[0]
        obj.Y = _XY[1]
        obj.targetX = _XY[0]
        obj.targetY = _XY[1]
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

    _msgUpdateTime = 1  # second
    _attackTime = 0.1   # second
    _offlineTime = 5    # second
    while True:
        _startTime = time.time()
        gTimeCounter += 1
        if (gTimeCounter * gFrameTime) > _msgUpdateTime:
            gTimeCounter = 0
            for _pilot in gObjList:
                if _pilot.type == 'pilot':
                    if _pilot.msgTimeCount > 0:
                        _pilot.msgTimeCount -= 1
                        if _pilot.msgTimeCount == 0:
                            _pilot.msg = ''

                if _pilot.type == 'enemy':
                    _targetPilot = _pilot
                    while _targetPilot.type != 'pilot':
                        _targetPilot = random.choice(gObjList)
                    _pilot.targetX = _targetPilot.X
                    _pilot.targetY = _targetPilot.Y

        for _pilot in gObjList:
            if _pilot.type == 'pilot' or _pilot.type == 'enemy':
                _pilot.HIT = False

        _pilotList = []
        for _pilot in gObjList:
            if _pilot.type == 'pilot' or _pilot.type == 'enemy':
                updatePosition(_pilot)
                if (_pilot.attack != 0) and ((time.time()-_pilot.attack) > _attackTime):
                    _pilot.attack = 0

                if _pilot.attack != 0:
                    _weapen = Object()
                    _weapen.id = _pilot.id
                    _weapen.width = _pilot.width/2
                    _weapen.height = _pilot.height
                    if _pilot.direction == 'right':
                        _weapen.X = _pilot.X + _pilot.width/2 + _weapen.width/2
                        _weapen.Y = _pilot.Y
                    else:
                        _weapen.X = _pilot.X - _pilot.width/2 - _weapen.width/2
                        _weapen.Y = _pilot.Y
                    _weapenCollision = myFunc.rectCollision(_weapen, gObjList)
                    if _weapenCollision[0]:
                        _pilot.attack = 0
                        for _beHitPilot in gObjList:
                            if _beHitPilot.id == _weapenCollision[1]:
                                print('Be HIT: ' + str(_weapenCollision[1]))
                                _beHitPilot.HIT = True
                                _damage = _pilot.ATK - _beHitPilot.DEF
                                if _damage > 0:
                                    _beHitPilot.HP -= _damage
                                    if _beHitPilot.HP <= 0:
                                        _beHitPilot.connectTimeOut = 1
                                break

                if (time.time() - _pilot.connectTimeOut) > _offlineTime:
                    if _pilot.type == 'pilot' or _pilot.type == 'enemy':
                        if _pilot.connectTimeOut == 0:
                            # addNewMsgToBox('系統公告', str(_pilot.name) + ' 離開遊戲')
                            gMsgCtrl.add('系統公告', str(_pilot.name) + ' 離開遊戲')
                            gObjList.remove(_pilot)
                            print('delete: ' + str(_pilot.id))
                        _pilot.connectTimeOut = 0

        for _pilot in gObjList:
            if _pilot.type == 'pilot' or _pilot.type == 'enemy':
                if _pilot.type == 'enemy' and _pilot.connectTimeOut != 0:
                    _pilot.connectTimeOut = time.time()
                _pilotList.append(_pilot.__dict__)

        gPilotListInJSON.update({'list': _pilotList})

        _exeTime = time.time()-_startTime
        # print(round((_exeTime*1000), 2))
        time.sleep(gFrameTime)

def updatePosition(pilot):
    global gFrameTime
    global gPilotStep
    global gObjList

    _P1 = [pilot.X, pilot.Y]
    _P2 = [pilot.targetX, pilot.targetY]
    _dX = _P1[0] - _P2[0]
    _dY = _P1[1] - _P2[1]
    if distance(_P1, _P2) < 1:
        return True
    else:
        gPilotStep = pilot.speed * gFrameTime
        _step = gPilotStep
        _d = round(distance(_P1, _P2))
        _howManyTimesToGo = round(_d / _step)
        if _howManyTimesToGo == 0:
            pilot.X = pilot.targetX
            pilot.Y = pilot.targetY
        else:
            if pilot.targetX > pilot.X:
                pilot.direction = 'right'
            elif pilot.targetX < pilot.X:
                pilot.direction = 'left'
            pilot.X = round(pilot.X - (_dX / _howManyTimesToGo))
            if myFunc.rectCollision(pilot, gObjList)[0]:
                pilot.X = round(pilot.X + (_dX / _howManyTimesToGo))
                pilot.targetX = pilot.X
                pilot.targetY = pilot.Y
            pilot.Y = round(pilot.Y - (_dY / _howManyTimesToGo))
            if myFunc.rectCollision(pilot, gObjList)[0]:
                pilot.Y = round(pilot.Y + (_dY / _howManyTimesToGo))
                pilot.targetX = pilot.X
                pilot.targetY = pilot.Y
        return False

def distance(P1, P2):
    _dX = P1[0] - P2[0]
    _dY = P1[1] - P2[1]
    return math.sqrt((_dX ** 2) + (_dY ** 2))

if __name__ == "__main__":
    global gObjList
    global gPilotList
    global gPilotListInJSON
    global gTimeCounter
    global gFrameTime           # Frame per second
    global gPilotVilocity       # pixel / s
    global gPilotStep           # Pixel per frame
    # global gMsgBox
    global gMsgCtrl

    try:
        gObjList = []
        gTimeCounter = 0
        gFrameTime = 0.05
        gPilotVilocity = 350
        gPilotStep = gPilotVilocity * gFrameTime
        # gMsgBox = []
        gPilotList = []
        gPilotListInJSON = {}
        gMsgCtrl = myFunc.MsgCtrl()

        # 建立一個子執行緒
        t = threading.Thread(target=updateAll)
        # 執行該子執行緒
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

