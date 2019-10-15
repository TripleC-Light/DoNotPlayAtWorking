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
import objCtrl as objCtrl

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
        global gFrameTime
        global gObjList
        global gPilotListInJSON
        global gMapSize
        global gMsgCtrl

        _getInitPositionFail = [-1, -1]
        _tmp = CMDfromWEB.split('@')
        _cmd = _tmp[0]
        _returnInfo = ''
        if _cmd == 'createPilot':
            _data = _tmp[1]
            _positionMode = _data
            _pilot = Object()
            _pilot.id = myFunc.getUniqueID(list(gObjList.keys()))
            _pilot.name = str(_pilot.id)
            _pilot.SP = 350 * gFrameTime
            _XY = getInitPosition(_positionMode, gMapSize, _pilot)
            if _XY != _getInitPositionFail:
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

        elif _cmd == 'reBorn':
            _id = _tmp[1]
            gObjList[_id].HP = 10

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
            _getInitPositionFail = [-1, -1]
            for _i in range(1):
                enemy = Object()
                enemy.id = myFunc.getUniqueID(list(gObjList.keys()))
                enemy.name = enemy.id
                _XY = getInitPosition('auto', gMapSize, enemy)
                if _XY != _getInitPositionFail:
                    enemy.type = 'enemy'
                    enemy.pic = 'zombie'
                    enemy.SP = 30 * gFrameTime
                    enemy.X = _XY[0]
                    enemy.Y = _XY[1]
                    enemy.tX = _XY[0]
                    enemy.tY = _XY[1]
                    enemy.timeOut = round(time.time(), 3)
                    enemy.W = random.randint(20, 150)
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
                    _reserveList[_mapObj] = gObjList[_mapObj]
            gObjList = _reserveList.copy()

            _data = _tmp[1]
            _mapRegion = _data
            _mapObjInJSON = {}
            _mapObjList = []
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
                        _obj.id = myFunc.getUniqueID(list(gObjList.keys()))
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
            _mapObjInJSON['ObjList'] = _mapObjList
            _objToJSON = json.dumps(_mapObjInJSON)
            _returnInfo = 'setMap@' + _objToJSON

        self.write_message(_returnInfo)

def getInitPosition(positionMode, mapSize, obj):
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
                print('Error: Already try 1000 times to find a position')
                return [-1, -1]
        else:
            _collisionState = (False, 0)
    return _XY

def updateAll():
    global gFrameTime
    global gPilotListInJSON
    global gMsgCtrl
    global gObjList

    _offlineTime = 5    # second
    _timeCtrl = myFunc.TimeCtrl()
    _timeCtrl.attackTime = 0.1   # second

    while 1:
        _timeCtrl.sysTime = time.time()
        # _timeCtrl.showFPS()

        objCtrl.clearBeHITstate(gObjList)

        _pilotList = []
        for _id in list(gObjList.keys()):
            _pilot = gObjList[_id]
            if _pilot.type == 'pilot' or _pilot.type == 'enemy':
                updatePosition(_pilot)
                _timeCtrl.clearAttackTime(_pilot)

                if _pilot.attack != 0:
                    _weapen = Object()
                    _weapen.id = _pilot.id
                    _weapen.W = _pilot.W/2
                    _weapen.H = _pilot.H
                    if _pilot.dir == 'right':
                        _weapen.X = _pilot.X + _pilot.W/2 + _weapen.W/2
                        _weapen.Y = _pilot.Y
                    else:
                        _weapen.X = _pilot.X - _pilot.W/2 - _weapen.W/2
                        _weapen.Y = _pilot.Y
                    _weapenCollision = myFunc.rectCollision(_weapen, gObjList)
                    if _weapenCollision[0]:
                        _pilot.attack = 0
                        for _beHitPilot in gObjList:
                            for _beHitID in _weapenCollision[1]:
                                if gObjList[_beHitPilot].id == _beHitID:
                                    gObjList[_beHitPilot].beHIT = True
                                    _damage = _pilot.AT - gObjList[_beHitPilot].DEF
                                    if _damage > 0:
                                        if gObjList[_beHitPilot].HP > 0:
                                            gObjList[_beHitPilot].HP -= _damage
                                    break

                if (_timeCtrl.sysTime - _pilot.timeOut) > _offlineTime:
                    if _pilot.timeOut == 0:
                        gMsgCtrl.add('系統公告', str(_pilot.name) + ' 離開遊戲')
                        del gObjList[_id]
                        print('delete: ' + str(_id))
                    else:
                        _pilot.timeOut = 0

                if _pilot.HP == -999:
                    if _pilot.type != 'pilot':
                        print('Game Over: ' + str(_pilot.id))
                        del gObjList[_id]
                    else:
                        gMsgCtrl.add('系統公告', str(_pilot.name) + ' HP歸零')
                        _pilot.HP = -1000
                elif _pilot.HP == -1000:
                    _pilot.HP = -1000
                elif _pilot.HP <= 0:
                    _pilot.HP = -999

        if _timeCtrl.oneSecondTimeOut():
            for _pilot in list(gObjList.keys()):

                if gObjList[_pilot].msgTimeCount > 0:
                    gObjList[_pilot].msgTimeCount -= 1
                    if gObjList[_pilot].msgTimeCount == 0:
                        gObjList[_pilot].msg = ''

                if gObjList[_pilot].type == 'enemy':
                    _allDistance = {}
                    for _id in gObjList:
                        if gObjList[_id].type == 'pilot' and gObjList[_id].HP > 0:
                            _allDistance[_id] = int(myFunc.distance([gObjList[_pilot].X, gObjList[_pilot].Y], [gObjList[_id].X, gObjList[_id].Y]))
                    if len(_allDistance) == 0:
                        gObjList[_pilot].tX = random.randint(0, gMapSize[0])
                        gObjList[_pilot].tY = random.randint(0, gMapSize[1])
                    else:
                        _mostCloseID = min(_allDistance, key=_allDistance.get)
                        _targetPilot = gObjList[_mostCloseID]
                        gObjList[_pilot].tX = _targetPilot.X
                        gObjList[_pilot].tY = _targetPilot.Y

                    _weapen = Object()
                    _weapen.id = gObjList[_pilot].id
                    _weapen.W = gObjList[_pilot].W / 2
                    _weapen.H = gObjList[_pilot].H
                    if gObjList[_pilot].dir == 'right':
                        _weapen.X = gObjList[_pilot].X + gObjList[_pilot].W / 2 + _weapen.W / 2
                        _weapen.Y = gObjList[_pilot].Y
                    else:
                        _weapen.X = gObjList[_pilot].X - gObjList[_pilot].W / 2 - _weapen.W / 2
                        _weapen.Y = gObjList[_pilot].Y
                    _weapenCollision = myFunc.rectCollision(_weapen, gObjList)

                    if _weapenCollision[0]:
                        for _beHitPilot in gObjList:
                            for _beHitID in _weapenCollision[1]:
                                if gObjList[_beHitPilot].type == 'pilot' and gObjList[_beHitPilot].id == _beHitID and gObjList[_beHitPilot].HP > 0:
                                    gObjList[_pilot].attack = _timeCtrl.sysTime

        for _id in list(gObjList.keys()):
            _pilot = gObjList[_id]
            if _pilot.type == 'pilot' or _pilot.type == 'enemy':
                if _pilot.type == 'enemy' and _pilot.timeOut != 0:
                    _pilot.timeOut = round(_timeCtrl.sysTime, 3)
                _pilotList.append(_pilot.__dict__)

        gPilotListInJSON['list'] = _pilotList
        time.sleep(gFrameTime)

def updatePosition(pilot):
    global gObjList

    _P1 = [pilot.X, pilot.Y]
    _P2 = [pilot.tX, pilot.tY]
    _dX = _P1[0] - _P2[0]
    _dY = _P1[1] - _P2[1]
    if abs(_dX) < 1 and abs(_dY) < 1:
        return True
    else:
        _step = pilot.SP
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

            pilot.Y = round(pilot.Y - (_dY / _howManyTimesToGo))
            if myFunc.rectCollision(pilot, gObjList)[0]:
                pilot.Y = round(pilot.Y + (_dY / _howManyTimesToGo))
                pilot.tY = pilot.Y
        return False

if __name__ == "__main__":
    global gObjList
    global gPilotListInJSON
    global gFrameTime           # Frame per second
    global gMsgCtrl
    global gMapSize

    try:
        gObjList = {}
        gFrameTime = 0.05
        gPilotListInJSON = {}
        gMsgCtrl = myFunc.MsgCtrl()
        gMapSize = []

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
